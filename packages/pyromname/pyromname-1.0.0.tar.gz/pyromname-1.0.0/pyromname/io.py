import os
import re
import shutil


def get_destination_filename(destination_dir, destination_filename, number=0):
    filename = destination_filename
    if number > 0:
        (name, ext) = os.path.splitext(destination_filename)
        filename = f"{name}_{number}{ext}"
    destination_file = os.path.join(destination_dir, filename)
    if os.path.exists(destination_file):
        number = number + 1
        return get_destination_filename(destination_dir, destination_filename, number)
    else:
        return destination_file


def get_original_filename(filename):
    (_, ext) = os.path.splitext(filename)
    return re.sub(f"(_\\d+){ext}$", f"{ext}", filename)


def move_to_dir(file, destination_dir, destination_filename):
    shutil.move(file, get_destination_filename(destination_dir, destination_filename))


def copy_to_dir(file, destination_dir, destination_filename):
    shutil.copy(file, get_destination_filename(destination_dir, destination_filename))
