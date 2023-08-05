from . import Gitlab, methods
from typing import Any, Optional, Dict, List, Iterable, Tuple
import requests
import logging

log = logging.getLogger(__name__)


class Group:
    gitlab: Gitlab
    id: int

    def __init__(self, gitlab: Gitlab, id_: int) -> None:
        self.gitlab = gitlab
        self.id = id_

    def send_request(
        self, method: methods, url: str, data: Any = None, params_: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        return self.gitlab.send_request(method, f"groups/{self.id}/{url}", data, params_)

    def send_requests(
        self, requests: Iterable[Tuple[methods, str, Any, Optional[Dict[str, str]]]]
    ) -> Iterable[requests.Response]:
        return self.gitlab.send_requests((x[0], f"groups/{self.id}/{x[1]}", x[2], x[3]) for x in requests)

    def get_info(self) -> 'Optional[Dict[str, int | str]]':
        resp = self.send_request("GET", "", params_={"with_projects": "false"})
        if resp.ok:
            return resp.json()
        else:
            log.debug(resp.json())
        return None

    def projects(self) -> List[int]:
        ret: List[int] = []
        resp = self.send_request("GET", "projects", params_={
                                 "per_page": "100", "page": "1"})
        if not resp.ok:
            log.debug(resp.json())
            return []
        ret.extend(x["id"] for x in resp.json())
        total_pages = resp.headers['X-Total-Pages']
        if total_pages:
            for j, resp in enumerate(
                self.send_requests(
                    ("GET", "projects", None, {"per_page": "100", "page": str(i)}) for i in range(2, int(total_pages)+1)
                )
            ):
                print(f"Getting project page {int(j + 2):02d}/" +
                      f"{int(total_pages):02d}", end="\r")
                ret.extend(x["id"] for x in resp.json())
        print()
        return ret
