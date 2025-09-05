# Tandem: A Linux upgrade client for Discord
## What is Tandem?

*Tandem* is a *[dpkg]* based upgrade client for [Discord]'s Linux desktop app.

## Motivation

*Tandem* was born out a minor annoyance: the Linux Desktop application
*does not* auto update.

With *Tandem*, what used to be a multi click process is now a simple command,
which *can also* be run in the background.

## Using Tandem

If you're *not* planning on poking around with *Tandem's* source code, then
you can use the pre-built binary executable.

This binary can be downloaded from the project's releases, [here][Releases].

Once you've downloaded the appropriate binary, it can be run like so:

``` bash
cd ~/Downloads

./tandem --help

"""
usage: tandem [-h] [-v] [--dpkg-verbose] [--dry-run]

A Discord upgrade client for Linux.

options:
  -h, --help      show this help message and exit
  -v, --verbose   Enables verbose logging.
  --dpkg-verbose  Enables dpkg verbose logging.
  --dry-run       Toggle whether Discord will be updated.

Authored by <culver.darian@gmail.com>, licensed under GPL v3.
"""
```

## Using Tandem *during* development

Using *Tandem* during development is easy, *but* it does assume you have a
few things installed:

* dpkg
* git
* Python
* Python's pip module
* Python's venv module
* Discord's package dependencies
  * libasound2
  * libatomic1
  * libnotify4
  * libnspr4
  * libnss3
  * libxss1
  * libxtst6

Once these are installed, you're ready to go!

### 1: Checking out the project

First, we'll get *Tandem*'s source code onto our machine:

``` bash
mkdir /tmp/tandem
cd /tmp/tandem
git clone git@github.com:Darianisak/provisioning.git --depth=1
```

### 2: Creating a Virtual Environment

Then, we'll create a virtual environment to prevent *Tandem* from interfering
with other projects, and/or system packages:

``` bash
cd /tmp/tandem/provisioning
python3 -m venv .venv
source .venv/bin/activate
pip install --requirement ansible/roles/discord/bin/updater/requirements.txt
```

### 3: Running Tandem

And then we'll run *Tandem* to install or update Discord:

``` bash
python3 ansible/roles/discord/bin/updater/update_discord.py

"""
INFO - Installed version: 0.0.108
INFO - Upstream version: 0.0.108
INFO - Installed version is up to date!
"""
```

And then we'll check that Discord has been installed with:

``` bash
apt policy discord
```

For further details about *Tandem*, or the options that it can take, check out
the help dialog:

``` bash
python3 ansible/roles/discord/bin/updater/update_discord.py --help

"""
usage: tandem [-h] [-v] [--dpkg-verbose] [--dry-run]

A Discord upgrade client for Linux.

options:
  -h, --help      show this help message and exit
  -v, --verbose   Enables verbose logging.
  --dpkg-verbose  Enables dpkg verbose logging.
  --dry-run       Toggle whether Discord will be updated.

Authored by <culver.darian@gmail.com>, licensed under GPL v3.
"""
```

## Building Tandem

*Tandem* is build using [PyInstaller], which complies the tool into a single
binary file.

*Assuming* you already have the project checked out under `/tmp/tandem`, the
next step would be to create a virtual environment:

``` bash
cd /tmp/tandem/provisioning
python3 -m venv .venv
source .venv/bin/activate
pip install --requirement ansible/roles/discord/bin/updater/requirements.txt

```

Then, we'll run the build process:

``` bash
cd ansible/roles/discord/bin/updater
pyinstaller update_discord.py --onefile --name tandem
```

Alongside a number of build artifacts, this will produce a single executable
binary file:

``` bash
cd dist

./tandem --help

"""
usage: tandem [-h] [-v] [--dpkg-verbose] [--dry-run]

A Discord upgrade client for Linux.

options:
  -h, --help      show this help message and exit
  -v, --verbose   Enables verbose logging.
  --dpkg-verbose  Enables dpkg verbose logging.
  --dry-run       Toggle whether Discord will be updated.

Authored by <culver.darian@gmail.com>, licensed under GPL v3.
"""
```

## FAQ
### What distributions has this been tested with?

*Tandem* has been tested with both Ubuntu Noble and Debian Bookwork.

### What if I already have Discord installed?

That's great! *Tandem* will not attempt to do an update *unless* your installed
version of Discord *is* older than the most recently released version from
Discord's upgrade channels.

*If* you have the most recently released version already, *Tandem* will not
attempt to do anything.

<!-- Links -->

[dpkg]: https://man7.org/linux/man-pages/man1/dpkg.1.html
[Discord]: https://discord.com/
[PyInstaller]: https://pyinstaller.org/en/stable/index.html
[Releases]: https://github.com/Darianisak/provisioning/releases
