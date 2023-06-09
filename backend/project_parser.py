import uuid
import os
from typing import Optional
from dataclasses import dataclass
import configparser
import re
import logging
from typing import Dict
from backend.schematic import Schematic
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
@dataclass
class ProjectFile:
    name: str
    exists: bool
    path: str

class Project:
    def __init__(self, root_folder) -> None:
        self.ready = False
        self.root = Path(root_folder)
        self.parser = configparser.ConfigParser()
        self.schematics: Dict[str, Schematic] = {}
        self.variants = {}
        self.variant_uid_map = {}
        project_paths = [p for p in os.listdir(self.root) if p.lower().endswith(".prjpcb")]
        if len(project_paths) == 0:
            raise FileNotFoundError(f"No project found in directory: {self.root}")
        self.path = project_paths[0]
    
    def read(self) -> None:
        full_path = self.root / Path(self.path)
        logging.info(f"Reading project file: {full_path}")
        with open(full_path, "r", encoding="ascii", errors="ignore") as f:
            content = f.read()
            self.parser.read_string(content)
            self.ready = True
        return self

    def get_schematics(self):
        if not self.ready:
            self.read()
        schematics = []
        for key, value in self.parser.items():
            if "Document" not in key:
                continue
            name, extension = os.path.splitext(value["documentpath"])
            if extension != ".SchDoc":
                continue
            exists = os.path.exists(self.root / value["documentpath"])
            schematics.append(ProjectFile(name, exists, value["documentpath"]))
        return schematics
    
    def get_variants(self):
        ALT_REGEX = r"Designator=([^\|]+).*?AlternatePart=(.*?)"
        PARAM_REGEX = r"ParameterName=(.*?)\|VariantValue=(.*)"
        if not self.ready:
            self.read()
        self.variants.clear()
        self.variants["[No Variation]"] = {}
        for heading, content in self.parser.items():
            if "ProjectVariant" not in heading:
                continue
            variant = content["Description"]
            self.variants[variant] = {}
            for i in range(1, int(content.get("VariationCount", 0))):
                match = re.search(ALT_REGEX, content[f"Variation{i}"])
                refdes, altpart = match.groups()
                self.variants[variant][refdes] = {}
                if not altpart.strip():
                    continue
                self.variants[variant][refdes]['name'] = altpart
            for i in range(1, int(content.get("ParamVariationCount", 0))):
                match = re.search(PARAM_REGEX, content[f"ParamVariation{i}"])
                name, value = match.groups()
                self.variants[variant][refdes][name] = value
        return self.variants

    def get_variant_names(self):
        if self.variant_uid_map:
            return self.variant_uid_map
        self.get_variants()
        for key, _ in self.variants.items():
            if key == "[No Variation]":
                self.variant_uid_map["default"] = key
                continue
            self.variant_uid_map[str(uuid.uuid4())] = key
        return self.variant_uid_map

    def get_schematic_json(self, path: str) -> Schematic:
        if not self.ready:
            self.read()
        filepath = f"{self.root}/{path}.SchDoc"
        self.schematics[path] = Schematic().read(filepath)
        return self.schematics[path]
    
    def get_image(self, schematic: str, path: str):
        sch = self.schematics[schematic]
        if sch.storage.get(path):
            return sch.storage.get(path)
        return sch.storage.get(path.replace("\\\\", "\\"))


if __name__ == "__main__":
    p = Project("designs/Altium P-MT3620RDB-1-0")
    p.read()
    print(p.get_schematic_as_base64(p.get_schematics()[0]))
            

