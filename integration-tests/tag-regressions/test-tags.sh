#! /usr/bin/bash

set -e

if [ -f .github-vars ]; then
    echo -e "Running in CI - sourcing environment file..."
    # shellcheck disable=SC1091
    source .github-vars
    # shellcheck disable=SC1091
    source "${VIRTUAL_ENV}/bin/activate"
fi

echo -e "\nA bash script for performing basic/naive regression tests execution order.\n"

if [ -e "${VIRTUAL_ENV}" ]; then
    if ! pip list | grep 'ansible-core' > /dev/null ; then
        echo -e "\nError! 'ansible-core' not found!\n"
        exit 1
    fi
else
    echo -e "\nError! No venv sourced!\n"
    exit 1
fi

DEFAULT_ARGS="ansible/provision.yaml --list-tasks --inventory ansible/inventory"
EXPECTED_DIR="integration-tests/tag-regressions/expected"

if ! touch "${EXPECTED_DIR}/.00X.txt" 2>/dev/null ; then
    echo -e "\nError! Can't write tempfiles to ${EXPECTED_DIR}\n"
    exit 1
else
    rm "${EXPECTED_DIR}/.00X.txt"
fi

function run_test() {
    # Takes input args:
    #   1: Test number, "001", "00N"
    #   2: Ansible tag, "--tags always", "--tags apt"

    TEST_FILE="${EXPECTED_DIR}/${1}.txt"
    TMP_TEST_FILE="${EXPECTED_DIR}/.${1}.txt"

    echo -e "\nChecking for regressions against ${TEST_FILE}..."

    # shellcheck disable=SC2086
    ansible-playbook $DEFAULT_ARGS $2 > "${TMP_TEST_FILE}"

    if ! diff "${TEST_FILE}" "${TMP_TEST_FILE}"; then
        echo "Failure."
    else
        echo "Success."
    fi
    rm "${TMP_TEST_FILE}"
}

echo -e "\nRunning Naive regression tests...\n\n"

# Test 'default' tasks.
run_test "001" " "

# Test 'always' tasks.
run_test "002" "--tags always"

# Test 'apt' tasks.
run_test "003" "--tags apt"