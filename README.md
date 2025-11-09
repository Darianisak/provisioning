# Provisioning: Automating environment setup, one package at a time.
## What is Provisioning?

*Provisioning* is an automation tool set, built on [Ansible], which brings
enterprise configuration management and [IaC] principles to home systems.

*Provisioning's* value add is that it can take a clean system install and
handle everything from Codium preferences to Video Game launchers *and*
their dependencies, in as little as 5 minutes.

## Motivation

After one-to-many system rebuilds, I got fed up with redefining apt-sources,
reading documentation, and generally being unable to use my computer.

This reached a breaking point while installing [Steam], which has a number of
[dependencies][Steam-Issue] that aren't mentioned on the Debian wiki.

So, having a background in DevOps and experience with Ansible, I set about
codifying *my entire* home PC - this project is the ongoing result of
that effort.

## Other Tools

While the 'core' of *Provisioning* is it's flexible [Ansible] based backend,
this project *also* implements a few other tools:

### TestTags

*TestTags*, which was inspired by a past job working with unyieldly [Ansible]
playbooks, is a *Shell* based test framework for catching regressions in the
execution order of [Ansible] playbooks.

Put another way, this tool helps to ensure that *A runs before B*, and helps
to catch changes that would make *B run before A*.

For more details, check out *TestTags* documentation, [here][TestTags].

## Using

When we talk about *Provisioning*, we're typically referring to the [Ansible]
'core', but there's a few different ways we can use the software.

### From a cold install

TODO - this section is under construction!

Using *Provisioning* to set up a system after installing the Operating System
is the *exact* use case this tool was written for.

#### Run the setup script

We'll first define *what* our username is:

``` bash
export INPUT_USERNAME="your_username"
```

Then, we'll run the bootstrap script to prepare our environment for running
the Ansible tooling:

``` bash
mkdir /tmp/prov
cd /tmp/prov
curl https://raw.githubusercontent.com/Darianisak/provisioning/main/bootstrap.sh -o ./bootstrap.sh
chmod 0755 bootstrap.sh
/usr/bin/bash bootstrap.sh
```

<!-- FIXME: The bootstrap script is broken; unsure how long that's been the case for. -->

<!-- For the time being, we'll also need to update some metadata manually: -->
<!--  -->
<!-- ``` bash -->
<!-- # sed 's/darianculver/<your_username>/g' -i -->
<!-- ``` -->


<!-- ### Interactively, in a pre-existing install -->
<!--  -->
<!--  -->
<!-- ## Enhancing Provisioning -->
<!--  -->

### Selectively

Say you wanted to install [Codium] with extensions, settings, and themes with
one command - *provisioning* let's you do that.

Assuming you've got a [Development](#development) checkout, this type of
operation would look like:

``` bash
source .venv
cd provisioning/ansible
ansible-playbook -K provision.yaml --tags codium
```

### Against a remote host

*Provisioning* also supports defining remote environments via playbooks:

``` bash
cd provisioning
source .venv/bin/activate
cd ansible

ansible-playbook remote.yaml --inventory inventory
```

## Development

Ansible can be cumbersome to develop for, so *provisioning* makes an effort
to provide a repeatable and easily extendable dev work flow.

### Preparing a dev environment

Development environment set up is reasonably standard:

``` bash
# Cloning the checkout
#
git clone git@github.com:Darianisak/provisioning.git

# Preparing the dev virtual environment
#
cd provisioning
python3 -m venv .venv
source .venv

# Installing Python dependencies
#
pip install -r ansible-requirements.txt

# Installing Ansible dependencies
#
ansible-galaxy install -r ansible/requirements.yaml
```

### Testing with Docker

Once you've written a play and would like to test that it *actually* works,
we can spin up a Docker container to isolate the filesystem changes.

``` bash
cd provisioning

# Use `docker compose` to manage the life cycle of our container.
# `--remove-orphans` is provided to ensure we clean up old containers and don't
# run into service name collision.
#
docker compose run --remove-orphans local_node

# Navigate to the `ansible` directory. Our venv is already sourced in the shell.
#
cd ansible

# Now run Ansible against your play's tag with `--tags`
# `-K` will prompt you for the super user password, which is `foo`.
#
ansible-playbook provision.yaml --tags $YOUR_PLAY_TAG -K

# You can also check *what* tags are available
#
ansible-playbook provision.yaml --list-tags

# If your play requires the Ansible vault, you'll need to provide your
# vault credentials
#
ansible-playbook provision.yaml --tags $YOUR_PLAY_TAG -K --ask-vault-pass
```

Please note that this workflow relies on the use of [Ansible Tags].

### Testing *remote* system provisioning with Docker

This project also provides a degree of parity with a remote host, i.e., one you
would provision over SSH in the form of two Docker containers.

This workflow can be used by:

``` bash
# Starting up the 'remote' compose profile
#
docker compose --profile remote up --remove-orphans

# Getting an interactive shell in the 'main' service container of the
# remote profile, 'control_node'
#
docker compose exec -it control_node bash

# Running Ansible with the `remote.yaml` playbook and feeding it an inventory.
#
cd ansible
ansible-playbook -K remote.yaml --inventory /tmp/inventory
```

#### How the remote workflow works

The remote workflow is intended as a parity approximation of deploying to an
*actual* Debian 13 virtual machine.

This works by:

* Defining a testing SSH key pair in `docker-compose.yaml`.
  * This key pair *is not* sensitive and was created for this purpose alone.
* Mounting the respective key pair portions into `control_node`
  and `follower_node`.
* Ensuring the `follower_node` is running `sshd` as part of it's entrypoint,
  and is listening/exposing port 22.
* Overriding the default SSH config for `control_node` to
  disable `StrictHostKeyChecking`.

This workflow *isn't* without it's faults, but it does give us some degree of
confidence that our playbooks won't seriously damage a *real* remote machine.

### Using the Ansible debugger

Ansible has support for a pretty decent interactive run-time debugger, but
the upstream documentation is pretty lacking.

#### Setting breakpoints

To use the debugger, you'll need to add the `debugger` attribute to your plays.

``` yaml
# A 'debugger' that will trigger every time this play is run.
#
# This is generally pretty helpful during active development of a play.
#
- name: a test play
  debugger: 'always'
  ansible.builtin.command:
    cmd: echo "hello world"

# A 'debugger' that will *only* trigger given a play failure.
#
# I find this pretty handy to define for the top level play, that way any
# failure gets caught and we can dig into the problematic state.
#
- name: a test play
  debugger: 'on_failed'
  ansible.builtin.command:
    cmd: echo "hello world"
```

For further details on setting breakpoints, check out the upstream
[Ansible Debugger] documentation.

#### Getting value from the debugger

Once you've had a [breakpoint](#setting-breakpoints) trigger, you'll get
dumped into an interactive Python shell with a little bit of syntactic sugar.

While the [documentation][Ansible Debugger] covers the individual commands,
it doesn't do a good job of explaining *how* you can use those commands, so...

``` bash
# Getting ALL the variables present for this task.
#
p task_vars

# Getting the response/return for a task - both success and failure.
#
p result._return_data

# Getting the 'ansible_facts' variable out of the current var scope.
#
p task_vars['ansible_facts']
```

A *really* cool thing to realize with the debugger is that Ansible works
*exclusively* with Python objects, so you can use the interactive debugger in
the same you would a Python REPL with much the same functions:

``` python
# Converting the response to a list and then get the len of the response.
#
p len(list(result._result_data))

# Getting the valid functions for a given Ansible object
#
p dir(task_vars)
```

### Checking for execution order changes with TestTags

If you've worked with large Ansible code bases before, you'll know that
refactors and other changes can modify the execution order quite dramatically.

For that reason, I wrote the TestTags tool, which takes a manifest of the
entire play (based on tags) and tracks it in git for easy regression analysis.

These checks can be run like so:

``` bash
docker compose run --remove-orphans local_node


# Run `TestTags` to get the apply manifest.
#
./opt/integration-tests/tag-regressions/test-tags.sh

# Manually diff the manifests for regressions
#
cd /opt/integration-tests/tag-regressions/expected
diff .001.txt 001.txt
```

## FAQ
### What distributions has this been tested with?

The entire *Provisioning* suite has been tested with Debian Bookworm.

There's only a few *hard* requirements a system must meet to use *Provisioning*:

* The following software installed:
    * `python3`
    * `dpkg`
    * `apt`
    * `openssl`
    * `sudo`
* An internet connection

### This seems like a lot of overhead

...It is!

But at the end of the day, I enjoy working on this project, *and* it's taught
me a few things, so I can't complain.

### Why not Puppet, Salt, etc.?

*Provisioning* is [Ansible] based, *mainly* because it's what I was most
familiar with at the time I started the project.

There are other benefits, though, in that we don't need to maintain
leader:follower nodes, and there's scope to run *Provisioning* against
remote hosts, though we aren't doing that yet.

<!-- Links -->

[Ansible]: https://docs.ansible.com/
[IaC]: https://en.wikipedia.org/wiki/Infrastructure_as_code
[Steam]: https://store.steampowered.com/
[Steam-Issue]: https://github.com/ValveSoftware/steam-for-linux/issues/7284#issuecomment-2414009466
[TestTags]: https://github.com/Darianisak/provisioning/blob/main/integration-tests/README.md
[Codium]: https://vscodium.com/
[Ansible Tags]: https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_tags.html
[Ansible Debugger]: https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_debugger.html
