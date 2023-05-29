import base64
import os
from typing import Optional
from dataclasses import dataclass
import configparser
import glob
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
        self.variants = []
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
        if not self.ready:
            self.read()
        self.variants.clear()
        for key, value in self.parser.items():
            if "ProjectVariant" not in key:
                continue
            variant = value["Description"]
            self.variants.append(variant)
        self.variants.append("[No Variation]")
        return self.variants

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
    p = Project("FPGA1394")
    p.read()
    print(p.get_schematic_as_base64(p.get_schematics()[0]))
            

