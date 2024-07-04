#! /usr/bin/bash

set -e

if [ -f .github-vars ]; then
    echo -e "Running in CI - sourcing environment file..."
    # shellcheck disable=SC1091
    source .github-vars
fi

echo -e \ "\nbootstrap.sh: A slightly hacky script for system provisioning.\n"

# Check release
apt-get update && apt-get install --assume-yes --no-install-recommends \
    --auto-remove --quiet lsb-release

DIST_CODENAME=$(lsb_release --short --codename 2>/dev/null)

# FIXME - room for improvement using cURL to have distro specific version files,
# similar to how we're dealing with Ansible requirements.
echo -e "\nSetting up package versions for ${DIST_CODENAME}...\n"

BASE_REPOSITORY_URL="https://raw.githubusercontent.com/Darianisak/provisioning"
GIT_BRANCH="main"
ANSIBLE_REQUIREMENTS="ansible-requirements.txt"

if [ "$(whoami)" != "root" ]; then
    echo -e "\nError! Please run this script as root!\n"
    exit 1
fi

if [ -z "${INPUT_USERNAME}" ]; then
    # FIXME - this could do with some input validation, given it's used for a regex
    echo -e "'INPUT_USERNAME' not found in environment. Prompting..."
    read -rp "Username? " INPUT_USERNAME
fi

if ! id --user "${INPUT_USERNAME}" 2>/dev/null ; then
    USERS=$(cut -d: -f1 /etc/passwd)
    echo -e "\nError! User '${INPUT_USERNAME}' does not exist!\n"
    echo -e "\nValid users are: ${USERS}\n"
    exit 1
fi

if grep "^sudo:x:.*:.*${INPUT_USERNAME}.*$" /etc/group ; then
    echo -e "\nUser already in sudoers. Skipping...\n"
else
    echo -e "\nAdding user to sudoers...\n"
    usermod -aG sudo "${INPUT_USERNAME}"
fi

echo -e "\nUpdating apt repositories and installing dependencies...\n"

apt-get update && \
    apt-get install --assume-yes --no-install-recommends --auto-remove --quiet \
    git curl python3.11-venv python3-apt  # python3-apt for ansible-playbook --check

mkdir --parents "/home/${INPUT_USERNAME}/code" && \
    mkdir --parents "/home/${INPUT_USERNAME}/venvs/ansible"

(
    cd "/home/${INPUT_USERNAME}/venvs" &&
    python3 -m venv ansible ./
)

echo -e "\nDownloading Ansible requirements...\n"
curl "${BASE_REPOSITORY_URL}/${GIT_BRANCH}/${ANSIBLE_REQUIREMENTS}" --output \
    "/home/${INPUT_USER}/.ansible-requirements.txt"

cat "/home/${INPUT_USER}/.ansible-requirements.txt"

echo -e "\nAmending ownerships with chown (/dev/null)...\n"
chown --verbose --preserve-root --recursive "${INPUT_USERNAME}:${INPUT_USERNAME}" \
    "/home/${INPUT_USERNAME}" &>/dev/null  # dev/null causes it's LOUD

# shellcheck disable=SC1091,SC1090
source "/home/${INPUT_USERNAME}/venvs/ansible/bin/activate"

echo -e "\nInstalling Ansible requirements for ansible-venv...\n"
pip --require-virtualenv install --requirement \
    "/home/${INPUT_USER}/.ansible-requirements.txt"

deactivate
rm "/home/${INPUT_USER}/.ansible-requirements.txt"
