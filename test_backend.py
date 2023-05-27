import os
from typing import Dict
from flask import render_template
from flask import Flask
import flask
from backend.backend import Backend
import yaml
import base64
import logging
import pytest


EXPECTED_DESIGNS = ['FPGA1394', 'nRF52-Quadcopter', 'Zooid', 'ZooidReceiver']
EXAMPLE_PROJECT = EXPECTED_DESIGNS[0]
EXAMPLE_SCHEMATIC = "S01.SchDoc"



CONFIG = yaml.safe_load(open("config.yaml"))
ROOT_DIRECTORY = CONFIG["project_directory"]
BACKEND = Backend(ROOT_DIRECTORY)


class TestSchematicServer:
    def test_project(self):
        BACKEND.get_projects()
        received = set(BACKEND.projects.keys())
        diff = (received - set(EXPECTED_DESIGNS))
        assert not diff, f"Differences are {diff}"

    def schematic(self):
        project = BACKEND.projects[EXAMPLE_PROJECT]
        assert not project.get_schematic_json(EXAMPLE_SCHEMATIC).records

    # def image(name, schematic: str, image_b64: str):
    #     path = base64.b64decode(image_b64[:-len(".bmp")])
    #     app.logger.info(f"Requesting image: {path}")
    #     image_binary = BACKEND.projects[name].get_image(schematic, path)
    #     response = flask.make_response(image_binary)
    #     response.headers.set('Content-Type', 'image/bmp')
    #     response.headers.set('Content-Disposition', 'attachment', filename=image_b64)
    #     return response
