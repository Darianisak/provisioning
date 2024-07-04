#! /usr/bin/bash

set -e

if ! docker --version; then
    echo -e "\nError! Pre-requisite 'docker' is not installed!\n"
    exit 1
fi

echo -e "\nSetting up test environment...\n"

DOCKER_IMAGE="debian:bookworm"
DOCKER_BASH_PATH="/usr/bin/bash"
SYSTEM_MOUNT_POINT="/home/$USER/code/provisioning"
DOCKER_MOUNT_POINT="/home/code"
TEST_USER="www-data"

echo -e "\nProvisioning docker environment...\n"

docker run --user root --tty --volume "${SYSTEM_MOUNT_POINT}:${DOCKER_MOUNT_POINT}" \
    --env INPUT_USERNAME="${TEST_USER}" "${DOCKER_IMAGE}" \
    "${DOCKER_BASH_PATH}" "${DOCKER_MOUNT_POINT}/bootstrap.sh"
