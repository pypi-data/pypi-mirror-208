import os
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

import defusedxml.ElementTree as ET


class RomDatabase:
    def __init__(self, dat_dir: str):
        self.dat_dir: str = dat_dir
        self._xml_files: List[str] = []
        self.crc_found: Dict[str, Dict[str, Set[str]]] = {}
        self._crc: Dict[str, Set[str]] = {}
        self.extensions: Set[str] = set()
        self.names: Dict[str, Tuple[str, str]] = {}

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
            for rom in xml_root.findall(".//rom"):
                crc = rom.get("crc").upper()
                name = rom.get("name")
                ext = name.split(".")[-1].lower()
                self.extensions.add(ext)
                self.names[crc] = (name, dat_file)
                self._crc[dat_file].add(crc)

    def name_by_crc(self, crc: str, source_file: str) -> Optional[Tuple[str, str]]:
        name_in_db = self.names.get(crc)
        if name_in_db:
            _, db = name_in_db
            self.crc_found[db][crc].add(os.path.basename(source_file))
        print(f"{crc} => {name_in_db}")
        return name_in_db

    def dbs(self) -> None:
        pass

    def info(self) -> Dict[str, Tuple[int, int]]:
        dict_info = {}
        for xml in self._xml_files:
            dict_info[xml] = (len(self._crc[xml]), len(self.crc_found[xml].keys()))
        return dict_info

    def stats(self) -> None:
        print()
        print("Rom founds:")
        for xml in self._xml_files:
            print(
                f"{xml} total {len(self._crc[xml])} found {len(self.crc_found[xml].keys())}"
            )

    def dump_found_crc(self, file: str) -> None:
        with open(file, "w+", encoding="utf-8") as writer:
            for xml in self._xml_files:
                for crc in sorted(self.crc_found[xml].keys()):
                    source_files = "".join(self.crc_found[xml][crc])
                    writer.write(f"{crc} {source_files}\n")
