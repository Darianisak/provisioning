import re
import logging
from subprocess import Popen, PIPE
import requests

DISCORD_LINUX_DOWNLOAD = "https://discord.com/api/download?platform=linux"
DISCORD_PKG_NAME = "discord"
REQUEST_TIMEOUT = 6


def main():
    latest_version = get_latest_version_num()
    logging.info("Upstream version: %s", latest_version)

    installed_version = get_installed_version_num()
    logging.info("Installed version: %s", installed_version)

    pass


def get_installed_version_num():
    # FIXME - need to handle cases whereby discord is not installed

    return re.search(
        r".+Installed:\s([\d\.]+)\s.+",
        Popen(
            ["apt", "policy", DISCORD_PKG_NAME], stdout=PIPE, encoding="UTF-8"
        ).stdout.read(),
    ).groups()[0]


def get_latest_version_num():
    # By preventing redirection, we can determine the latest version from the
    # redirect URL, without needing to download the package.
    #
    search_term = r".+<a href=\"(.+)\">.+"

    request_args = {
        "url": DISCORD_LINUX_DOWNLOAD,
        "allow_redirects": False,
        "timeout": REQUEST_TIMEOUT
    }

    version_string = ''

    with requests.get(**request_args) as response:
        version_string = response.text

    if version_string == '':
        # FIXME : error state
        return ''

    version = re.search(search_term, version_string).groups(1)[0]
    
    

        # .groups(1)[0]
        # .split("/")[5]


def update_to_latest():
    pass


if __name__ == "__main__":
    main()
