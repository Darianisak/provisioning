#! /usr/bin/bash

set -e

# Define package versions
GIT_VERSION=1:2.39.2-1.1
PYTHON_VENV_VERSION=3.11.2-6
ANSIBLE_CORE_VERSION=2.17.1

echo "A (slightly interactive) script for bootstraping the device for provisioning."

if [ "$(whoami)" != 'root' ]; then
    echo "Error! Please run this script as root."
    exit 1
fi

# Assumption: INPUT_USERNAME will always get defined, though this could
# handle NULL inputs better, etc.
read -r --prompt "Username? " INPUT_USERNAME

if grep "^sudo:x:.*:.*${INPUT_USERNAME}.*$" /etc/group ; then  
    echo "User already in sudoers. Skipping..."
else
    echo "Adding user to sudoers..."
    usermod -aG sudo "${INPUT_USERNAME}"
fi

# Install dependencies for further provisioning, i.e., Ansible.
apt-get update && \
    apt-get install -y git="${GIT_VERSION}" python3.11-venv="${PYTHON_VENV_VERSION}" 

# Set up base directories
mkdir --parents "/home/${INPUT_USERNAME}/code" && \
    mkdir --parents "/home/${INPUT_USERNAME}/venvs"

chown --verbose --preserve-root --recursive "${INPUT_USERNAME}:${INPUT_USERNAME}" "/home/${INPUT_USERNAME}/code"

# Set up provisioning venv
mkdir --parents "/home/${INPUT_USERNAME}/venvs/ansible" &&
    ( 
        cd "/home/${INPUT_USERNAME}/venvs/ansible" &&
        python3 -m venv ansible ./
    )

# Switch to provisioning virtual env and install Ansible, etc.
# shellcheck disable=SC1091
source ansible/bin/activate  

pip install ansible-core=="${ANSIBLE_CORE_VERSION}"
