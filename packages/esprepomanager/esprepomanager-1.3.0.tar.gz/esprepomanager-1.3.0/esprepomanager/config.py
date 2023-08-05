import re
import sys
import toml
import logging
import unicodedata
from .gitlab import Gitlab
from typing import List, Optional, Dict
from .person import Person
from .team import Team
from .utils import parse_csv

log = logging.getLogger(__name__)


class ConfigRepo:
    fullconfig_path: str
    database_path: str

    apitoken: str
    config_repo_id: int
    branch: str
    gitlab_base_url: str

    git: Gitlab
    dryrun: bool = False

    fullconfig: 'Optional[FullConfig]' = None
    persons: 'Optional[List[Person]]' = None
    teams: 'Optional[Dict[str, Team]]' = None

    def __init__(
        self, fullconfig_path: str, database_path: str, apitoken: str, config_repo_id: int,
        branch: str, gitlab_base_url: str, timeout: int, max_thread: int
    ) -> None:
        self.fullconfig_path = fullconfig_path
        self.database_path = database_path
        self.apitoken = apitoken
        self.config_repo_id = config_repo_id
        self.branch = branch
        self.gitlab_base_url = gitlab_base_url

        self.git = Gitlab(self.apitoken, self.gitlab_base_url,
                          timeout, max_thread)

    @classmethod
    def from_toml(cls, data: str, timeout: int = 5, max_thread: int = 1) -> 'ConfigRepo':
        try:
            decoded = toml.loads(data)
            return ConfigRepo(
                decoded["ConfigRepo"]["ConfigPath"],
                decoded["ConfigRepo"]["DatabasePath"],
                decoded["ConfigRepo"]["APIToken"],
                int(decoded["ConfigRepo"]["ConfigRepoID"]),
                decoded["ConfigRepo"]["Branch"],
                decoded["ConfigRepo"]["GitlabBaseURL"],
                timeout,
                max_thread
            )
        except Exception:
            log.critical("Malformed Config File!")
            sys.exit(1)

    def ensure_fullconfig(self, file_name: Optional[str] = None) -> None:
        if self.fullconfig and file_name is None:
            return
        data: str
        try:
            if not file_name:
                log.info(f"Getting {self.fullconfig_path} from configrepo")
                data = self.git.project(self.config_repo_id).get_file(
                    self.fullconfig_path, self.branch)
            else:
                log.debug(f"Read fullconfig from {file_name}")
                with open(file_name, "r") as f:
                    data = f.read()
            self.fullconfig = FullConfig.from_toml(data)
            log.debug(repr(self.fullconfig))
        except Exception:
            log.critical("Malformed FullConfig File!")
            sys.exit(1)

    def ensure_database(self, file_name: Optional[str] = None) -> None:
        if self.persons:
            if not self.teams:
                self.teams = {}
            return
        try:
            data: str
            if not file_name:
                log.info(f"Getting {self.database_path} from configrepo")
                data = self.git.project(self.config_repo_id).get_file(
                    self.database_path, self.branch)
            else:
                try:
                    log.debug(f"Read database from {file_name}")
                    with open(file_name, "r") as f:
                        data = f.read()
                except FileNotFoundError:
                    data = ""
            lines = data.splitlines()
            if len(lines):
                self.persons, self.teams = parse_csv(
                    lines[0].split(";"), lines[1:])
            else:
                self.persons = []
                self.teams = {}
            log.info(f"Read {len(self.persons)} students from database.")
            log.info(f"Read {len(self.teams)} teams from database.")
        except Exception:
            log.critical("Malformed Database!")
            sys.exit(1)

    def add_person(self, person: 'Person') -> bool:
        if self.persons is None:
            return False
        for p in self.persons:
            if p == person:
                p.combine(person)
                return False
        self.persons.append(person)
        return True

    def __repr__(self) -> str:
        return (f"ConfigRepo({self.fullconfig_path}, {self.database_path}, " +
                f"{self.apitoken}, {self.config_repo_id}, {self.branch}, " +
                f"{self.gitlab_base_url})")


class Assignment:
    find_team_regex: Optional[List[re.Pattern]] = None
    find_group_regex: Optional[List[re.Pattern]] = None

    name: str
    repository_name: str
    upstream_repo_id: int
    upstream_file_tree: Optional[List[str]] = None

    teamsize: int
    same_team_as: str

    def __init__(
        self, name: str, repository_name: str, upstream_repo_id: int, teamsize: int, same_team_as: str,
        find_team_regex: Optional[List[str]] = None, find_group_regex: Optional[List[str]] = None
    ) -> None:
        if find_team_regex:
            self.find_team_regex = [re.compile(x) for x in find_team_regex]
        if find_group_regex:
            self.find_group_regex = [re.compile(x) for x in find_group_regex]

        self.name = name
        self.repository_name = repository_name
        self.upstream_repo_id = upstream_repo_id

        self.teamsize = teamsize
        self.same_team_as = same_team_as

    def get_upstream_repo(self, config: ConfigRepo) -> None:
        if self.upstream_repo_id == -1:
            return
        info = config.git.project(self.upstream_repo_id).get_info()
        if not info or info.get("id") != self.upstream_repo_id:
            return
        self.upstream_file_tree = config.git.project(self.upstream_repo_id).tree(recursive=True)

    def filter_by_group(self, person: 'Person') -> str:
        if self.find_group_regex and len(self.find_group_regex):
            group = person.groups
            for reg in self.find_group_regex:
                res = reg.search(group)
                if not res:
                    return ""
                group = res.string[res.start():res.end()]
            return group
        return person.groups

    def get_team_id(self, person: 'Person', all_persons: 'List[Person]') -> 'Optional[int | str]':
        if person.teams.get(self.name):
            return person.teams[self.name].id

        if not self.filter_by_group(person):
            return None

        if self.find_team_regex and len(self.find_team_regex):
            group = person.groups
            for reg in self.find_team_regex:
                res = reg.search(group)
                if not res:
                    return None
                group = res.string[res.start():res.end()]
            try:
                return int(group)
            except ValueError:
                return group

        if self.same_team_as:
            if person.teams.get(self.same_team_as):
                return person.teams[self.same_team_as].id

        max_num = 1
        for pers in all_persons:
            if pers.teams.get(self.name):
                team = pers.teams[self.name]
                if len(team.persons) < self.teamsize:
                    return team.id
                try:
                    max_num = max(max_num, int(team.id) + 1)
                except ValueError:
                    max_num = max_num
        return max_num

    def fill_repo_name(self, person: 'Optional[Person]' = None, team: 'Optional[Team]' = None) -> str:
        return unicodedata.normalize('NFKD', self.repository_name.replace(
            "<Name>", person.name if person else ""
        ).replace(
            "<Team>", (f"{team.id:03d}" if isinstance(team.id, int) else team.id) if team else ""
        ).replace(
            "<Group>", self.filter_by_group(person) if person else ""
        ).replace(
            "<MatriculationNr>", person.mat_nr if person else ""
        ).replace(
            "<Email>", person.email if person else ""
        ).replace(
            "<GitlabID>", person.gitlab_id if person else ""
        ).replace(
            "<GitlabUsername>", person.gitlab_username if person else ""
        ).replace(
            "<Assignment>", self.name
        )).encode('ascii', 'ignore').decode("ascii")

    def __repr__(self) -> str:
        return (
            f"Assignment({self.name}, {self.repository_name}, {self.upstream_repo_id}, " +
            f"{self.teamsize}, {self.same_team_as}, {self.find_team_regex}, " +
            f"{self.find_group_regex})"
        )


class FullConfig:
    apitoken: str
    baseurl: str
    group_id: int
    group_name: str
    files_to_download: List[str]
    exclude_from_download: List[str]

    assignments: Dict[str, Assignment]
    group_namespace: Optional[str] = None

    def __init__(
        self, apitoken: str, baseurl: str, group_id: int, group_name: str, files_to_download: Optional[List[str]],
        exclude_from_download: Optional[List[str]]
    ) -> None:
        self.assignments = {}
        self.apitoken = apitoken
        self.baseurl = baseurl
        self.group_id = group_id
        self.group_name = group_name
        self.files_to_download = files_to_download or ["*"]
        self.exclude_from_download = exclude_from_download or []

    def get_group_info(self, config: ConfigRepo) -> None:
        if self.group_id == -1:
            return
        info = config.git.group(self.group_id).get_info()
        if not info or info.get("id") != self.group_id:
            return
        self.group_namespace = str(info.get("full_path"))

    @classmethod
    def from_toml(cls, data: str) -> 'FullConfig':
        decoded = toml.loads(data)
        config = FullConfig(
            decoded["Gitlab"]["APIToken"],
            decoded["Gitlab"]["BaseURL"],
            int(decoded["Gitlab"]["GroupID"]),
            decoded["Gitlab"]["GroupName"],
            decoded["Gitlab"].get("FilesToDownload"),
            decoded["Gitlab"].get("ExcludeFilesFromDownload"),
        )

        for ass, c in decoded.get("Assignments", {}).items():
            config.assignments[ass] = Assignment(
                ass,
                c["RepositoryName"],
                int(c["UpstreamRepositoryID"]),
                int(c["Team"]["TeamSize"]),
                c["Team"]["SameTeamAs"],
                c.get("FindTeamRegex"),
                c.get("FindGroupRegex"),
            )

        return config

    def __repr__(self) -> str:
        return (f"FullConfig({self.apitoken}, {self.baseurl}, " +
                f"{self.group_id}, {self.group_name}, " +
                f"{self.files_to_download}, {self.exclude_from_download}, " +
                f"{self.assignments!r})"
                )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} [CONFIG_FILE]")
        sys.exit(1)
    with open(sys.argv[1], "r") as f:
        config = ConfigRepo.from_toml(f.read())
    config.ensure_fullconfig()
    print(config)
    print(config.fullconfig)
