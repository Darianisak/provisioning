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
    echo "Are you in the project root?"
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

    echo -e "Test ${1} - ${3}\n" > "${TMP_TEST_FILE}"

    # shellcheck disable=SC2086
    ansible-playbook $DEFAULT_ARGS $2 >> "${TMP_TEST_FILE}"

    if ! diff "${TEST_FILE}" "${TMP_TEST_FILE}"; then
        echo "Failure."
    else
        echo "Success."
        rm "${TMP_TEST_FILE}"
    fi
}

echo -e "\nRunning Naive regression tests...\n\n"

run_test "001" " " "# Check the 'default' provisioning order"

run_test "002" "--tags always" "# Check tasks that are 'always' run"

run_test "003" "--tags apt" "# Check apt execution order"

run_test "004" "--tags docker" "# Check docker installation steps"

run_test "005" "--tags keyring" "# Check keyring installation order"

run_test "006" "--tags spotify" "# Check spotify installation steps"

run_test "007" "--tags codium" "# Check Codium installation steps"

run_test "008" "--tags extensions" "# Check Codium extension steps"

run_test "009" "--tags settings" "# Check Codium settings steps"

run_test "010" "--tags source" "# Check source file maniuplation order"

run_test "011" "--tags nvidia" "# Check nVidia installation order"

run_test "012" "--tags i386" "# Check configuration order of i386"

run_test "013" "--tags steam" "# Check configuration order for Steam"

run_test "014" "--tags git" "# Check git configuration order."

run_test "015" "--tags gnome" "# Check gnome configuration order."

run_test "016" "--tags ssh" "# Check SSH configuration order."
