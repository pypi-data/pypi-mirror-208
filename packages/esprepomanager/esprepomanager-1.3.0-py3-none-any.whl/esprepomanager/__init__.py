"""Custom python module for managing git repos
"""
from typing import Tuple
from concurrent.futures import ThreadPoolExecutor
import os
import sys
import logging
import argparse
import datetime
from functools import cmp_to_key
from .gitlab import access_level
from .config import ConfigRepo, FullConfig, Assignment
from .person import Person
from .repo import Repository
from .team import Team
from .utils import parse_csv, dump_csv, match_strings

__all__ = [
    "ConfigRepo", "FullConfig", "Assignment",
    "Person", "Repository", "Team",
    "parse_csv", "dump_csv"
]

name = "pyrepomanager"
log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="PyRepoManager",
        description="manage git repos"
    )
    parser.add_argument(
        "-a", "--assignments",
        nargs="*",
        metavar="ASSIGNMENTS"
    )
    parser.add_argument(
        "-b", "--branch",
        metavar="BRANCH",
        default="main",
        help="Branch to download from, will default to branch with latest \
            commit if given branch does not exist. [default: %(default)s]"
    )
    parser.add_argument(
        "--config",
        metavar="CONFIG",
        default="configrepo.toml",
        help="path to config file (offline) [default: %(default)s]"
    )
    parser.add_argument(
        "--configbranch",
        metavar="CONFIGBRANCH",
        help="Branch for config repo"
    )
    parser.add_argument(
        "--createrepos",
        action="store_true",
        help="create repositories for given assignment. Check your settings\
            with --dryrun"
    )
    parser.add_argument(
        "--database",
        metavar="DATABASE",
        help="path to database (offline)"
    )
    parser.add_argument(
        "--deadline",
        metavar="DEADLINE",
        help="needs to be in UTC+0 and format 2020-01-20T21:59:59.0000Z",
        type=lambda x: datetime.datetime.fromisoformat(x[:-1])
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Downloads files from repositories in group",
    )
    parser.add_argument(
        "--dryrun",
        action="store_true",
        help="Do nothing, print what would be done.\
            Doesn't work for --download"
    )
    parser.add_argument(
        "--groups", "-g",
        nargs="*",
        metavar="GROUPS",
        help="Download assignments only for groups."
    )
    parser.add_argument(
        "--ignoreotherbranches",
        action="store_true",
        help="download only from given branch and ignore other branches."
    )
    parser.add_argument(
        "--import",
        dest="import_",
        metavar="IMPORT",
        help="import students from given csv into database.\
            Implies --update flag."
    )
    parser.add_argument(
        "--norename",
        action="store_true",
        help="do not append student names to downloaded repositories"
    )
    parser.add_argument(
        "--outdir", "-o",
        metavar="OUTDIR",
        default="output",
        help="[default: %(default)s]"
    )
    cpu_count = os.cpu_count()
    parser.add_argument(
        "--threads", "-t",
        metavar="THREADS",
        default=cpu_count // 2 if cpu_count else 1,
        type=int,
        help="number of threads. [default: %(default)s]"
    )
    parser.add_argument(
        "--tree",
        metavar="TREE",
        help="path to search in git tree. Use if you want just a subfolder\
            e.g. a4"
    )
    parser.add_argument(
        "--timeoutonerror", "-w",
        metavar="TIMEOUTONERROR",
        default=5,
        type=int,
        help="If an error occurs(e.g. too many requests on gitlab) program\
            will wait for x seconds [default: %(default)s]"
    )
    parser.add_argument(
        "--update", "-u",
        action="store_true",
        default="--import" in sys.argv,
        help="updates the database, e.g. if there are missing gitlab IDs\
            for students it checks if they exist now and updates the database."
    )
    parser.add_argument(
        "--fullconfig",
        metavar="FULLCONFIG",
        help="path to fullconfig (offline)"
    )
    parser.add_argument(
        "--specialdeadlines",
        nargs="*",
        metavar="SPECIALDEADLINES",
        help="set deadlines per repository. repositoryID=Deadline example:\
            1900=2022-04-30T21:59:59.0000Z"
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="disable non error output."
    )
    parser.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        help="enable debug output."
    )
    return parser.parse_args()


def startup(args: argparse.Namespace) -> ConfigRepo:
    with open(args.config, "r") as f:
        config = ConfigRepo.from_toml(f.read(), args.timeoutonerror, args.threads)
    if args.configbranch:
        config.branch = args.configbranch
    if args.dryrun:
        config.dryrun = args.dryrun
    config.ensure_fullconfig(args.fullconfig)
    config.ensure_database(args.database)
    config.fullconfig.get_group_info(config)  # type: ignore

    if args.import_ or args.createrepos:
        args.update = True

    for ass in config.fullconfig.assignments.values():  # type: ignore
        log.log(25, f"Getting upstream repository for assignment {ass.name}")
        ass.get_upstream_repo(config)

    return config


def import_(args: argparse.Namespace, config: ConfigRepo) -> None:
    log.info("Running import")
    if config.persons is None:
        config.persons = []

    with open(args.import_, "r") as f:
        lines = f.readlines()
        h = {s: i for i, s in enumerate(lines[0].split(";"))}
        imported_persons = 0
        for li in lines[1:]:
            line = li.split(";")
            person = Person(line[h["Name"]], line[h["MatriculationNr"]], line[h["Email"]], line[h["Groups"]])
            imported_persons += config.add_person(person)

    log.info(f"Imported {imported_persons} persons")


def update_db(config: ConfigRepo) -> None:
    log.info("Running Updating")
    if config.persons is None:
        return

    no_id = [person for person in config.persons if not person.gitlab_id]
    log.log(25, f"Getting GitlabId for {len(no_id)} persons")
    config.git.search_persons(no_id)


def create_repos(args: argparse.Namespace, config: ConfigRepo) -> None:
    @cmp_to_key
    def _comp_ass(ass1: Assignment, ass2: Assignment) -> int:
        if ass1.name == ass2.same_team_as:
            return -1
        if ass1.name == ass1.same_team_as:
            return 1
        return 0

    def _fork_wrapper(team: Team) -> 'Tuple[Team, bool | Tuple[str, int]]':
        name = ass.fill_repo_name(team.persons[0], team)
        web_url = f"{config.gitlab_base_url}{config.fullconfig.group_namespace}/{name}"  # type: ignore
        log.log(25, f"Forking upstream for team {team.id} to {web_url}.git")
        if team.repository:
            pid = team.repository.id
            if config.git.project(pid).get_info():
                if args.dryrun:
                    return team, (web_url, pid)
                log.log(25, f"Repo for team {team.id} allready exists, only adding members")
                return team, config.git.project(pid).add_members(team.persons, access_level["developer"])

        if args.dryrun:
            return team, (web_url, -1)
        return team, config.git.project(ass.upstream_repo_id).fork(
            name, config.fullconfig.group_id, ass.upstream_file_tree, members=team.persons  # type: ignore
        )

    if config.fullconfig is None or config.persons is None or config.teams is None:
        return
    log.info("Starting to create Repos")
    if not args.assignments:
        log.error("No assignments specified!")
        return
    assignments = [ass for ass in (
        config.fullconfig.assignments.get(ass_str)
        for ass_str in args.assignments) if ass
    ]
    assignments.sort(key=_comp_ass)
    for ass in assignments:
        log.info(f"Working on assignment {ass.name}")
        for person in config.persons:
            if person.teams.get(ass.name):
                continue
            team_id = ass.get_team_id(person, config.persons)
            if team_id is None:
                continue
            team = config.teams.get(f"{ass.name}-{team_id}")
            if not team:
                team = Team(team_id, ass.name)
                config.teams[team.key] = team
            if person not in team.persons:
                team.persons.append(person)
                person.teams[ass.name] = team

        t = ThreadPoolExecutor(config.git.max_threads)
        for team, val in t.map(_fork_wrapper,
                               (t for t in config.teams.values() if t.assignment == ass.name and t.persons)):
            if not val:
                log.error(f"Failed to create repo for team {team.id}")
                continue
            if (team.repository and team.repository.id != -1) or isinstance(val, bool):
                continue
            web_url, pid = val
            server = web_url.split("//", 1)[1].split("/", 1)
            team.repository = Repository(server[0], server[1], pid)


def download(args: argparse.Namespace, config: ConfigRepo) -> None:
    def _download_wrapper(team: Team) -> 'Tuple[Team, bool]':
        if not team.repository or not team.persons:
            return team, False

        project = config.git.project(team.repository.id)
        deadline = args.deadline or None
        if args.specialdeadlines:
            for date in args.specialdeadlines:
                if int(date.split("=")[0]) == team.id:
                    try:
                        deadline = datetime.datetime.fromisoformat(date.split("=")[1][:-1])
                        break
                    except Exception:
                        pass
        commit_id = project.get_most_recent_commit(deadline, args.branch, max_tries=1)
        tree = project.tree(path=args.tree or None, recursive=True, ref=commit_id, max_tries=1)
        to_download = [file for file in tree if any(
            match_strings(expr, file) for expr in config.fullconfig.files_to_download)  # type: ignore
        ]
        to_download = [file for file in to_download if not any(
            match_strings(expr, file) for expr in config.fullconfig.exclude_from_download)  # type: ignore
        ]
        log.debug(f"Downloads for team {team.id}: {to_download}")
        if not to_download:
            return team, True
        dirname = f"{args.outdir}/{team.repository.baseurl.split('/')[-1]}"
        if not args.norename:
            dirname += "_" + team.persons[0].name.replace(" ", "_")
        try:
            os.mkdir(dirname)
        except FileExistsError:
            return team, False
        for file in to_download:
            filepath = dirname + "/"
            for dir in file.split("/")[:-1]:
                filepath += dir + "/"
                try:
                    os.mkdir(filepath)
                except FileExistsError:
                    pass
            content = project.get_file_b(file, commit_id)
            if not content:
                continue
            with open(filepath + file.split("/")[-1], "wb") as f:
                f.write(content)
        return team, True

    if config.fullconfig is None or config.teams is None:
        return
    log.info("Starting to download Repos")
    if not args.assignments:
        log.error("No assignments specified!")
        return
    assignments = [ass for ass in (
        config.fullconfig.assignments.get(ass_str)
        for ass_str in args.assignments) if ass
    ]
    for ass in assignments:
        log.info(f"Working on assignment {ass.name}")

        teams = [
            t for t in config.teams.values()
            if t.assignment == ass.name and t.persons and
            (not args.groups or
             any(any(group in pers.groups for group in args.groups) for pers in t.persons))
        ]

        try:
            os.mkdir(args.outdir)
        except FileExistsError:
            pass

        t = ThreadPoolExecutor(config.git.max_threads)
        for i, (team, val) in enumerate(t.map(_download_wrapper, teams)):
            if not val:
                log.error(f"Failed to download repo for team {team.id}")
                continue
            if log.isEnabledFor(25):
                print(f"Downloading {i:03d}/{len(teams):03d}", end="\r")
        print(f"Downloading {len(teams):03d}/{len(teams):03d}")


def cleanup(args: argparse.Namespace, config: ConfigRepo) -> None:
    if args.update:
        if args.database:
            log.debug("Saving database to disk")
            with open(args.database, "w") as f:
                f.write(dump_csv(config))
        else:
            log.debug("Saving database to repo")
            config.git.project(config.config_repo_id).update_file(config.database_path, config.branch, dump_csv(config))


def main():
    logging.addLevelName(25, "PRINT")
    args = parse_args()
    if args.verbose > 1:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose:
        logging.basicConfig(level=logging.INFO, format="")
    elif args.silent:
        logging.basicConfig(level=logging.ERROR, format="")
    else:
        logging.basicConfig(level=25, format="")
    log.debug(repr(args))

    config = startup(args)
    if args.import_:
        import_(args, config)
    if args.update:
        update_db(config)
    if args.createrepos:
        create_repos(args, config)
    if args.download:
        download(args, config)
    cleanup(args, config)


if __name__ == "__main__":
    main()
