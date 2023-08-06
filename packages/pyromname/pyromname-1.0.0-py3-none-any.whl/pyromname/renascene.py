import argparse
import os
import re
import urllib.request
import zlib

import pyromname.ui


def crc(filename):
    """Renvoie le CRC du fichier."""

    prev = 0
    for line in open(filename, "rb"):
        prev = zlib.crc32(line, prev)
    return f"{prev & 0xFFFFFFFF:08X}"


def get_info(renascene_id):
    """Retourne un dictionnaire contenant les informations Renascene à partir de l'ID."""

    with urllib.request.urlopen(
        f"https://renascene.com/ps1/info/{renascene_id}"
    ) as response:
        html = response.read()
        html_decoded = html.decode()
        regex_title = r"<h1>(.*)<\/h1>"
        rep_title = re.findall(regex_title, html_decoded)
        regex_info = r'<tr><td class="infLeftTd">(.*)<\/td><td class="infRightTd">(.*)<\/td><\/tr>'
        rep_info = re.findall(regex_info, html_decoded)
        info = dict(rep_info)
        info["Title"] = rep_title[0]
        regex_key = r'href="([^"]+)"'
        rep_key = re.findall(regex_key, info["KEYS.BIN"])
        url = rep_key[0].replace("&amp;", "&")
        url = f"https:{url}"
        key_content = urllib.request.urlopen(url).read()
        info["KEYS.BIN"] = key_content

        rep_region_duplicates = re.findall(
            r'<tr class="dupTRSel">(.*?)</tr>', html_decoded
        )
        rep_region = re.findall(r"<td[^>]+?>(.*?)<\/td>", rep_region_duplicates[0])

        info["ID"] = rep_region[0]
        info["Region"] = rep_region[1]
        info["Country"] = rep_region[2]
        info["Tilte2"] = rep_region[3]
        info["SerialNumberPS1"] = rep_region[4]
        info["SerialNumber"] = rep_region[5]

        return info


def get_id(serial_number):
    """Retourne les ID renascene trouvés à partir du numéro de série."""

    with urllib.request.urlopen(
        f"https://renascene.com/ps1/?target=search&srch={serial_number}&srchser=1"
    ) as response:
        html = response.read()
        html_decoded = html.decode()
        ids = []
        responses = re.findall(r'<tr class="defRows "[^>]+>(.*?)</tr>', html_decoded)
        for response in responses:
            tds = re.split(r"(?:</td>)(?:<td[^>]*)>", response)
            ids.append(tds[1])
        return ids
    return None


def get_local_info(dirname):
    """Retourne les informations 'locales' à partir du répertoire.
    Calcul les CRC des fichiers suivant:
    - CRC EBOOT.PBP
    - CRC DOCUMENT.DAT
    """

    local_crc = {}
    files = "EBOOT.PBP", "DOCUMENT.DAT"
    for file in files:
        filename = os.path.join(dirname, file)
        if os.path.isfile(filename):
            local_crc[file] = crc(filename)
        else:
            local_crc[file] = None

    return local_crc


def check(renascene_id, dirname):
    """Vérifie que le répertoire contient bien le jeu correspondant à l'identifiant Renascene."""

    pyromname.ui.print_info(f"Check {renascene_id} in {dirname} ...", end="")

    local_crc = get_local_info(dirname)
    renascene_info = get_info(renascene_id)

    if renascene_info["CRC32 (EBOOT.PBP)"] != local_crc["EBOOT.PBP"]:
        pyromname.ui.print_failure(": KO")
        pyromname.ui.print_failure(
            f'CRC32 (EBOOT.PBP) is not the same (\'{local_crc["EBOOT.PBP"]}\' vs \'{renascene_info["CRC32 (EBOOT.PBP)"]}\')'
        )
        if local_crc["EBOOT.PBP"] is None:
            pyromname.ui.print_failure("EBOOT.PBP is missing")
        return False, renascene_info

    if renascene_info["CRC32 (DOCUMENT.DAT)"] != local_crc["DOCUMENT.DAT"]:
        pyromname.ui.print_failure(": KO")
        pyromname.ui.print_failure(
            f'CRC32 (DOCUMENT.DAT) is not the same (\'{local_crc["DOCUMENT.DAT"]}\' vs \'{renascene_info["CRC32 (DOCUMENT.DAT)"]}\')'
        )
        if local_crc["DOCUMENT.DAT"] is None:
            pyromname.ui.print_failure("DOCUMENT.DAT is missing")
        return False, renascene_info

    filename = os.path.join(dirname, "KEYS.BIN")
    if os.path.isfile(filename):
        key_content = open(filename, "rb").read()
    else:
        key_content = None

    if renascene_info["KEYS.BIN"] != key_content:
        pyromname.ui.print_failure(": KO")
        pyromname.ui.print_failure("'KEYS.BIN' is not the same")
        return False, renascene_info

    pyromname.ui.print_success(": OK")
    return True, renascene_info


def rename(base_dir, actual_dir, renascene_info, subdir, dry_run=True):
    """Renomme le répertoire contenant le jeu avec les informatoins Renascene."""

    title_re = re.search(r"^([^\(]+)(?: \(([^\)]+)\))?$", renascene_info["Title"])
    if title_re:
        title = title_re.group(1)
        title_complement = title_re.group(2)
        if title_complement:
            title_complement = f" ({title_complement})"
        else:
            title_complement = ""
    name = f"{renascene_info['ID']} - {title} [{renascene_info['SerialNumber']}] [{renascene_info['Region']}]{title_complement}"
    name = name.replace(":", " -")
    if actual_dir != name:
        subdir = renascene_info["SerialNumberPS1"].replace("-", "")
        if not dry_run:
            os.mkdir(os.path.join(base_dir, name))
            os.rename(
                os.path.join(base_dir, actual_dir), os.path.join(base_dir, name, subdir)
            )
            pyromname.ui.print_partialsuccess(
                f"rename '{actual_dir}' to '{name}/{subdir}'"
            )
        else:
            pyromname.ui.print_partialsuccess(
                f"DRY-RUN rename '{actual_dir}' to '{name}/{subdir}'"
            )
    else:
        pyromname.ui.print_success(f"{actual_dir} is great !!")


def renacheck(dirname):
    """Vérifie la validité des jeux contenus dans le répertoire."""

    for _, dirnames, _ in os.walk(dirname):
        for subdirname in dirnames:
            good = False
            id_match = re.search(
                r"^(\d+) - ((?:[\w '\-\d])+) \[([^\]]+)\] \[([^\]]+)\](?: \(([^\)]+)\))?$",
                subdirname,
            )
            if id_match:
                # Le répertoire correspond au format suivant:
                # {renascene_id} - {name} [{serial_number}] [{region}] {name_complement}
                # Par exemple, 0523 - Castlevania - Symphony of the Night [NPEF-00051] [EU] (French Store Dump)
                renascene_id = id_match.group(1)
                name = id_match.group(2)
                serial_number = id_match.group(3)
                region = id_match.group(4)
                name_complement = id_match.group(5)

                renascene_info = get_info(renascene_id)
                subdir = os.path.join(
                    subdirname, renascene_info["SerialNumberPS1"].replace("-", "")
                )

                (status, renascene_info) = check(
                    renascene_id, os.path.join(dirname, subdir)
                )

                if status:
                    rename(dir, subdirname, renascene_info, subdir)
                    good = True
                else:
                    pyromname.ui.print_failure("KOKO")
                    continue
            else:
                pyromname.ui.print_info(f"{subdirname} is not matching.")
                serial_number_match = re.search(r"(\w{4}\d{5})", subdirname)
                if serial_number_match:
                    # Le répertoire contient un numéro de série.
                    serial_number = serial_number_match.group(1)
                    pyromname.ui.print_info(
                        f"Search with serial number '{serial_number}'."
                    )
                    ids = get_id(serial_number)
                    subdir = ""
                    for renascene_id in ids:
                        pyromname.ui.print_info(f"Try with {renascene_id}")
                        (status, renascene_info) = check(
                            renascene_id, os.path.join(dirname, subdirname)
                        )
                        if status:
                            rename(dir, subdirname, renascene_info, subdir)
                            good = True
                            break
                        else:
                            pyromname.ui.print_info("Need to try with another ...")
                else:
                    pyromname.ui.print_failure("KOKO")

            if not good:
                pyromname.ui.print_failure(f"{subdirname} is not valid.")

        break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("rom_dir", help="Rom directory")
    args = parser.parse_args()
    rom_dir = args.rom_dir
    renacheck(rom_dir)
