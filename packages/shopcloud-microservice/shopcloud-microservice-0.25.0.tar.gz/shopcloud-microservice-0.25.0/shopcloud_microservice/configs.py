from pathlib import Path
from typing import List

import yaml

from . import exceptions


class Config:
    FILENAME = 'microservices.yaml'
    VERSION = 'V1'

    def __init__(self, **kwargs):
        self.working_dir = kwargs.get('working_dir', None)
        if self.working_dir == '.':
            self.working_dir = None

    def dict(self) -> dict:
        return {}

    def load_projects(self) -> List[str]:
        filename = 'projects.yaml'

        if self.working_dir is not None:
            filename = Path(self.working_dir) / filename

        if not Path(filename).exists():
            raise exceptions.ProjectFileNotFound()

        projects = []

        with open(filename) as f:
            data = yaml.safe_load(f.read())
            projects = data.get('projects', [])

        return projects
