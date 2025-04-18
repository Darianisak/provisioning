# integration-tests

This directory contains scripts for assisting with manually testing the system provisioning process.

## Helper commands

Checking what tasks are available in an Ansible playbook:
`ansible-playbook $PLAYBOOK_FILE --list-tasks -K`

Start Ansible from a specific task:
`ansible-playbook $PLAYBOOK_FILE --start-at-task $TASK_NAME --verbose -K`

Note: Password, `-K` is `foo` - defined in Dockerfile.

Run the test suite:
```
# Localhost
docker compose run --remove-orphans --build --interactive -t testing

./opt/integration-tests/tag-regressions/test-tags.sh
```

Provision a system:
`ansible-playbook provision.yaml -K --ask-vault-pass`


Create a basic system user account for validating ownership, etc. (interactive)
    N.B. Maybe investigate the Ansible user module?
`sudo adduser $NAME`


Ansible debugger:
https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_debugger.html#resolving-errors-in-the-debugger

`p task_vars` for variables

`p result._result` for job output

`p task_vars['ansible_facts]` to 'drill down' into the `ansible_facts` for this host.

```
# Dumping all objects. Ansible debugger is just Python objects.
# Wrap anything you want methods from with `dir()`

[localhost] TASK: Check if using gnome (debug)> dir()
['host', 'play_context', 'result', 'task', 'task_vars']

dir(task)
p dir(task)
```
