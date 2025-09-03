import sys
import re
import logging
import argparse
from subprocess import Popen, PIPE
from uuid import uuid1
from os import remove
from pathlib import Path
import requests

DISCORD_LINUX_DOWNLOAD = "https://discord.com/api/download?platform=linux"
DISCORD_PKG_NAME = "discord"
REQUEST_TIMEOUT = 30


def main():
    args = parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level, format="%(levelname)s - %(message)s")

    latest_version = get_latest_version_num()
    logging.info("Upstream version: %s", latest_version)

    installed_version = get_installed_version_num()
    logging.info("Installed version: %s", installed_version)

    if is_version_newer(installed_version, latest_version):
        logging.info("Installed version is up to date!")
        sys.exit(0)
    else:
        logging.info("The installed version is not the most recent!")

    f_path = f"/tmp/discord-{uuid1()}"
    download_latest(f_path)
    install_package(f_path, dry_run=args.dry_run)

    delete_install_file(f_path)
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

    # FIXME - this should have try/catch for http 40X, etc.
    #
    with requests.get(**request_args) as response:
        version_string = response.text

    if version_string == "":
        logging.error("Version string was not set!")
        sys.exit(1)

    latest_version = re.search(search_term, version_string)
    return latest_version.groups()[0]


def get_installed_version_num():
    """
    Function uses apt to determine if Discord is already installed.

    In the event that Discord *has not* been installed, we'll return a 0.0.0
    version number, which will enable installation.
    """
    search_term = r".+Installed:\s([\d\.]+)\s.+"
    package_name = DISCORD_PKG_NAME

    version_string = ""

    # FIXME - We should probably use dpkg instead to avoid apt scripting stderr
    #   `WARNING: apt does not have a stable CLI interface. Use with caution in scripts.`
    #
    with Popen(["apt", "policy", package_name], stdout=PIPE, encoding="UTF-8") as apt:
        stdout = apt.stdout.read()

        if not stdout:
            logging.debug("%s is not installed!", package_name)
            return "0.0.0"

        version_string = re.search(search_term, stdout).groups()[0]

    return version_string


def is_version_newer(version_a: str, version_b: str) -> bool:
    # Naive validation, checks that period is used for delimiting.
    #
    for ver in version_a, version_b:
        if "." not in ver:
            logging.error("Invalid version format found!")
            sys.exit(1)

        continue

    # Split the version string into it's constituent integer parts so we
    # can 'just' do 1-1 comparisons.
    #
    a = version_a.split(".")
    b = version_b.split(".")

    for version in a, b:
        if len(version) != 3:
            logging.error("Unexpected version strings found!")
            sys.exit(1)

        continue

    log_message = f"Version A, '{version_a}' is older than B, '{version_b}'"

    # REFAC - do this with a list comprehension.
    # FIXME - Cases whereby A is the same as B result in A appearing as older.
    #
    for subversion in [0, 1, 2]:
        if a[subversion] < b[subversion]:
            logging.info(log_message)
            return False

    logging.info("Version B is newer!")
    return True


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

    # FIXME - validate that f_path does not yet exist.
    #

    logging.debug("Will write install file to %s", f_path)

    with requests.get(**request_args) as req:
        req.raise_for_status()
        with open(f_path, "wb") as f:
            for chunk in req.iter_content(chunk_size=c_size):
                f.write(chunk)

    # A sanity check that things have gone to plan.
    #
    _is_file_present(f_path)

    logging.info("Installation package installed.")
    return f_path


def install_package(f_path: str, dry_run: bool):
    _is_file_present(f_path)

    if dry_run:
        logging.info("Dry run was requested; will not attempt Discord upgrade.")
        return

    # FIXME - Need handling for the following:
    #   dpkg: error: cannot access archive '/tmp/discord-${UUID}': No such file or directory
    #
    Popen(["sudo", "dpkg", "-i", f_path], stdout=PIPE, encoding="UTF-8")
    logging.info("Discord has been updated.")


def _is_file_present(f_path: str):
    install_path = Path(f_path)

    if not install_path.is_file():
        logging.error("The Discord download at %s could not be found!", f_path)
        sys.exit(1)

    logging.debug("Discord download at %s was verified.", f_path)


def delete_install_file(f_path: str):
    remove(f_path)


if __name__ == "__main__":
    main()
