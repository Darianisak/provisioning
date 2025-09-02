import sys
import re
import logging
from subprocess import Popen, PIPE
from uuid import uuid1
from os import remove
from pathlib import Path
import requests

DISCORD_LINUX_DOWNLOAD = "https://discord.com/api/download?platform=linux"
DISCORD_PKG_NAME = "discord"
REQUEST_TIMEOUT = 30


def main():
    # FIXME - Use argparse to support toggling the verbosity.
    #
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s - %(message)s"
    )

    latest_version = get_latest_version_num()
    logging.info("Upstream version: %s", latest_version)

    installed_version = get_installed_version_num()
    logging.info("Installed version: %s", installed_version)

    if is_version_newer(installed_version, latest_version):
        logging.info("The installed version is not the most recent!")
    else:
        logging.info("Installed version is up to date!")
        sys.exit(0)

    f_path = f"/tmp/discord-{uuid1()}"
    download_latest(f_path)
    install_package(f_path)

    delete_install_file(f_path)

    logging.info("Package installed.")
    sys.exit(0)


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


def install_package(f_path: str):
    _is_file_present(f_path)
    # FIXME - Need handling for the following:
    #   dpkg: error: cannot access archive '/tmp/discord-${UUID}': No such file or directory
    #
    Popen(["sudo", "dpkg", "-i", f_path], stdout=PIPE, encoding="UTF-8")


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
