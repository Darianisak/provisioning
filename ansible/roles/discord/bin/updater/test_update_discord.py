import unittest
import logging
from update_discord import is_remote_version_newer

# <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>Redirecting...</title>\n<h1>Redirecting...</h1>\n<p>You should be redirected automatically to target URL: <a href="https://stable.dl2.discordapp.net/apps/linux/0.0.107/discord-0.0.107.deb">https://stable.dl2.discordapp.net/apps/linux/0.0.107/discord-0.0.107.deb</a>.  If not click the link.

logging.disable()


class TestVersionComparison(unittest.TestCase):
    def test_local_major_newer(self):
        local = "2.0.0"
        remote = "1.0.0"
        self.assertFalse(is_remote_version_newer(local, remote))

    def test_local_major_older(self):
        local = "1.0.0"
        remote = "2.0.0"
        self.assertTrue(is_remote_version_newer(local, remote))

    def test_local_minor_newer(self):
        local = "0.2.0"
        remote = "0.1.0"
        self.assertFalse(is_remote_version_newer(local, remote))

    def test_local_minor_older(self):
        local = "0.1.0"
        remote = "0.2.0"
        self.assertTrue(is_remote_version_newer(local, remote))

    def test_local_patch_newer(self):
        local = "0.0.2"
        remote = "0.0.1"
        self.assertFalse(is_remote_version_newer(local, remote))

    def test_local_patch_older(self):
        local = "0.0.1"
        remote = "0.0.2"
        self.assertTrue(is_remote_version_newer(local, remote))

    def test_local_patch_older_complex(self):
        local = "0.0.94"
        remote = "0.0.107"
        self.assertTrue(is_remote_version_newer(local, remote))

    def test_local_same_version(self):
        local = "1.1.35"
        remote = "1.1.35"
        self.assertFalse(is_remote_version_newer(local, remote))

    def test_no_period_delim(self):
        local = "1.1.35"
        remote = "1-1-35"
        with self.assertRaises(SystemExit):
            is_remote_version_newer(local, remote)

    def test_incorrect_version_length_short(self):
        local = "1.1"
        remote = "1.2.3"
        with self.assertRaises(SystemExit):
            is_remote_version_newer(local, remote)

    def test_incorrect_version_length_long(self):
        local = "1.1.1"
        remote = "1.2.3.4"
        with self.assertRaises(SystemExit):
            is_remote_version_newer(local, remote)
