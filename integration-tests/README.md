# integration-tests

This directory contains scripts for assisting with manually testing the system provisioning process.

## Helper commands

Checking what tasks are available in an Ansible playbook:
`ansible-playbook $PLAYBOOK_FILE --list-tasks`

Start Ansible from a specific task:
`ansible-playbook $PLAYBOOK_FILE --start-at-task $TASK_NAME --verbose`

Run the test suite:
```
# Localhost
./integration-tests/interactive-container.sh

# In the container:
./home/code/bootstrap.sh
./home/code/integration-tests/tag-regressions/test-tags.sh
```

Provision a system:
`ansible-playbook provision.yaml -K`


Create a basic system user account for validating ownership, etc. (interactive)
    N.B. Maybe investigate the Ansible user module?
`sudo adduser $NAME`