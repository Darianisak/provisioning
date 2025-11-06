# TODO - This documentation needs a rewrite

# integration-tests

This directory contains scripts for assisting with manually testing the system provisioning process.

## Helper commands

Run the test suite:

``` bash
docker compose run --remove-orphans --build --interactive -t testing

./opt/integration-tests/tag-regressions/test-tags.sh
```

Create a basic system user account for validating ownership, etc. (interactive)
    N.B. Maybe investigate the Ansible user module?

``` bash
sudo adduser $NAME
```


Ansible debugger:
https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_debugger.html#resolving-errors-in-the-debugger

`p task_vars` for variables

`p result._return_data` for job output

`p task_vars['ansible_facts]` to 'drill down' into the `ansible_facts` for this host.

``` bash
# Dumping all objects. Ansible debugger is just Python objects.
# Wrap anything you want methods from with `dir()`

[localhost] TASK: Check if using gnome (debug)> dir()
['host', 'play_context', 'result', 'task', 'task_vars']

dir(task)
p dir(task)
```
