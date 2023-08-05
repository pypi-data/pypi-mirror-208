from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .team import Team


class Person:
    name: str
    mat_nr: str
    email: str
    groups: str
    gitlab_id: str
    gitlab_username: str

    teams: 'Dict[str, Team]'

    def __init__(
        self, name: str, mat_nr: str,
        email: Optional[str] = None, groups: 'Optional[str]' = None,
        gitlab_id: Optional[str] = None, gitlab_username: Optional[str] = None
    ) -> None:
        self.teams = {}
        self.name = name
        self.mat_nr = mat_nr
        self.email = email or ""
        self.groups = groups or ""
        self.gitlab_id = gitlab_id or ""
        self.gitlab_username = gitlab_username or ""

    def combine(self, ext: 'Person') -> bool:
        if self != ext:
            return False
        self.email = ext.email if ext.email else self.email
        self.groups = ext.groups if ext.groups else self.groups
        self.gitlab_id = ext.gitlab_id if ext.gitlab_id else self.gitlab_id
        self.gitlab_username = ext.gitlab_username if ext.gitlab_username else self.gitlab_username
        return True

    @property
    def reverseName(self) -> str:
        name = self.name.split(" ")
        name[-1] = name[-1] + ","
        name[0], name[-1] = name[-1], name[0]
        return " ".join(name)

    def checkGitLabName(self, name: str) -> bool:
        return f"{name[name.find(',')+1:]} {name[:name.find(',')]}".strip() == self.name

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, self.__class__):
            raise NotImplementedError
        return self.name == __value.name and self.mat_nr == __value.mat_nr

    def __repr__(self) -> str:
        return (f"Person({self.name}, {self.mat_nr}, {self.email}, " +
                f"{self.groups}, {self.gitlab_id}, {self.gitlab_username})")
