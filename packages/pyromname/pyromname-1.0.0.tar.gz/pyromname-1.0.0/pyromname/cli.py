import argparse
import os
import pathlib
import shutil

import pyromname.crc
import pyromname.file
import pyromname.io
import pyromname.rom_database
import pyromname.rom_database_3dsdb
import pyromname.rom_database_dat
import pyromname.seven_zip
import pyromname.ui
import pyromname.zip

# pyromname.file.FileStatus.PARTIAL_SUCCESS
# => Le traitement de l'archive est un succès partiel. L'archive contient au moins une ROM reconnue.
# pyromname.file.FileStatus.SUCCESS
# => le traitement de l'archive est un succès: on peut supprimer. L'archive ne contient que des ROM reconnues.
# pyromname.file.FileStatus.FAILURE
# => l'archive ne contient aucune ROM reconnue.


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dat_dir", help="Datfiles directory")
    parser.add_argument("rom_dir", help="Rom directory")
    parser.add_argument("-l", "--limit", type=int, help="Process LIMIT files only")
    parser.add_argument(
        "-e", "--extract", help="Extract valid roms to EXTRACT directory"
    )
    parser.add_argument(
        "-c", "--compress", help="Zip extracted rom", action="store_true"
    )
    parser.add_argument("-a", "--compress-algorithm", help="Compression algorithm")
    parser.add_argument(
        "-m", "--move", help="Move rom to ok/ko sub folder", action="store_true"
    )
    parser.add_argument("-d", "--dry-run", help="Dry run mode", action="store_true")
    parser.add_argument(
        "-u", "--dump", help="Dump the list of CRC", action="store_true"
    )
    parser.add_argument("-k", "--check", help="Check rom_dir", action="store_true")
    parser.add_argument("-f", "--dat-format", help="Datfiles format")
    args = parser.parse_args()

    dat_dir = args.dat_dir
    rom_dir = args.rom_dir
    destination_dir = args.extract
    limit = args.limit
    move = args.move
    dry_run = args.dry_run
    compress = args.compress
    dump = args.dump
    check = args.check
    # rom_dir = destination_dir
    dat_format = args.dat_format
    compression_algorithm = pyromname.zip.CompressionAlgorithm.BZIP2

    if dat_format == "3dsdb":
        pyromname.ui.print_info("Dat format: 3dsdb")
        pyromname.file.File.rom_database = (
            pyromname.rom_database_3dsdb.RomDatabase3dsdb(dat_dir)
        )
    elif dat_format == "dat":
        pyromname.file.File.rom_database = pyromname.rom_database_dat.RomDatabaseDat(
            dat_dir
        )
    else:
        pyromname.ui.print_info("Dat format: no-intro / redump")
        pyromname.file.File.rom_database = pyromname.rom_database.RomDatabase(dat_dir)
    pyromname.file.File.rom_database.load()

    if compression_algorithm == "bzip2":
        compression_algorithm = pyromname.zip.CompressionAlgorithm.BZIP2
    elif compression_algorithm == "deflated":
        compression_algorithm = pyromname.zip.CompressionAlgorithm.DEFLATED
    elif compression_algorithm == "lzma":
        compression_algorithm = pyromname.zip.CompressionAlgorithm.LZMA

    ok_dir = os.path.join(rom_dir, "ok")
    ko_dir = os.path.join(rom_dir, "ko")
    err_dir = os.path.join(rom_dir, "err")
    ok_file = os.path.join(rom_dir, "crc.txt")

    if destination_dir:
        destination_dir = os.path.normpath(destination_dir)

    if move:
        pathlib.Path(ok_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(ko_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(err_dir).mkdir(parents=True, exist_ok=True)

    for path, _, files in os.walk(rom_dir):
        if path in [ok_dir, ko_dir, err_dir, destination_dir]:
            pyromname.ui.print_info(f"Skipping {path}")
            continue

        for filename in files:
            filepath = os.path.join(path, filename)

            # if not "0822" in file:
            #    continue

            if limit is not None:
                if limit == 0:
                    break
                limit = limit - 1

            if filepath.split(".")[-1] in pyromname.file.File.rom_database.extensions:
                archive_file = pyromname.file.SingleFile(
                    filepath
                )  # type: pyromname.file.File
            else:
                archive_file = pyromname.file.ArchiveFile(filepath)

            if not destination_dir:
                if check:
                    msg = f"Check {filepath}"
                    try:
                        status = archive_file.check()
                        if status == pyromname.file.FileStatus.SUCCESS:
                            pyromname.ui.print_success(msg)
                        elif status == pyromname.file.FileStatus.PARTIAL_SUCCESS:
                            pyromname.ui.print_partialsuccess(msg)
                        else:
                            pyromname.ui.print_failure(msg)
                    except pyromname.file.FileException as exception:
                        pyromname.ui.print_failure(msg)
                        pyromname.ui.print_failure(
                            f"  KO '{filepath}' {exception.message}."
                        )
                else:
                    msg = f"Listing {filepath}"
                    try:
                        (status, results) = archive_file.content
                        if status == pyromname.file.FileStatus.SUCCESS:
                            pyromname.ui.print_success(msg)
                        elif status == pyromname.file.FileStatus.PARTIAL_SUCCESS:
                            pyromname.ui.print_partialsuccess(msg)
                        else:
                            pyromname.ui.print_failure(msg)
                        for filename_in_archive, crc, name_in_db in results:
                            if name_in_db:
                                name, database = name_in_db
                                pyromname.ui.print_success(
                                    f"  OK '{filename_in_archive}' with CRC '{crc}' match '{name}' found in '{database}'."
                                )
                            else:
                                pyromname.ui.print_failure(
                                    f"  KO '{filename_in_archive}' with CRC '{crc}' not found."
                                )
                    except pyromname.file.FileException as exception:
                        pyromname.ui.print_failure(msg)
                        pyromname.ui.print_failure(
                            f"  KO '{filepath}' {exception.message}."
                        )
            else:
                msg = f"Extraction {filepath}"
                status = None
                try:
                    status, extract_results = archive_file.extract(destination_dir)
                    if status == pyromname.file.FileStatus.SUCCESS:
                        pyromname.ui.print_success(msg)
                    elif status == pyromname.file.FileStatus.PARTIAL_SUCCESS:
                        pyromname.ui.print_partialsuccess(f"{msg}")
                    else:
                        pyromname.ui.print_failure(msg)
                    for (
                        filename_in_archive,
                        crc,
                        name_in_db,
                        extracted_content,
                    ) in extract_results:
                        if name_in_db is None:
                            pyromname.ui.print_failure(
                                f"  KO '{filename_in_archive}' with CRC '{crc}' not found."
                            )
                        elif extracted_content is None:
                            pyromname.ui.print_failure(
                                f"  KO '{filename_in_archive}' with CRC '{crc}' failed to extract."
                            )
                        else:
                            name, database = name_in_db
                            pyromname.ui.print_success(
                                f"  OK '{filename_in_archive}' with CRC '{crc}' match '{name}' found in '{database}' extracted to '{extracted_content}'."
                            )
                except pyromname.file.FileException as exception:
                    pyromname.ui.print_failure(type(exception))
                    pyromname.ui.print_failure(msg)
                    pyromname.ui.print_failure(
                        f"  KO '{filepath}' {exception.message}."
                    )

                if move:
                    if status is None:
                        if not dry_run:
                            shutil.move(filepath, err_dir)
                        else:
                            pyromname.ui.print_info(
                                f"DRY-RUN Move file {filepath} to {err_dir}"
                            )
                    elif status == pyromname.file.FileStatus.SUCCESS:
                        if not dry_run:
                            shutil.move(filepath, ok_dir)
                        else:
                            pyromname.ui.print_info(
                                f"DRY-RUN Move file {filepath} to {ok_dir}"
                            )
                    elif status == pyromname.file.FileStatus.FAILURE:
                        if not dry_run:
                            shutil.move(filepath, ko_dir)
                        else:
                            pyromname.ui.print_info(
                                f"DRY-RUN Move file {filepath} to {ko_dir}"
                            )

    if compress:
        pyromname.ui.print_info(f"compress {rom_dir} {compression_algorithm}")
        for path, _, files in os.walk(rom_dir):
            for filename in files:
                file = os.path.join(path, filename)
                if file.split(".")[-1] in pyromname.file.File.rom_database.extensions:
                    pyromname.ui.print_info(f"Zip file {file}")
                    filezip = pyromname.zip.make_zip(file, compression_algorithm)
                    zip_is_good = pyromname.zip.test_zip(filezip)
                    if zip_is_good:
                        if not dry_run:
                            os.remove(file)
                        else:
                            pyromname.ui.print_info(f"DRY-RUN Remove file {file}")

    pyromname.file.File.rom_database.stats()
    if dump:
        pyromname.file.File.rom_database.dump_found_crc(ok_file)
