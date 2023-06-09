import os
from typing import Dict
from flask import render_template
from flask import Flask
import flask
from backend.backend import Backend
import yaml
import base64
import logging


CONFIG = yaml.safe_load(open("config.yaml"))
ROOT_DIRECTORY = CONFIG["project_directory"]
BACKEND = Backend(ROOT_DIRECTORY)
app = Flask(__name__, template_folder="frontend/templates/")

logging.basicConfig(level=logging.INFO)

@app.route("/project/<name>")
def project(name):
    project = BACKEND.projects[name]
    return render_template(
        "project.html",
        name=name,
        schematics=project.get_schematics(),
        variants=project.get_variant_names()
    )

@app.route("/schematic/<name>/<schematic>")
def schematic(name, schematic: str):
    schematic = BACKEND.projects[name].get_schematic_json(schematic)
    return {"result": schematic.records}

@app.route("/variant/<name>/<variant_uid>")
def variant(name, variant_uid: str):
    print(variant_uid, BACKEND.projects[name].get_variant_names())
    vname = BACKEND.projects[name].get_variant_names()[variant_uid]
    print(vname, BACKEND.projects[name].variants.keys())
    variant = BACKEND.projects[name].variants[vname]
    return {"result": variant}

@app.route("/image/<name>/<schematic>/<image_b64>")
def image(name, schematic: str, image_b64: str):
    path = base64.b64decode(image_b64[:-len(".bmp")])
    app.logger.info(f"Requesting image: {path}")
    image_binary = BACKEND.projects[name].get_image(schematic, path)
    response = flask.make_response(image_binary)
    response.headers.set('Content-Type', 'image/bmp')
    response.headers.set('Content-Disposition', 'attachment', filename=image_b64)
    return response

@app.route("/")
def main():
    projects = BACKEND.projects.keys()
    return render_template("index.html", structure=projects);

