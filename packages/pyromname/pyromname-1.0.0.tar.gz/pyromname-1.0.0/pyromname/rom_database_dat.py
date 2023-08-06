import os
import re
from collections import defaultdict

import pyromname.rom_database


class RomDatabaseDat(pyromname.rom_database.RomDatabase):
    def load(self) -> None:
        for dat_file in [
            os.path.join(self.dat_dir, f)
            for f in os.listdir(self.dat_dir)
            if os.path.isfile(os.path.join(self.dat_dir, f))
        ]:
            self._xml_files.append(dat_file)
            self.crc_found[dat_file] = defaultdict(set)
            self._crc[dat_file] = set()
            with open(dat_file, encoding="utf-8") as filep:
                for line in filep.readlines():
                    rom_match = re.search(r"rom \( (.*)\)", line)
                    if rom_match:
                        rom_infos_str = rom_match.group(1)
                        rom_infos = re.findall(
                            r'(\w+) (?:"([^"]+)"|(\w+))', rom_infos_str
                        )
                        infos = {}
                        for key, quoted_value, value in rom_infos:
                            infos[key] = quoted_value if quoted_value else value
                        name = infos["name"]
                        # 0-Ji no Kane to Cinderella - Halloween Wedding (Japan) (v1.01).iso
                        name = re.sub(r"(.*)?( \(v\d+\.\d+\))", "\\g<1>", name)
                        crc = infos["crc"].upper()
                        _, file_extension = os.path.splitext(name)
                        self.extensions.add(file_extension)
                        self.names[crc] = (name, dat_file)
                        self._crc[dat_file].add(crc)
