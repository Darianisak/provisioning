#! /usr/bin/bash

set -e

echo -e \ "\nbootstrap.sh: A slightly hacky script for system provisioning.\n"

# Check release
apt-get update && apt-get install --assume-yes --no-install-recommends \
    --auto-remove --quiet lsb-release

DIST_CODENAME=$(lsb_release --short --codename 2>/dev/null)

# FIXME - room for improvement using cURL to have distro specific version files,
# similar to how we're dealing with Ansible requirements.
if [ "${DIST_CODENAME}" == "bookworm" ]; then
    echo -e "\nSetting up package versions for Debian Bookworm...\n"
    GIT_VERSION="1:2.39.2-1.1"
    PYTHON_VENV_VERSION="3.11.2-6"
    CURL_VERSION="7.88.1-10+deb12u5"  # This SHOULD already be installed.
else
    echo -e "\nError! Current distro is not supported!\n"
    exit 1
fi

BASE_REPOSITORY_URL="https://raw.githubusercontent.com/Darianisak/provisioning"
GIT_BRANCH="darianculver/bootstrap-script"
ANSIBLE_REQUIREMENTS="ansible-requirements.txt"

echo "A (slightly interactive) script for bootstraping the device for provisioning."

if [ "$(whoami)" != 'root' ]; then
    echo "Error! Please run this script as root."
    exit 1
fi

# Assumption: INPUT_USERNAME will always get defined.
# FIXME - this could do with some input validation, given it's used for a regex
read -r --prompt "Username? " INPUT_USERNAME

if grep "^sudo:x:.*:.*${INPUT_USERNAME}.*$" /etc/group ; then  
    echo "User already in sudoers. Skipping..."
else
    echo "Adding user to sudoers..."
    usermod -aG sudo "${INPUT_USERNAME}"
fi

# Prepare env for Ansible provisioning.
apt-get update && \
    apt-get install -y git="${GIT_VERSION}" curl="${CURL_VERSION}" \
    python3.11-venv="${PYTHON_VENV_VERSION}"


mkdir --parents "/home/${INPUT_USERNAME}/code" && \
    mkdir --parents "/home/${INPUT_USERNAME}/venvs"


mkdir --parents "/home/${INPUT_USERNAME}/venvs/ansible" &&
    ( 
        cd "/home/${INPUT_USERNAME}/venvs/ansible" &&
        python3 -m venv ansible ./
    )

curl "${BASE_REPOSITORY_URL}/${GIT_BRANCH}/${ANSIBLE_REQUIREMENTS}" --output \
    "/home/${INPUT_USER}/.ansible-requirements.txt"

chown --verbose --preserve-root --recursive "${INPUT_USERNAME}:${INPUT_USERNAME}" \
    "/home/${INPUT_USERNAME}"

# shellcheck disable=SC1091
source ansible/bin/activate  

pip --require-virtualenv install --requirement \
    "/home/${INPUT_USER}/.ansible-requirements.txt"

deactivate

rm "/home/${INPUT_USER}/.ansible-requirements.txt"
