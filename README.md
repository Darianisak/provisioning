# Provisioning: Automating environment setup, one package at a time.
## What is Provisioning?

*Provisioning* is an automation tool set, built on [Ansible], which brings
enterprise configuration management and [IaC] principles to home systems.

*Provisionings* value add is that it can take a clean system install and
handle everything from Codium preferences to Video Game launchers *and*
their dependencies, in as little as 5 minutes.

## Motivation

After one-to-many system rebuilds, I got fed up with redefining apt-sources,
reading obscure documentation, and just generally not being able to use my PC.

This reached a breaking point while installing [Steam], which has a number of
[undeclared dependencies][Steam-Issue] in the Debian documentation.

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


## Using Provisioning

When we talk about *Provisioning*, we're typically referring to the [Ansible]
'core', but there's a few different ways we can use the software.

### From a cold install

Using *Provisioning* to set up a system after installing the Operating System
is the *exact* use case this tool was written for.

#### 1: Run the setup script

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
## FAQ
### What distributions has this been tested with?

The entire *Provisioning* suite has been tested with Debian Bookworm.

There's only a few *hard* requirements a system must meet to use *Provisioning*:

* Python3
* Dpkg
* Apt
* Being connected to the internet

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
