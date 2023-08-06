import json
import logging
import pathlib
import shutil
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional
from tqdm import tqdm

from watchtower_pipeline import models


@dataclass
class ContextWriter:

    projects: List[models.Project]
    asset_types: List[models.AssetType]
    task_types: List[models.TaskType]
    task_status: List[models.TaskStatus]
    users: List[models.User] = field(default_factory=list)

    def to_dict(self):
        return {
            'asset_types': [asdict(a) for a in self.asset_types],
            'users': [p.to_dict() for p in self.users],
            'projects': [asdict(p) for p in self.projects],
            'task_status': [asdict(t) for t in self.task_status],
            'task_types': [asdict(t) for t in self.task_types],
        }

    def download_previews(self, requests_headers: Optional[Dict] = None, force=False):
        for user in tqdm(self.users, desc="Downloading User thumbnails"):
            user.download_and_assign_thumbnail(requests_headers=requests_headers, force=force)
        for p in tqdm(self.projects, desc="Downloading Project thumbnails"):
            p.download_and_assign_thumbnail(requests_headers=requests_headers, force=force)

    def write_as_json(self):
        dst = models.BASE_PATH / 'public/data/projects/context.json'
        dst.parent.mkdir(parents=True, exist_ok=True)
        with open(dst, 'w') as outfile:
            json.dump(self.to_dict(), outfile, indent=2)


@dataclass
class ProjectWriter:
    """Saves a project and all its data as JSON files."""

    project: models.Project
    shots: List[models.Shot]
    assets: List[models.Asset]
    sequences: List[models.Sequence]
    edit: models.Edit
    casting: List[models.ShotCasting]

    def dump_data(self, name, data):
        dst = models.BASE_PATH / f"public/data/projects/{self.project.id}/{name}.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        with open(dst, 'w') as outfile:
            json.dump(data, outfile, indent=2)
        logging.debug(f"Saved {name} data for project {self.project.id}")

    def download_previews(self, requests_headers: Optional[Dict] = None, force=False):
        # Get the project square thumbnail
        self.project.download_and_assign_thumbnail(requests_headers=requests_headers, force=force)
        for s in tqdm(self.shots, desc="Downloading Shot thumbnails"):
            s.download_and_assign_thumbnail(requests_headers=requests_headers, force=force)
        for a in tqdm(self.assets, desc="Downloading Asset thumbnails"):
            a.download_and_assign_thumbnail(requests_headers=requests_headers, force=force)

    def write_as_json(self):
        self.dump_data('project', asdict(self.project))
        self.dump_data('edit', self.edit.to_dict())
        self.dump_data('assets', [asdict(a) for a in self.assets])
        self.dump_data('shots', [asdict(s) for s in self.shots])
        self.dump_data('sequences', [asdict(s) for s in self.sequences])
        self.dump_data('casting', [c.to_dict() for c in self.casting])


@dataclass
class WatchtowerBundler:
    @staticmethod
    def bundle(static_path: pathlib.Path):
        """Combine the embedded dist_watchtower with the static_path content."""
        dist_watchtower_src = pathlib.Path(__file__).parent.parent / 'dist_watchtower'
        dist_watchtower_dst = pathlib.Path().cwd() / 'watchtower'
        shutil.copytree(dist_watchtower_src, dist_watchtower_dst, dirs_exist_ok=True)
        shutil.copytree(static_path.parent, dist_watchtower_dst, dirs_exist_ok=True)
        logging.info(f"Watchtower bundle ready at {dist_watchtower_dst}")
        logging.info(f"You can preview it with the following command:")
        logging.info(f"\tpython -m http.server --directory {dist_watchtower_dst}")
