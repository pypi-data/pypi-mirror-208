""" Handle zip archives. """

import os
import shutil
import zipfile
from enum import IntEnum

import pyromname.io


class CompressionAlgorithm(IntEnum):
    DEFLATED = zipfile.ZIP_DEFLATED
    BZIP2 = zipfile.ZIP_BZIP2
    LZMA = zipfile.ZIP_LZMA


def make_zip(
    file: str, compression_algorithm: CompressionAlgorithm = CompressionAlgorithm.BZIP2
):
    """Create a zip with the file 'file'.
    The file name is the original file name.
    The name of the file in the archive is the name of the original file.

    Args:
        file (str): the file to compress.

    Returns:
        str: the new zip file.
    """

    original_filename = os.path.basename(pyromname.io.get_original_filename(file))
    (name, _) = os.path.splitext(original_filename)
    destination_dir = os.path.dirname(file)
    filezip = pyromname.io.get_destination_filename(
        destination_dir, f"{name}.{compression_algorithm}.zip"
    )

    # cf. https://medium.com/dev-bits/ultimate-guide-for-working-with-i-o-streams-and-zip-archives-in-python-3-6f3cf96dca50

    # Alternative version to set metadata
    # zinfo = zipfile.ZipInfo.from_file(file, original_filename)
    # zinfo.compress_type = zipfile.ZIP_DEFLATED
    # zinfo.date_time = (1980, 1, 1, 0, 0, 0)
    # zinfo._compresslevel = 9
    # with zipfile.ZipFile(filezip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as myzip:
    #    with open(file, "rb") as src, myzip.open(zinfo, "w") as dest:
    #        shutil.copyfileobj(src, dest, 1024 * 8)

    with zipfile.ZipFile(
        filezip, "w", int(compression_algorithm), compresslevel=9, allowZip64=True
    ) as zip_archive:
        with open(file, "rb") as src, zip_archive.open(
            original_filename, "w", force_zip64=True
        ) as file1:
            shutil.copyfileobj(src, file1, 1024 * 8)

    return filezip


def test_zip(filezip: str) -> bool:
    """Test zip file 'filezip'.

    Args:
        filezip (str): the zip file to test.

    Returns:
        bool: True only if 'filezip' is valid.
    """

    zip_is_good = False
    with zipfile.ZipFile(filezip, "r") as myzip:
        if myzip.testzip() is None:
            zip_is_good = True
    return zip_is_good
