import unittest
from update_discord import is_version_newer

# <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>Redirecting...</title>\n<h1>Redirecting...</h1>\n<p>You should be redirected automatically to target URL: <a href="https://stable.dl2.discordapp.net/apps/linux/0.0.107/discord-0.0.107.deb">https://stable.dl2.discordapp.net/apps/linux/0.0.107/discord-0.0.107.deb</a>.  If not click the link.


class TestVersionComparison(unittest.TestCase):
    def test_major_newer(self):
        a = "2.0.0"
        b = "1.0.0"
        self.assertTrue(is_version_newer(a, b))

    def test_major_older(self):
        a = "1.0.0"
        b = "2.0.0"
        self.assertFalse(is_version_newer(a, b))

    def test_minor_newer(self):
        a = "0.2.0"
        b = "0.1.0"
        self.assertTrue(is_version_newer(a, b))

    def test_minor_older(self):
        a = "0.1.0"
        b = "0.2.0"
        self.assertFalse(is_version_newer(a, b))

    def test_patch_newer(self):
        a = "0.0.2"
        b = "0.0.1"
        self.assertTrue(is_version_newer(a, b))

    def test_patch_older(self):
        a = "0.0.1"
        b = "0.0.2"
        self.assertFalse(is_version_newer(a, b))

    def test_patch_older_complex(self):
        a = "0.0.94"
        b = "0.0.107"
        self.assertTrue(is_version_newer(a, b))

    def test_same_version(self):
        a = "1.1.35"
        b = "1.1.35"
        self.assertTrue(is_version_newer(a, b))
