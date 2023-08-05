from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Any, List, Dict, Literal, Iterable, Tuple, TYPE_CHECKING
import requests
import time

if TYPE_CHECKING:
    from .project import Project
    from .group import Group
    from .user import User
    from esprepomanager.person import Person

methods = Literal["GET", "PUT", "POST", "PATCH", "DELETE"]
visibility = Literal["private", "internal", "public"]
access_levels = Literal["no_access", "minimal", "guest",
                        "reporter", "developer", "maintainer", "owner"]
access_level: Dict[access_levels, int] = {
    "no_access": 0, "minimal": 5, "guest": 10,
    "reporter": 20, "developer": 30, "maintainer": 40, "owner": 50
}


class Gitlab:
    api_token: str
    base_url: str
    timeout: int
    max_threads: int
    api_version: str = "v4"

    is_timeout: bool = False

    def __init__(self, api_token: str, base_url: Optional[str] = None, timeout: int = 5, max_threads: int = 1) -> None:
        self.api_token = api_token
        self.base_url = base_url or "https://gitlab.com"
        self.timeout = timeout
        self.max_threads = max_threads

    def project(self, id_: int) -> 'Project':
        from .project import Project
        return Project(self, id_)

    def group(self, id_: int) -> 'Group':
        from .group import Group
        return Group(self, id_)

    def send_request(
        self, method: methods, url: str, data: Any = None, params_: Optional[Dict[str, str]] = None, max_tries: int = 5
    ) -> requests.Response:
        try:
            if self.is_timeout:
                time.sleep(5)
            params = params_.copy() if params_ else {}
            params["access_token"] = self.api_token
            ret: requests.Response
            if method == "GET":
                ret = requests.get(
                    f"{self.base_url}/api/{self.api_version}/{url}",
                    params=params
                )
            elif method == "PUT":
                ret = requests.put(
                    f"{self.base_url}/api/{self.api_version}/{url}",
                    json=data, params=params
                )
            elif method == "POST":
                ret = requests.post(
                    f"{self.base_url}/api/{self.api_version}/{url}",
                    json=data,
                    params=params
                )
            elif method == "PATCH":
                ret = requests.patch(
                    f"{self.base_url}/api/{self.api_version}/{url}",
                    json=data,
                    params=params
                )
            elif method == "DELETE":
                ret = requests.delete(
                    f"{self.base_url}/api/{self.api_version}/{url}",
                    params=params
                )
            else:
                raise NotImplementedError
            if ret.status_code == 429:
                # print("\nTimeout!")
                self.is_timeout = True
                time.sleep(self.timeout)
                return self.send_request(method, url, data, params_)
            self.is_timeout = False
            return ret
        except requests.exceptions.RequestException as ex:
            if max_tries == 1:
                raise ex
            time.sleep(5)
            return self.send_request(method, url, data, params_, max_tries - 1)

    def send_requests(
        self, requests_: Iterable[Tuple[methods, str, Any, Optional[Dict[str, str]]]]
    ) -> Iterable[requests.Response]:
        def _send_wrapper(args: Tuple[methods, str, Any, Optional[Dict[str, str]]]) -> requests.Response:
            return self.send_request(*args)

        executor = ThreadPoolExecutor(max_workers=self.max_threads)
        return executor.map(_send_wrapper, requests_)

    def project_members(self, projects: List[int]) -> 'Dict[int, List[User]]':
        def _send_wrapper(project: int) -> 'Tuple[int, List[User]]':
            return project, self.project(project).members()

        ret: 'Dict[int, List[User]]' = {}
        executor = ThreadPoolExecutor(max_workers=self.max_threads)

        for i, users in enumerate(executor.map(_send_wrapper, projects)):
            print(f"Getting project members {(i+1):04d}/{len(projects):04d}", end="\r")
            ret[users[0]] = users[1]
        print()
        return ret

    def search(self, search: str, scope: Literal["projects", "users"]) -> 'List[Dict[str, str | int]]':
        if scope == "projects":
            resp = self.send_request("GET", "projects", params_={"search": search, "order_by": "name", "sort": "asc"})
        else:
            resp = self.send_request("GET", "search", params_={"scope": scope, "search": search})
        return resp.json()

    def search_persons(self, users: 'List[Person]') -> None:
        def _send_wrapper(user: 'Person') -> 'Optional[Tuple[Person, List[Dict[str, str | int]]]]':
            resp = self.search(user.reverseName, "users")
            resp = [r for r in resp if user.checkGitLabName(str(r.get("name", "")))]
            if len(resp) > 1:
                return user, resp
            if len(resp) == 0:
                resp = self.search(user.name, "users")
                resp = [r for r in resp if user.checkGitLabName(str(r.get("name", "")))]
            if len(resp) > 1:
                return user, resp
            if len(resp) == 0:
                return None
            if user.checkGitLabName(str(resp[0].get("name", ""))):
                user.gitlab_id = str(resp[0].get("id", ""))
                user.gitlab_username = str(resp[0].get("username", ""))
            return None

        executor = ThreadPoolExecutor(max_workers=self.max_threads)
        ret: 'List[Tuple[Person, List[Dict[str, str | int]]]]' = []

        for i, rets in enumerate(executor.map(_send_wrapper, users)):
            if rets:
                ret.append(rets)
            print(f"Getting gitlab id {(i+1):04d}/{len(users):04d}", end="\r")
        print()

        for user, search in ret:
            print(f"\nSearch for Person({user.name}) returned multiple options:")
            print("  0: None")
            for i, ser in enumerate(search):
                print(f"  {i + 1}: id: {ser['id']}, name: {ser['name']}, username: {ser['username']}")
            choice = input("--> ")
            try:
                c = int(choice)
                if 0 <= c - 1 < len(search):
                    user.gitlab_id = str(search[c - 1].get("id", ""))
                    user.gitlab_username = str(search[c - 1].get("username", ""))
            except ValueError:
                continue


__all__ = ["Gitlab"]
