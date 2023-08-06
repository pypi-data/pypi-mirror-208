import os
from collections import defaultdict

import defusedxml.ElementTree as ET

import pyromname.rom_database


class RomDatabase3dsdb(pyromname.rom_database.RomDatabase):
    def load(self) -> None:
        for dat_file in [
            os.path.join(self.dat_dir, f)
            for f in os.listdir(self.dat_dir)
            if os.path.isfile(os.path.join(self.dat_dir, f))
        ]:
            self._xml_files.append(dat_file)
            self.crc_found[dat_file] = defaultdict(set)
            self._crc[dat_file] = set()
            xml_root = ET.parse(dat_file).getroot()
            for rom in xml_root.findall(".//release"):
                name = rom.find("name").text
                rom_id = int(rom.find("id").text)
                if not rom.find("imgcrc").text:
                    print(f"Skip rom '{name}' with empty CRC.")
                    continue
                crc = rom.find("imgcrc").text.upper()
                ext = "3ds"
                self.extensions.add(ext)
                self.names[crc] = (
                    f"{rom_id:04} - {name}.{ext}",
                    dat_file,
                )
                self._crc[dat_file].add(crc)
