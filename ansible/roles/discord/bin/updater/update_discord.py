import sys
import re
import logging
import argparse
from subprocess import Popen, PIPE, DEVNULL
from typing import List
from uuid import uuid1
from os import remove
from pathlib import Path
import requests

DISCORD_LINUX_DOWNLOAD = "https://discord.com/api/download?platform=linux"
DISCORD_PKG_NAME = "discord"
DISCORD_DEPENDENCIES = [
    "libasound2",
    "libatomic1",
    "libnotify4",
    "libnspr4",
    "libnss3",
    "libxss1",
    "libxtst6",
]
REQUEST_TIMEOUT = 30


def main():
    args = parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG

    dpkg_log = DEVNULL
    if args.dpkg_verbose:
        dpkg_log = PIPE

    logging.basicConfig(level=log_level, format="%(levelname)s - %(message)s")

    installed_version = get_installed_version_num(DISCORD_PKG_NAME, log_level=dpkg_log)

    if installed_version == "0.0.0":
        # 0.0.0 is a known constant that we control; if it's returned we know
        # the package is not installed so there's no point in comparing against
        # remote versions.
        #
        logging.info("%s is not installed!", DISCORD_PKG_NAME)
    else:
        logging.info("Installed version: %s", installed_version)
        remote_version = get_latest_version_num()
        logging.info("Upstream version: %s", remote_version)

        if is_remote_version_newer(installed_version, remote_version):
            logging.info("The installed version is not the most recent!")
        else:
            logging.info("Installed version is up to date!")
            sys.exit(0)

    logging.info("Checking that %s dependencies are installed...", DISCORD_PKG_NAME)
    if not are_dependencies_installed(DISCORD_DEPENDENCIES, log_level=dpkg_log):
        logging.fatal(
            "%s dependencies are missing! Please install: %s",
            DISCORD_PKG_NAME,
            DISCORD_DEPENDENCIES,
        )
        sys.exit(1)
    logging.info("Dependencies are installed!")

    logging.info("Beginning installation process...")

    f_path = f"/tmp/discord-{uuid1()}"
    download_latest(f_path)
    install_package(f_path, dry_run=args.dry_run, log_level=dpkg_log)

    remove(f_path)
    sys.exit(0)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="tandem",
        description="A Discord upgrade client for Linux.",
        epilog="Authored by <culver.darian@gmail.com>, licensed under GPL v3.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enables verbose logging."
    )
    parser.add_argument(
        "--dpkg-verbose", action="store_true", help="Enables dpkg verbose logging."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Toggle whether Discord will be updated."
    )

    return parser.parse_args()


def get_latest_version_num():
    # By preventing redirection, we can determine the latest version from the
    # redirect URL, without needing to download the package.
    #
    request_args = {
        "url": DISCORD_LINUX_DOWNLOAD,
        "allow_redirects": False,
        "timeout": REQUEST_TIMEOUT,
    }

    # Parse the redirection notice to get the upstream version num.
    #
    search_term = r'.+<a\shref=".+\/([.\d]+)\/.+".+'

    version_string = ""

    try:
        with requests.get(**request_args) as response:
            response.raise_for_status()
            version_string = response.text
    except requests.ConnectionError:
        # It would be overkill to implement retry logic for this.
        #
        logging.fatal(
            "Could not establish a connection to %s - try again later.",
            DISCORD_LINUX_DOWNLOAD,
        )
        sys.exit(1)

    except requests.HTTPError as e:
        logging.fatal(
            "An HTTPError occurred while checking for install candidates: %s", e
        )
        sys.exit(1)

    if version_string == "":
        logging.fatal("Response could not be processed correctly!")
        sys.exit(1)

    latest_version = re.search(search_term, version_string)
    return latest_version.groups()[0]


def get_installed_version_num(package_name: str, log_level: int):
    """
    Function uses dpkg to determine if Discord is already installed.

    In the event that Discord *has not* been installed, we'll return a 0.0.0
    version number, which will enable installation.
    """
    version_string = ""
    version_metadata_key = "Version:"

    with Popen(
        ["dpkg", "--status", package_name],
        stdout=PIPE,
        stderr=log_level,
        encoding="UTF-8",
    ) as status:
        response = status.stdout.read().split()

        if not response:
            return "0.0.0"

        if version_metadata_key not in response:
            logging.fatal("DPKG response does not container version metadata!")
            sys.exit(1)

        version_index = response.index(version_metadata_key) + 1
        version_string = response[version_index]

    return version_string


def is_remote_version_newer(local: str, remote: str) -> bool:
    # Naive validation, checks that period is used for delimiting.
    #
    invalid_data_format = "The version strings are not correctly formatted!"

    if any("." not in ver_str for ver_str in [local, remote]):
        logging.fatal(invalid_data_format)
        sys.exit(1)

    # We'll split the strings to make comparisons easier.
    #
    a = local.split(".")
    b = remote.split(".")

    if any(len(ver_str) != 3 for ver_str in [a, b]):
        logging.fatal(invalid_data_format)
        sys.exit(1)

    if a == b:
        # If local is the same as remote, than we don't need to update.
        #
        return False

    return any(int(b[sub_ver]) > int(a[sub_ver]) for sub_ver in [0, 1, 2])


def are_dependencies_installed(packages: List[str], log_level: int):
    return any(
        pkg_ver == "0.0.0"
        for pkg_ver in [
            get_installed_version_num(package, log_level) for package in packages
        ]
    )


def download_latest(f_path: str):
    # Partially nabbed from:
    #   https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
    #

    request_args = {
        "url": DISCORD_LINUX_DOWNLOAD,
        "timeout": REQUEST_TIMEOUT,
        "stream": True,
    }
    c_size = 4096

    logging.debug("Will write install file to %s", f_path)

    try:
        with requests.get(**request_args) as req:
            req.raise_for_status()
            with open(f_path, "wb") as f:
                for chunk in req.iter_content(chunk_size=c_size):
                    f.write(chunk)
    except requests.ConnectionError:
        # It would be overkill to implement retry logic for this.
        #
        logging.fatal(
            "Could not establish a connection to %s - try again later.",
            DISCORD_LINUX_DOWNLOAD,
        )
        sys.exit(1)

    except requests.HTTPError as e:
        logging.fatal("An HTTPError occurred during installation: %s", e)
        sys.exit(1)

    # A sanity check that things have gone to plan.
    #
    _is_file_present(f_path)

    logging.info("Installation package downloaded.")
    return f_path


def install_package(f_path: str, dry_run: bool, log_level: int):
    _is_file_present(f_path)

    if dry_run:
        logging.info("Dry run was requested; will not attempt Discord upgrade.")
        return

    with Popen(
        ["sudo", "dpkg", "-i", f_path], stdout=PIPE, stderr=log_level, encoding="UTF-8"
    ) as dpkg:
        logging.debug(dpkg.stdout.read())

    logging.info("Discord has been updated.")


def _is_file_present(f_path: str):
    install_path = Path(f_path)

    if not install_path.is_file():
        logging.fatal("The Discord download at %s could not be found!", f_path)
        sys.exit(1)

    logging.debug("Discord download at %s was verified.", f_path)


if __name__ == "__main__":
    main()
