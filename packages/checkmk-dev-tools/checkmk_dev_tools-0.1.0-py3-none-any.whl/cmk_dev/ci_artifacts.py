#!/usr/bin/env python3

"""Give information about and download named arguments from Nexus
"""

import hashlib
import logging
import sys
import time
from argparse import ArgumentParser
from argparse import Namespace as Args
from collections.abc import Mapping
from configparser import ConfigParser
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from jenkins import Jenkins, JenkinsException


def parse_args() -> Args:
    """Cool git like multi command argument parser"""
    parser = ArgumentParser("Provide CI artifacts locally")
    parser.add_argument(
        "--log-level",
        "-l",
        choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
        type=str.upper,
        default="INFO",
    )

    parser.set_defaults(func=lambda *_: parser.print_usage())
    subparsers = parser.add_subparsers(help="available commands", metavar="CMD")

    parser_info = subparsers.add_parser("info")
    parser_info.set_defaults(func=fn_info)
    parser_info.add_argument("job", type=lambda a: a.strip(" /"))

    parser_fetch = subparsers.add_parser("fetch")
    parser_fetch.set_defaults(func=fn_fetch)
    parser_fetch.add_argument("job", type=str)
    parser_fetch.add_argument("-p", "--params", type=split_params, action="append")
    parser_fetch.add_argument(
        "-t",
        "--time-constraints",
        default="today",
    )
    parser_fetch.add_argument(
        "-o",
        "--out-dir",
        default="out",
        type=Path,
    )

    return parser.parse_args()


def split_params(string: str) -> dict[str, str]:
    """Splits a 'string packed map' like 'foo=23,bar=42 into a dict"""
    return {k: v for p in string.split(",") for k, v in (p.split("="),)}


def logger():
    """Convenience function retrieves 'our' logger"""
    return logging.getLogger("ci-artifacts")


@dataclass
class Build:
    """Models a Jenkins job build"""

    timestamp: datetime
    result: str
    building: str
    artifacts: list[str]
    parameters: str
    in_progress: bool

    def __init__(self, raw_build_info):
        def params_from(build_info):
            """Return job parameters of provided @build_info as dict"""
            for action in build_info["actions"]:
                if action.get("_class") == "hudson.model.ParametersAction":
                    return {p["name"]: p["value"] for p in action["parameters"]}
            return {}

        self.timestamp = datetime.fromtimestamp(raw_build_info["timestamp"] // 1000)
        self.result = raw_build_info["result"]
        self.building = raw_build_info["building"]
        self.artifacts = [a["relativePath"] for a in raw_build_info["artifacts"]]
        self.parameters = params_from(raw_build_info)
        self.url = raw_build_info["url"]
        self.in_progress = raw_build_info["inProgress"]


@dataclass
class Job:
    """Models a Jenkins job"""

    name: str
    fullname: str
    builds: Mapping[int, Build]

    def __init__(self, raw_job_info, raw_build_infos):
        self.name = raw_job_info["name"]
        self.fullname = raw_job_info["fullName"]
        self.builds = {bi["id"]: Build(bi) for bi in raw_build_infos}


@dataclass
class Folder:
    """Models a Jenkins folder"""

    name: str
    fullname: str
    jobs: str

    def __init__(self, raw_job_info):
        self.name = raw_job_info["name"]
        self.fullname = raw_job_info["fullName"]
        self.jobs = [j["name"] for j in raw_job_info["jobs"]]


@contextmanager
def jenkins_client() -> Jenkins:
    """Create a Jenkins client interface using the config file used for JJB"""
    jjb_config = ConfigParser()
    jjb_config.read(Path("~/.config/jenkins_jobs/jenkins_jobs.ini").expanduser())
    jenkins_config = dict(jjb_config["jenkins"])
    client = Jenkins(
        url=jenkins_config["url"],
        username=jenkins_config["user"],
        password=jenkins_config["password"],
        timeout=10,
    )
    whoami = client.get_whoami()
    if not whoami["id"] == jenkins_config["user"]:
        logger().warning("client.get_whoami() does not match jenkins_config['user']")

    yield client


def fn_info(args: Args) -> None:
    """Entry point for information about job artifacts"""
    with jenkins_client() as server:
        class_name = (job_info := server.get_job_info(args.job))["_class"]
        if class_name == "com.cloudbees.hudson.plugins.folder.Folder":
            # print(yaml.dump(job_info))
            print(Folder(job_info))
        elif class_name == "org.jenkinsci.plugins.workflow.job.WorkflowJob":
            build_infos = [server.get_build_info(args.job, b["number"]) for b in job_info["builds"]]
            print(Job(job_info, build_infos))
        else:
            print(f"Don't know class type {class_name}", file=sys.stderr)
            raise SystemExit(-1)


def meets_constraints(build, params, time_constraints):
    """Checks if a set of requirements are met for a given build"""
    if build.parameters != params:
        print(f"don't match: {build.parameters} != {params}")
        return False

    if time_constraints == "today":
        if build.timestamp.date() != datetime.now().date():
            print(f"Time constraints not met: {build.timestamp.date()} != {datetime.now().date()}")
            return False
    else:
        raise RuntimeError(f"Don't understand {time_constraints}")

    return True


def md5from(filepath: Path) -> str | None:
    """Returns an MD5 sum from contents of file provided"""
    with suppress(FileNotFoundError):
        with open(filepath, "rb") as input_file:
            file_hash = hashlib.md5()
            while chunk := input_file.read(1 << 16):
                file_hash.update(chunk)
            return file_hash.hexdigest()
    return None


def download_artifacts(client: Jenkins, build_url: str, out_dir: Path) -> None:
    """Downloads all artifacts listed for given job/build to @out_dir"""
    # pylint: disable=protected-access
    out_dir.mkdir(parents=True, exist_ok=True)

    # https://bugs.launchpad.net/python-jenkins/+bug/1973243
    # https://bugs.launchpad.net/python-jenkins/+bug/2018576
    fingerprints = client._session.get(
        f"{build_url}api/json?tree=fingerprint[fileName,hash]"
    ).json()["fingerprint"]
    if not fingerprints:
        print("No artifacts (yet)")
        return

    for fingerprint in fingerprints:
        fp_filename, fp_hash = fingerprint["fileName"], fingerprint["hash"]
        logger().debug("Handle artifact: %s (md5: %s)", fp_filename, fp_hash)
        artifact_filename = out_dir / fp_filename
        local_hash = md5from(artifact_filename)

        if local_hash == fp_hash:
            logger().debug("File is already available locally: %s (md5: %s)", fp_filename, fp_hash)
            continue

        if local_hash and local_hash != fp_hash:
            logger().warning(
                "File exists locally but hashes differ: %s %s != %s",
                fp_filename,
                local_hash,
                fp_hash,
            )

        with client._session.get(f"{build_url}artifact/{fp_filename}", stream=True) as reply:
            logger().debug("Download: %s", fp_filename)
            reply.raise_for_status()
            with open(artifact_filename, "wb") as out_file:
                for chunk in reply.iter_content(chunk_size=1 << 16):
                    out_file.write(chunk)


def fn_fetch(args: Args) -> None:
    """Entry point for fetching artifacts"""
    params = {k: v for p in (args.params or []) for k, v in p.items()}
    logger().debug("Parsed params: %s", params)
    with jenkins_client() as client:
        if not (job_info := client.get_job_info(args.job))["_class"].endswith("WorkflowJob"):
            logger().error("'%s' is not a WorkflowJob", args.job)
            raise SystemExit(-1)
        job = Job(
            job_info, (client.get_build_info(args.job, b["number"]) for b in job_info["builds"])
        )
        for build_id, build in job.builds.items():
            if meets_constraints(build, params, args.time_constraints):
                print(
                    f"Found matching build: {build_id}"
                    f" {build.timestamp} {build.result} {build.parameters}"
                )
                for key, value in build.__dict__.items():
                    print(f"  {key}: {value}")
                if build.in_progress or build.building:
                    print(f"Waiting for job #{build_id} to finish..")
                    while True:
                        build = Build(client.get_build_info(args.job, build_id))
                        if build.in_progress or build.building:
                            logger().debug(
                                "build.in_progress=%s build.building=%s",
                                build.in_progress,
                                build.building,
                            )
                            time.sleep(2)
                            continue
                        break
                if not build.artifacts:
                    raise RuntimeError("Job has no artifacts!")

                download_artifacts(client, build.url, args.out_dir)
                break
            print("===")


def main() -> None:
    """Entry point for everything else"""
    try:
        args = parse_args()
        logging.basicConfig(
            format="%(levelname)s %(asctime)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=getattr(logging, args.log_level),
        )
        logger().debug("Parsed args: %s", args)
        args.func(args)
    except JenkinsException as exc:
        logger().error("%r", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
