import unittest
from pprint import pprint

from sf2.args import get_args



class TestArgs(unittest.TestCase):

    # def test_help(self):
    #     # args = get_args(["encrypt", "--help"])
    #     args = get_args(["ssh", "--help"])

    # encrypt

    def test_encrypt_mk(self):
        args = get_args(["encrypt", "-i", "in.txt", "-o", "out.x"])
        results = [args.infilename, args.outfilename]
        expected = ["in.txt", "out.x"]

        self.assertEqual(results, expected)

    def test_encrypt_format(self):
        args = get_args(["encrypt", "--format", "json", "-m", "foobar", "-i", "in.txt", "-o", "out.x"])
        results = [args.infilename, args.outfilename, args.format, args.password]
        expected = ["in.txt", "out.x", "json", "foobar"]

        self.assertEqual(results, expected)

    # decrypt

    def test_decrypt_mk(self):
        args = get_args(["decrypt", "--password", "-i", "in.txt", "-o", "out.x"])
        results = [args.infilename, args.outfilename, args.password_method, args.ssh_method]
        expected = ["in.txt", "out.x", True, False]

        self.assertEqual(results, expected)

    def test_decrypt_mk_with_master_password(self):
        args = get_args(["decrypt", "--password", "-m", "foobar", "-w", "-i", "in.txt", "-o", "out.x"])
        results = [args.infilename, args.outfilename, args.password_method, args.password, args.allow_weak_password]
        expected = ["in.txt", "out.x", True, "foobar", True]

        self.assertEqual(results, expected)

    def test_decrypt_ssh_key_no_file(self):
        args = get_args(["decrypt", "--ssh", "-i", "in.txt", "-o", "out.x"])
        results = [args.infilename, args.outfilename, args.ssh_method]
        expected = ["in.txt", "out.x", True]

        self.assertEqual(results, expected)

    def test_decrypt_ssh_key_with_file(self):
        args = get_args(["decrypt", "--ssh", "-y", "/home/foo/.ssh/id_rsa", "-K", "foobar", "-i", "in.txt", "-o", "out.x"])
        results = [args.infilename, args.outfilename, args.ssh_method, args.private_key_file, args.private_key_password]
        expected = ["in.txt", "out.x", True, "/home/foo/.ssh/id_rsa", "foobar"]

        self.assertEqual(results, expected)

    # # # convert
    def test_decrypt_mk(self):
        args = get_args(["convert", "-i", "in.y", "-o", "out.x"])
        results = [args.infilename, args.outfilename]
        expected = ["in.y", "out.x"]
        self.assertEqual(results, expected)

    # # # open
    def test_open_mk(self):
        args = get_args(["open", "--password", "--program", "nano",  "out.x"]) 
        results = [args.commands, args.infilenames, args.password_method, args.program]
        expected = ['open', ['out.x'], True, 'nano']

        self.assertEqual(results, expected)

    def test_open_ssh_key_no_file(self):
        args = get_args(["open", "--ssh", "--program", "nano",  "out.x"]) 
        results = [args.commands, args.infilenames, args.ssh_method, args.program, args.private_key_file]
        expected = ['open', ['out.x'], True, 'nano', None]

        self.assertEqual(results, expected)

    def test_open_ssh_key_with_file(self):
        args = get_args(["open", "--ssh", "-y", ".ssh/id_rsa", "--program", "nano",  "out.x"]) 
        results = [args.commands, args.infilenames, args.ssh_method, args.program, args.private_key_file]
        expected = ['open', ['out.x'], True, 'nano', ".ssh/id_rsa"]

        self.assertEqual(results, expected)

    # # Currently disable, need to implement configuration
    # # def test_open_without_args(self):
    # #     args = get_args(["open", "out.x"]) 
    # #     results = [args.commands, args.infilename, args.password_method, args.program, args.ssh_method]
    # #     expected = ['open', ['out.x'], False, None, None]

    # #     self.assertEqual(results, expected)

    # verify
    def test_verify_mk(self):
        args = get_args(["verify", "--password",  "out.x"]) 
        results = [args.commands, args.infilenames, args.password_method]
        expected = ['verify', ['out.x'], True]

        self.assertEqual(results, expected)

    def test_verify_ssh_key_no_file(self):
        args = get_args(["verify", "--ssh", "out.x"]) 
        results = [args.commands, args.infilenames, args.ssh_method]
        expected = ['verify', ['out.x'], True]

        self.assertEqual(results, expected)

    def test_verify_ssh_key_with_file(self):
        args = get_args(["verify", "--ssh", "-y", ".ssh/id_rsa", "out.x"]) 
        results = [args.commands, args.infilenames, args.ssh_method, args.private_key_file]
        expected = ['verify', ['out.x'], True, ".ssh/id_rsa"]

        self.assertEqual(results, expected)

    # # ssh add
    def test_ssh_add_all(self):
        args = get_args(["ssh", "add", "-k", ".ssh/id_rsa.pub", "-a", "foo@bar", "out.x"]) 
        results = [args.commands, args.ssh_commands, args.public_key_file, args.auth_id, args.infilenames]
        expected = ['ssh', "add", ".ssh/id_rsa.pub", "foo@bar", ["out.x"]]

        self.assertEqual(results, expected)

    def test_ssh_add_default(self):
        args = get_args(["ssh", "add", "out.x"]) 
        results = [args.commands, args.ssh_commands, args.public_key_file, args.auth_id, args.infilenames]
        expected = ['ssh', "add", None, None, ["out.x"]]

        self.assertEqual(results, expected)

    # ssh rm
    def test_ssh_rm(self):
        args = get_args(["ssh", "rm", "-p", "foo@bar", "out.x"]) 
        results = [args.commands, args.ssh_commands, args.auth_id_pattern, args.infilenames]
        expected = ['ssh', "rm", "foo@bar", ["out.x"]]

        self.assertEqual(results, expected)

    # ssh ls
    def test_ssh_ls(self):
        args = get_args(["ssh", "ls", "out.x"]) 
        results = [args.commands, args.ssh_commands, args.infilenames]
        expected = ['ssh', "ls",  ["out.x"]]

        self.assertEqual(results, expected)