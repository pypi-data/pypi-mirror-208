from tempfile import mkstemp
import os
from threading import Thread
import logging
import re

import inotify.adapters
from flufl.lock import Lock
from flufl.lock import TimeOutError

RAMFS = "/dev/shm"

# The `OpenInRAM` class is a Python class that provides methods for encrypting and decrypting files,
# running commands on them, and monitoring changes to the files.
class OpenInRAM:
    def __init__(self, file_object, command:str):
        """
        This is the constructor for a class that takes a file object and a command string as arguments,
        initializes some instance variables, and logs some debug information.
        
        :param file_object: The file object is a reference to a file that the code will read from or
        write to. It could be a file on the local file system or a network file
        :param command: The `command` parameter is a string that represents a command to be executed. It
        is passed to the `interpole_command` method to replace any placeholders with actual values
        before being executed
        :type command: str
        """
        
        self._file_object = file_object
        self._log = logging.getLogger(f"{self.__class__.__name__}({file_object})")
        self._running = False

        self._command = self.interpole_command(command)
        self._log.debug(f"Command : {self._command}")

    def interpole_command(self, command:str)->str:
        """
        This function checks if a given command string contains the word "filename" and adds it if it
        doesn't, or replaces it with "{filename}" if it does.
        
        :param command: The input command string that needs to be checked and modified if necessary
        :type command: str
        :return: a string that includes the placeholder "{filename}" if the input command does not
        already contain it. If the input command already contains the placeholder, the function returns
        the command with the placeholder formatted as "{filename}".
        """
        command = command.strip()
        if re.search(r"[\{\[]\s*filename\s*[\}\]]", command) is None:
            return command + " {filename}"
        else:
            command = re.sub(r"[\[]\s*filename\s*[\]]", "{filename}", command)
            return command
        
    def on_write_inotify_thread(self, source_path:str, destination_path:str, callback:callable):
        """
        This function uses inotify to monitor a source directory for changes and calls a callback
        function when a file is written to the destination directory.
        
        :param source_path: The path of the directory being watched for changes
        :type source_path: str
        :param destination_path: The `destination_path` parameter is a string that represents the path
        of the destination file or directory where the contents of the source file or directory will be
        copied to
        :type destination_path: str
        :param callback: The `callback` parameter is a callable function that will be executed when a
        file is written to the `source_path` directory. The `destination_path` parameter is passed as an
        argument to the `callback` function
        :type callback: callable
        :return: nothing explicitly, but it will return implicitly if the condition `if not
        self._running` is met. In that case, the function will exit and return control to the calling
        function.
        """
        i = inotify.adapters.Inotify()

        i.add_watch(source_path)

        for event in i.event_gen():

            if not self._running:
                return

            if event is not None:
                (_, type_names, _, _) = event

                if "IN_CLOSE_WRITE" in type_names:
                    callback(destination_path)

    def write_back_callback(self, file_to_encrypt:str):
        """
        This function encrypts a given file and logs the result, or logs an error if the file is not
        found.
        
        :param file_to_encrypt: file_to_encrypt is a string parameter that represents the file path of
        the file that needs to be encrypted
        :type file_to_encrypt: str
        """
        try:
            self._file_object.encrypt(file_to_encrypt)
            self._log.debug(f"Sync plain ({file_to_encrypt}) to encrypted")
        except FileNotFoundError as e:
            self._log.debug(f"No Sync plain ({file_to_encrypt}) : {e}")

    def read_back_callback(self, plain_text_path:str):
        """
        This function reads a decrypted file and writes it to a plain text file with restricted
        permissions.
        
        :param plain_text_path: The parameter `plain_text_path` is a string that represents the file
        path where the decrypted data will be written to
        :type plain_text_path: str
        """
        decrypted = self._file_object.decrypt()
        try:
            os.chmod(plain_text_path, 0o600)
            with open(plain_text_path, 'wb') as f:
                f.write(decrypted)
                f.flush()
            os.chmod(plain_text_path, 0o400)
            self._log.debug(f"Sync plain ({plain_text_path}) from encrypted")
        except Exception as e:
            self._log.warning(f"Failed to sync : {e}")

    def run_write(self):
        """
        This function decrypts a file, creates a temporary file, writes the decrypted content to the
        temporary file, monitors changes to the temporary file, runs a command using the temporary file
        as input, and then removes the temporary file.
        """
        decrypted = self._file_object.decrypt()

        try:
            fd, path = mkstemp(dir=RAMFS, suffix=".plain")
            self._log.debug(f"Create tmp file {path} (fd={fd})")
            with os.fdopen(fd, 'wb') as f:
                f.write(decrypted)
                f.flush()

                # Run a thread that monitor file change.
                # This way, modification are automatically write back to the encrypted file
                self._running = True
                write_back_thread = Thread(target=self.on_write_inotify_thread, args=(path,path, self.write_back_callback))
                write_back_thread.start()

                command = self._command.format(filename=path)
                self._log.debug(f"Run command : {command}")
                os.system(command)
            
        except Exception as e:
            self._log.error(f"Something failed : {e}")
        finally:
            self._log.debug(f"Tmp file {path} safely remove")
            os.unlink(path)
            # stopping the thread
            self._running = False

    def run_read(self):
        """
        This function reads a decrypted file, creates a temporary file, runs a command on the temporary
        file, and monitors changes to the temporary file.
        """
        decrypted = self._file_object.decrypt()

        try:
            # This code is creating a temporary file in the RAMFS directory with a ".plain" suffix.
            # The `mkstemp()` function returns a tuple containing a file descriptor and the path to
            # the created file. The file descriptor is then used to open the file using `os.fdopen()`,
            # and the decrypted content is written to the file. The `flush()` method is called to
            # ensure that all data is written to the file. The file is then made read-only using
            # `os.chmod()` with a permission of 0o400.
            fd, path = mkstemp(dir=RAMFS, suffix=".plain")
            self._log.debug(f"Create tmp file {path} (fd={fd})")
            with os.fdopen(fd, 'wb') as f:
                f.write(decrypted)
                f.flush()
            self._log.debug(f"Tmp file {path} is now read only")
            os.chmod(path, 0o400)

            # Run a thread that monitor file change.
            # This way, modification are automatically write back to the encrypted file
            self._running = True
            read_back_thread = Thread(target=self.on_write_inotify_thread, args=(str(self._file_object), path, self.read_back_callback))
            read_back_thread.start()

            command = self._command.format(filename=path)
            self._log.debug(f"Run command : {command}")
            os.system(command)
            
        except Exception as e:
            self._log.error(f"Something failed : {e}")
        finally:
            self._log.debug(f"Tmp file {path} safely remove")
            os.unlink(path)
            # stopping the thread
            self._running = False


    def run(self):
        """
        This function runs a file in read or write mode depending on whether it is locked or not.
        """
        # Remove logs from inotify
        logging.getLogger('inotify.adapters').setLevel(logging.WARNING)

        filename = str(self._file_object)
        lock_file = filename + ".lock"

        try:
            with Lock(lock_file, default_timeout=0):
                self._log.debug(f"File opened in R/W")
                self.run_write()
        except TimeOutError:
            self._log.debug(f"File opened in RO")
            self.run_read()
