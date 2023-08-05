import datetime
import time
from . import Gitlab, methods, visibility, access_level
from urllib import parse
from typing import Any, Literal, Optional, Dict, List, TYPE_CHECKING, Tuple
import requests
import base64
import logging
from .user import User

if TYPE_CHECKING:
    from esprepomanager.person import Person

log = logging.getLogger(__name__)


class Project:
    gitlab: Gitlab
    id: int

    def __init__(self, gitlab: Gitlab, id_: int) -> None:
        self.gitlab = gitlab
        self.id = id_

    def send_request(
        self, method: methods, url: str, data: Any = None, params_: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        return self.gitlab.send_request(
            method, f"projects/{self.id}/{url}", data, params_)

    def get_info(self) -> Optional[Dict[str, Any]]:
        resp = self.send_request("GET", "")
        if resp.ok:
            return resp.json()
        else:
            log.debug(resp.json())
        return None

    def delete(self, max_tries: int = 3) -> bool:
        for _ in range(max_tries):
            resp = self.send_request("DELETE", "")
            if resp.ok:
                return True
            else:
                log.debug(resp.json())
        return False

    def get_file(self, path: str, ref: str) -> str:
        resp = self.send_request("GET", "repository/files/" + parse.quote(path, ""), params_={"ref": ref})
        if not resp.ok:
            log.debug(resp.json())
            return ""
        return base64.b64decode(resp.json()["content"]).decode("utf-8")

    def get_file_b(self, path: str, ref: str) -> bytes:
        resp = self.send_request("GET", "repository/files/" + parse.quote(path, ""), params_={"ref": ref})
        if not resp.ok:
            log.debug(resp.json())
            return b""
        return base64.b64decode(resp.json()["content"])

    def update_file(self, path: str, branch: str, content: str) -> bool:
        resp = self.send_request("PUT", "repository/files/" + parse.quote(path, ""), {
            "branch": branch,
            "commit_message": f"Updated {path}",
            "content": content,
            "encoding": "text"
        })
        if not resp.ok:
            log.debug(resp.json())
            return False
        return True

    def tree(
        self, path: Optional[str] = None, recursive: bool = False,
        ref: Optional[str] = None, max_tries: int = 3
    ) -> List[str]:
        params = {
            "recursive": "true" if recursive else "false",
            "pagination": "keyset",
            "per_page": "100",
            "order_by": "path",
            "sort": "asc"
        }
        if path:
            params["path"] = path
        if ref:
            params["ref"] = ref

        link: Optional[str] = None
        ret_list: List[str] = []
        next_page: bool = True
        while next_page:
            for _ in range(max_tries):
                if link:
                    resp = requests.get(link)
                else:
                    resp = self.send_request("GET", "repository/tree", params_=params)
                j_resp = resp.json()
                if resp.ok:
                    ret_list.extend(x["path"] for x in j_resp)
                    if resp.links.get("next"):
                        link = resp.links.get("next")["url"]  # type: ignore
                    else:
                        next_page = False
                    break
                else:
                    log.debug(j_resp)
                    time.sleep(1)

        return ret_list

    def members(self) -> List[User]:
        resp = self.send_request("GET", "members", params_={"per_page": "100"})
        if not resp.ok:
            log.debug(resp.json())
            return []
        return [User.from_json(x) for x in resp.json()]

    def set_protected_branch(self, branch: str, access: int, allow_force: bool = False) -> bool:
        resp = self.send_request("POST", "protected_branches", params_={
            "name": branch,
            "allow_force_push": "true" if allow_force else "false",
            "push_access_level": str(access),
            "merge_access_level": str(access)
        })
        if not resp.ok:
            log.debug(resp.json())
        return resp.ok

    def unprotect_branch(self, branch: str) -> bool:
        resp = self.send_request("DELETE", f"protected_branches/{branch}")
        if not resp.ok:
            log.debug(resp.json())
        return resp.ok

    def fork(
        self, name: str, namespace_id: int, tree: Optional[List[str]],
        visibility_: visibility = "private", members: 'Optional[List[Person]]' = None,
        max_tries: int = 3
    ) -> 'Literal[False] | Tuple[str, int]':
        if self.id == -1:
            return self.create(name, namespace_id, members, max_tries)

        for _ in range(max_tries):
            resp = self.send_request(
                "POST", "fork", params_={
                    "name": name, "path": name, "namespace_id": str(namespace_id), "visibility": visibility_
                }
            )
            j_resp = resp.json()
            log.debug(j_resp)
            is_ok = resp.ok
            if j_resp.get('message', {}).get('path', {}) == ['has already been taken']:
                rresp = self.gitlab.search(name, "projects")
                for proj in rresp:
                    if proj["name"] == name:
                        j_resp["id"] = proj["id"]
                        j_resp["web_url"] = proj["web_url"]
                        is_ok = True
                        break
            if is_ok:
                pid = int(j_resp["id"])
                web_url = j_resp["web_url"]
                time.sleep(1)
                if not tree or self.gitlab.project(pid).tree(recursive=True) == tree:
                    break
                self.gitlab.project(pid).delete(max_tries)
            time.sleep(1)
        else:
            return False

        self.gitlab.project(pid).unprotect_branch("main")
        self.gitlab.project(pid).set_protected_branch("main", access_level["developer"], False)

        if members:
            ret = self.gitlab.project(pid).add_members(members, access_level["developer"], max_tries)
            return (web_url, pid) if ret else False
        return (web_url, pid)

    def add_members(self, persons: 'List[Person]', access_level_: int, max_tries: int = 3) -> bool:
        ids = ",".join(x.gitlab_id for x in persons if x.gitlab_id)
        if not len(ids):
            return True

        for _ in range(max_tries):
            resp = self.send_request(
                "POST", "members", params_={"user_id": ids, "access_level": str(access_level_)}
            )

            j_resp = resp.json()
            if resp.ok or j_resp.get('message') == 'Member already exists':
                return True
            log.debug(j_resp)
            time.sleep(1)
        return False

    def create(
        self, name: str, namespace_id: int, members: 'Optional[List[Person]]' = None,
        max_tries: int = 3
    ) -> 'Literal[False] | Tuple[str, int]':
        for _ in range(max_tries):
            resp = self.gitlab.send_request(
                "POST", "projects", params_={"name": name, "namespace_id": str(namespace_id)}
            )

            if resp.ok:
                break
            log.debug(resp.json())
            time.sleep(1)
        else:
            return False

        j_resp = resp.json()
        pid = int(j_resp["id"])
        web_url = j_resp["web_url"]

        if members:
            ret = self.gitlab.project(pid).add_members(members, access_level["developer"], max_tries)
            return (web_url, pid) if ret else ret

        return (web_url, pid)

    def get_most_recent_commit(
        self, date: Optional[datetime.datetime] = None, ref: Optional[str] = None, max_tries: int = 3
    ) -> str:
        params = {}
        if date:
            params["until"] = date.isoformat()+"Z"
        if ref:
            params["ref_name"] = ref
        for _ in range(max_tries):
            resp = self.send_request("GET", "repository/commits", params_=params)

            if resp.ok:
                break
            log.debug(resp.json())
            time.sleep(1)
        else:
            return ""

        j_resp = resp.json()
        if not j_resp:
            return ""
        return j_resp[0].get("id", "")
