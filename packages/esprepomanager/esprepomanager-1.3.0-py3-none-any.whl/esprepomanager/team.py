from typing import Dict, List, Optional, TYPE_CHECKING
from .repo import Repository
from .utils import save_get

if TYPE_CHECKING:
    from .person import Person


class Team:
    id: 'int | str'
    key: str
    assignment: str
    persons: 'List[Person]'
    repository: Optional[Repository]

    def __init__(
        self, id_: 'int | str', assignment: str, persons: 'Optional[List[Person]]' = None,
        repository: Optional[Repository] = None
    ) -> None:
        self.id = id_
        self.assignment = assignment
        self.key = f"{assignment}-{id_}"
        self.persons = persons or []
        self.repository = repository

    @classmethod
    def from_csv_line(
        cls, headers: Dict[str, int], data: List[str], assignments: List[str], person: 'Person'
    ) -> 'List[Team]':
        ret: 'List[Team]' = []
        for ass in assignments:
            if not save_get(data, headers[f"Team{ass}"]):
                continue
            try:
                team = Team(
                    int(data[headers[f"Team{ass}"]]),
                    ass,
                    [person]
                )
            except ValueError:
                team = Team(
                    data[headers[f"Team{ass}"]],
                    ass,
                    [person]
                )
            if f"WebUrlRepo{ass}" in headers and data[headers[f"WebUrlRepo{ass}"]]:
                server = data[headers[f"WebUrlRepo{ass}"]].split("//", 1)[1].split("/", 1)
                team.repository = Repository(
                    server[0],
                    server[1],
                    int(data[headers[f"Repo{ass}ID"]])
                )
            ret.append(team)
        return ret

    def __repr__(self) -> str:
        return f"Team({self.id}, {self.assignment}, {self.persons!r}, {self.repository!r})"
