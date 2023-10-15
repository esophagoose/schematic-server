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
    schematics, hierarchy = project.get_schematics()
    print(hierarchy)
    return render_template(
        "project.html",
        name=name,
        schematics=schematics.keys(),
        hierarchy=hierarchy,
        variants=project.get_variant_names()
    )


@app.route("/schematic/<project>/<name>")
def schematic(project, name: str):
    schematic = BACKEND.projects[project].get_schematic_json(name)
    return {"name": name, "result": schematic.records}


@app.route("/variant/<name>/<variant_uid>")
def variant(name, variant_uid: str):
    vname = BACKEND.projects[name].get_variant_names()[variant_uid]
    variant = BACKEND.projects[name].variants[vname]
    return {"result": variant}


@app.route("/image/<name>/<schematic>/<image_b64>")
def image(name, schematic: str, image_b64: str):
    path = base64.b64decode(image_b64[:-len(".bmp")])
    app.logger.info(f"Requesting image: {path}")
    image_binary = BACKEND.projects[name].get_image(schematic, path)
    response = flask.make_response(image_binary)
    response.headers.set('Content-Type', 'image/bmp')
    response.headers.set('Content-Disposition',
                         'attachment', filename=image_b64)
    return response


@app.route("/")
def main():
    projects = BACKEND.projects.keys()
    return render_template("index.html", structure=projects)
