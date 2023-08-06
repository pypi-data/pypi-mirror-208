import os
import subprocess
import tempfile

import pyromname.io


class SevenZipException(Exception):
    def __init__(self, command, message):
        self.command = command
        self.message = message

        super().__init__(self.message)


class SevenZipErrorException(SevenZipException):
    def __init__(self, command, error):
        lines = error.splitlines()
        errors_msg = None
        error_msg = []
        for index, line in enumerate(lines):
            if line.startswith("ERRORS:"):
                errors_msg = f"{line[8:]}{lines[index+1]}"
            if line.startswith("ERROR:"):
                if index < len(lines) - 1:
                    next_line = lines[index + 1]
                    if not next_line.startswith("ERROR:"):
                        error_msg.append(f"{line[7:]} {next_line}")
                else:
                    error_msg.append(line[7:])
        msg = None
        if len(error_msg) == 1:
            msg = f"{error_msg[0]}"
        else:
            msg = f"({'/'.join(error_msg)})"
        if errors_msg:
            message = f"{errors_msg} {msg}"
        else:
            message = f"{msg}"

        super().__init__(command, message)


class SevenZipEmptyException(SevenZipException):
    def __init__(self, command):
        super().__init__(command, "Archive is empty.")


class SevenZipMissingCRCException(SevenZipException):
    def __init__(self, command):
        super().__init__(command, "Archive does not contains CRC.")


class SevenZip:
    def __init__(self, file):
        self.file = file

    def cmd(self, cmd):
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=-1,
            encoding="utf-8",
        )
        output, error = process.communicate()
        if process.returncode == 0:
            return output
        else:
            raise SevenZipErrorException(" ".join(cmd), error)

    def content(self):
        cmd = ["7z", "l", "-slt", f"{self.file}", "-sccUTF-8"]
        path = []
        crc = []
        output = self.cmd(cmd)
        first_path = True
        for line in output.splitlines():
            if line.startswith("Path = "):
                if first_path:
                    first_path = False
                else:
                    path.append(line.rstrip("\n").replace("Path = ", ""))
            if line.startswith("CRC = "):
                crc.append(line.rstrip("\n").replace("CRC = ", ""))

        if len(path) == 0:
            raise SevenZipEmptyException(" ".join(cmd))
        if len(crc) == 0:
            raise SevenZipMissingCRCException(" ".join(cmd))

        return list(zip(path, crc))

    def test(self):
        cmd = ["7z", "t", f"{self.file}", "-sccUTF-8"]
        _ = self.cmd(cmd)
        return True

    def extract_to_specific_filename(
        self, filename_to_extract, destination_dir, destination_filename
    ):
        with tempfile.TemporaryDirectory() as tmpdirname:
            cmd = [
                "7z",
                "e",
                f"-o{tmpdirname}",
                f"{self.file}",
                f"{filename_to_extract}",
                "-aou",
                "-sccUTF-8",
            ]
            _ = self.cmd(cmd)
            extracted_file = os.path.join(
                tmpdirname, os.path.basename(filename_to_extract)
            )
            pyromname.io.move_to_dir(
                extracted_file, destination_dir, destination_filename
            )
            return True
