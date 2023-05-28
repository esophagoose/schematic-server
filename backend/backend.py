import backend.project_parser as pp
import glob 
from typing import Dict
from pathlib import Path

class Backend:
    def __init__(self, root) -> None:
        self.root = Path(root)
        self._projects: Dict[str, pp.Project] = {}

    @property
    def projects(self):
        if not self._should_refresh_projects():
            return self._projects
        self._projects.clear()
        for p in glob.glob(f"{self.root}/*/", recursive=True):
            folders = [i for i in p.split("/") if i]
            project_folder = folders[-1]
            try:
                self._projects[project_folder] = pp.Project(p)
            except FileNotFoundError as e:
                print(e)
        return self._projects
    
    def _should_refresh_projects(self):
        # TODO: Write better refreshing mechanism
        return not self._projects
    