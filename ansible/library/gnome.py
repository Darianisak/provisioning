#!/usr/bin/env python

# Copyright: (c) 2025, Darian Culver <culver.darian@gmail.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""



def run_module():
    """
    want module to take in an ordered list of key:val
    need to check installation state of each app 
    need to remove non-installed packages from the order
    need to call gsettings and apply.
    """
    pass


def validate_key_value_pairs():
    """
    Verifies the structure of the data passed to `gnome.py`.

    E.g., that each list item *is* a key:value pair
    """
    pass


def validate_args_content():
    """
    Verifies the *content* of the data passed to `gnome.py` as being
    in the expected format.

    E.g., that each items key is a *package name*, and each value is a
    desktop binary(?) for gsettings.
    """
    pass


def main():
    run_module()


if __name__ == "__main__":
    main()
