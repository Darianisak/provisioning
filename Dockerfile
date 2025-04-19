
# Defines base image for testing provisioning tooling.
# Essentially 'just' for ensuring a patched base image.
#
# docker build --file Dockerfile --target base-image --tag base .
#
FROM debian:bookworm AS base-image
SHELL ["/bin/bash", "-exo", "pipefail", "-c"]

RUN \
    apt-get update \
    && apt-get dist-upgrade --assume-yes \
    && apt-get clean --assume-yes \
    && rm --recursive --force /var/lib/apt/lists/*

# Our testing image. Runs the bootstrap script and adds the resulting
# VirtualEnv to the user's path.
#
# docker compose run --remove-orphans --build --interactive -t testing
#
FROM base-image AS ansible-test-image

ARG INPUT_USERNAME=unset-username
ARG VOL_MOUNT=/opt

SHELL ["/bin/bash", "-exo", "pipefail", "-c"]

COPY ./bootstrap.sh /opt/bootstrap.sh

# This is a localhost test container, a 'foo' password is non issue.
#
# Note: Don't purge openssl - that breaks things during playbooks.
#
RUN \
    apt-get update \
    && apt-get install openssl --assume-yes --no-install-recommends \
    && useradd -p $(openssl passwd -6 'foo') -ms /bin/bash ${INPUT_USERNAME} \
    && /opt/bootstrap.sh \
    && rm --force /opt/bootstrap.sh \
    && apt-get clean --assume-yes \
    && rm -rf /var/lib/apt/lists/*

WORKDIR ${VOL_MOUNT}

USER ${INPUT_USERNAME}

ENV PATH="/home/${INPUT_USERNAME}/venvs/ansible/bin:${PATH}"
