class Repository:
    gitlab_server: str
    baseurl: str
    id: int

    def __init__(self, gitlab_server: str, baseurl: str, id_: int) -> None:
        self.gitlab_server = gitlab_server
        self.baseurl = baseurl
        self.id = id_

    @property
    def weburl(self) -> str:
        return f"https://{self.gitlab_server}/{self.baseurl}"

    @property
    def httprepo(self) -> str:
        return f"https://{self.gitlab_server}/{self.baseurl}.git"

    @property
    def sshrepo(self) -> str:
        return f"git@{self.gitlab_server}:{self.baseurl}.git"

    def __repr__(self) -> str:
        return f"Repository({self.gitlab_server}, {self.baseurl}, {self.id})"
