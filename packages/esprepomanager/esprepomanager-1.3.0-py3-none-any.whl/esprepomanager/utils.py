
from typing import Iterable, Tuple, Sequence, List, Dict, TypeVar, Optional, TYPE_CHECKING, overload
from .person import Person

if TYPE_CHECKING:
    from .team import Team
    from .config import ConfigRepo


PERSON_HEADERS = ["Name", "MatriculationNr", "Email", "Groups"]
REPO_HEADERS = ["Team{}", "WebUrlRepo{}", "HttpRepo{}", "SshRepo{}", "Repo{}ID"]
GITLAB_HEADERS = ["GitlabID", "GitlabUsername"]

T1 = TypeVar('T1')
T2 = TypeVar('T2')


@overload
def save_get(from_: Sequence[T1], index: int) -> Optional[T1]: ...
@overload
def save_get(from_: Sequence[T1], index: int, default: T2) -> 'T1 | T2': ...


def save_get(from_, index, default=None):
    if index >= len(from_):
        return default
    return from_[index]


def match_strings(expr: str, string: str) -> bool:
    if expr.startswith("*") and expr.endswith("*"):
        return expr[1:-1] in string
    if expr.startswith("*"):
        return string.endswith(expr[1:])
    if expr.endswith("*"):
        return string.startswith(expr[:-1])
    return expr == string


def parse_csv(headers: Iterable[str], data: Iterable[str]) -> 'Tuple[List[Person], Dict[str, Team]]':
    from .team import Team
    h_dic: Dict[str, int] = {s: i for i, s in enumerate(headers)}
    assignments: List[str] = []
    for header in headers:
        if header.startswith("Team"):
            assignments.append(header[4:])
    persons: List[Person] = []
    teams: 'Dict[str, Team]' = {}

    for line in data:
        lines = line.split(";")
        person_ = Person(
            save_get(lines, h_dic["Name"], ""),
            save_get(lines, h_dic["MatriculationNr"], ""),
            save_get(lines, h_dic["Email"], ""),
            save_get(lines, h_dic["Groups"], ""),
            save_get(lines, h_dic["GitlabID"], ""),
            save_get(lines, h_dic["GitlabUsername"], ""),
        )
        persons.append(person_)
        teams_ = Team.from_csv_line(h_dic, lines, assignments, person_)
        for team in teams_:
            if team.key is None:
                continue
            if team.key not in teams:
                teams[team.key] = team
            else:
                repo = teams[team.key].repository
                if (repo and repo.id == -1 and team.repository):
                    repo.id = team.repository.id
                teams[team.key].persons.append(person_)
            person_.teams[team.assignment] = teams[team.key]

    return (persons, teams)


def dump_csv(config: 'ConfigRepo') -> str:
    assignments_names = []
    if config.fullconfig:
        assignments_names.extend(sorted(list(config.fullconfig.assignments.keys())))
    headers = [*PERSON_HEADERS]
    for header in REPO_HEADERS:
        headers.extend(header.format(a) for a in assignments_names)
    headers.extend(GITLAB_HEADERS)
    ret = [";".join(headers)]

    if config.persons:
        for person in config.persons:
            line: List[str] = [person.name, person.mat_nr, person.email, person.groups]
            person_ass: List[List[str]] = []
            for team in (person.teams.get(ass) for ass in assignments_names):
                team_strings: List[str] = []
                if not team:
                    team_strings.append("")
                    repo = None
                else:
                    team_strings.append(f"{team.id:03d}" if isinstance(team.id, int) else team.id)
                    repo = team.repository
                if not repo:
                    team_strings.extend("" for _ in REPO_HEADERS[1:])
                else:
                    team_strings.append(repo.weburl)
                    team_strings.append(repo.httprepo)
                    team_strings.append(repo.sshrepo)
                    team_strings.append(str(repo.id))
                person_ass.append(team_strings)
            for i in range(len(REPO_HEADERS)):
                for j in range(len(person_ass)):
                    line.append(person_ass[j][i])
            line.append(person.gitlab_id)
            line.append(person.gitlab_username)
            ret.append(";".join(line))

    return "\n".join(ret) + "\n"
