import os
from typing import Dict
from flask import render_template
from flask import Flask
import flask
from backend.project_parser import Project
import json
import base64
import logging

app = Flask(__name__, template_folder="frontend/templates/")
root_folder = '.'
cache: Dict[str, Project] = {}


logging.basicConfig(level=logging.INFO)

@app.route("/project/<name>")
def project(name, variant=None, schematic=None):
    if name not in cache:
        cache[name] = Project(f"designs/{name}")
        cache[name].read()

    schematics = cache[name].get_schematics()
    variants = cache[name].get_variants()

    variant = int(flask.request.args.get('variant', 0))
    schematic_index = int(flask.request.args.get('schematic', 0))

    selected_schematic = schematics[schematic_index]
    sch_binary = cache[name].get_schematic_as_base64(selected_schematic).records
    return render_template(
        "project.html",
        name=name,
        schematics=schematics,
        variants=variants,
        selected_schematic=schematic_index,
        selected_variant=variant,
        render_target=sch_binary
    )

@app.route("/schematic/<name>/<schematic>")
def schematic(name, schematic: str):
    if name not in cache:
        cache[name] = Project(f"designs/{name}")
        cache[name].read()
    return cache[name].get_schematic_json(schematic).records

@app.route("/image/<name>/<schematic>/<image_b64>")
def image(name, schematic: str, image_b64: str):
    if name not in cache:
        cache[name] = Project(f"designs/{name}")
        cache[name].read()
    path = base64.b64decode(image_b64[:-len(".bmp")])
    app.logger.info(f"Requesting image: {path}")
    image_binary = cache[name].get_image(schematic, path)
    response = flask.make_response(image_binary)
    response.headers.set('Content-Type', 'image/bmp')
    response.headers.set('Content-Disposition', 'attachment', filename=image_b64)
    return response

@app.route("/")
def main():
    return render_template("index.html", structure=Project(f"designs").get_projects().keys());
    # for root, dirs, files in os.walk(root_folder):
    #     for file in files:
    #         if not file.endswith(".PrjPCB") and not dirs:
    #             continue
    #         print(root, dirs, file, os.path.isfile(file))
            # folders = os.path.split(root)
            # folders = folders[folders.index(root_folder)+1:]
            # i = 0
            # while i < len(folders): 
            #     if 
            # if i == 0 

