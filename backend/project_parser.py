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
from collections import OrderedDict

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
        self.parser = configparser.RawConfigParser()
        self.schematics: OrderedDict[str, Schematic] = {}
        self.variants = {}
        self.variant_uid_map = {}
        for filename in os.listdir(self.root):
            if filename.lower().endswith(".prjpcb"):
                self.path = filename
                break
        if not self.path:
            raise FileNotFoundError(f"No project file found in: {self.root}")
    
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
        path, _ = os.path.splitext(self.root / Path(self.path))
        hierachry = {}
        if os.path.exists(f"{path}.PrjPcbStructure"):
            hierachry = self._read_pcb_structure(f"{path}.PrjPcbStructure")
        return self._get_schematics_from_parser(), hierachry

    def _new_read_pcb_structure(self, path):
        tree = {}
        root_nodes = []
        with open(path, "r") as f:
            for line in f.readlines():
                is_root_node = re.search(r"^Record=TopLevelDocument")
                if is_root_node: # first line in file
                    schematic_name = re.search(r"FileName=(.*?).SchDoc\|", line).group()[0]
                    root_node = {
                        "name": schematic_name,
                        "children": [],
                    }
                    tree[schematic_name] = root_node
                    root_nodes.append(root_node)
                else:
                    parent_file_name, schematic_name = re.search(r"SourceDocument=(.*?).SchDoc\|.*?FileName=(.*?).SchDoc", line).group()
                    node = {
                        "name": schematic_name,
                        "children": [],
                    }
                    parent = tree[parent_file_name]
                    if not parent:
                        raise RuntimeError("Missing parent node!")
                    parent['children'].append(node)
                    tree[node["name"]] = node
        return root_nodes

    def _read_pcb_structure(self, path):
        tree = {}
        structure = []
        with open(path, "r") as f:
            for line in f.readlines():
                if line.startswith("Record=TopLevelDocument"):
                    schematic_name = re.search(r"FileName=(.*?).SchDoc\|", line).group()[0]
                    tree[schematic_name] = 1
                else:
                    parent_file_name, schematic_name = re.search(r"SourceDocument=(.*?).SchDoc\|.*?FileName=(.*?).SchDoc", line).group()
                    parent = tree[parent_file_name]
                    tree[schematic_name] = parent + 1
        sorted_tree = sorted(tree.items(), key=lambda x: x[1])
        for name, index in sorted_tree.items():
            structure.append("  "*index + name)
        return structure


    def _get_schematics_from_parser(self):
        for key, value in self.parser.items():
            if "Document" not in key:
                continue
            filepath = value["documentpath"]
            name, extension = os.path.splitext(filepath)
            if extension != ".SchDoc":
                continue
            self.schematics[name] = Schematic(filepath)
        return self.schematics
    
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
        self.schematics[path] = Schematic(filepath).read()
        return self.schematics[path]
    
    def get_image(self, schematic: str, path: str):
        sch = self.schematics[schematic]
        if sch.storage.get(path):
            return sch.storage.get(path)
        return sch.storage.get(path.replace("\\\\", "\\"))
            

