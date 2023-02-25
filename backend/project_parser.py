import base64
import os
from typing import Optional
from dataclasses import dataclass
import configparser
import glob
import logging
from typing import Dict
from backend.schematic import Schematic

logging.basicConfig(level=logging.DEBUG)
@dataclass
class ProjectFile:
    name: str
    exists: bool
    path: str

class Project:
    def __init__(self, root_folder) -> None:
        self.root = root_folder
        self.parser = configparser.ConfigParser()
        self.schematics: Dict[str, Schematic] = {}
    
    def read(self, filepath: Optional[str] = None) -> None:
        if not filepath:
            filepath = glob.glob(f"{self.root}/*.PrjPCB")[0]
        logging.info(f"Reading project file: {filepath}")
        self.parser.read(filepath, encoding="latin1")

    def get_projects(self):
        projects = {}
        for p in glob.glob(f"{self.root}/*/", recursive=True):
            folders = [i for i in p.split("/") if i]
            projects[folders[-1]] = p
        return projects

    def get_schematics(self):
        schematics = []
        for key, value in self.parser.items():
            if "Document" not in key:
                continue
            print(value)
            name, extension = os.path.splitext(value["documentpath"])
            if extension != ".SchDoc":
                continue
            exists = os.path.exists(f'{self.root}/{value["documentpath"]}')
            schematics.append(ProjectFile(name, exists, value["documentpath"]))
        return schematics
    
    def get_variants(self):
        return ["[No Variation]"]

    def get_schematic_as_base64(self, doc: ProjectFile) -> Schematic:
        filepath = f"{self.root}/{doc.path}"
        return Schematic().read(filepath)

    def get_schematic_json(self, path: str) -> Schematic:
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
            

