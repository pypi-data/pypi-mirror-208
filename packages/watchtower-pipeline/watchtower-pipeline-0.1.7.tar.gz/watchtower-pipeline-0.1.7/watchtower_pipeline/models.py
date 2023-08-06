import hashlib
import logging
import pathlib
import requests
from urllib.parse import urlparse
import sys
import uuid
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, TypedDict, Optional


BASE_PATH = pathlib.Path.cwd()

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


class StaticPreviewMixin:

    thumbnailUrl = None

    @staticmethod
    def hash_filename(name):
        return hashlib.md5(name.encode()).hexdigest()

    @staticmethod
    def generate_preview_file_path(file_id: str) -> pathlib.Path:
        """Generate a normalized file path.
        This forces .png extension, which for now is ok since all image
        file use that extension, and we do not need to deal with videos.

        For example:
        - 0a32d425-6723-4f2b-baf7-2a6d457fa669
        becomes:
        - 0a/30a32d425-6723-4f2b-baf7-2a6d457fa669.png
        """
        filename = f'{file_id}.png'
        return pathlib.Path('data/previews') / file_id[:2] / filename

    @staticmethod
    def fetch_and_save_media(src_url, headers, dst: pathlib.Path, force=False):
        if not dst.is_file() or force:
            dst.parent.mkdir(parents=True, exist_ok=True)
            r_file = requests.get(src_url, headers=headers, allow_redirects=True)
            dst.write_bytes(r_file.content)

    def download_and_assign_thumbnail(
        self,
        requests_headers: Optional[Dict] = None,
        force=False,
    ):
        """Download and assign a thumbnail.

        This function assumes that the download url is a valid (full) url located
        at self.thumbnailUrl, and will replace that value with a path to (absolute
        from the site root) to the local file once it's downloaded.
        """
        src_url = self.thumbnailUrl
        logging.debug(f"Downloading {self.name}, {src_url}")
        if not src_url:
            return
        result = urlparse(src_url)
        if not all([result.scheme, result.netloc]):
            logging.debug("Skipping local url. This file was already processed.")
            return
        dst_url = self.generate_preview_file_path(self.hash_filename(src_url))
        dst = BASE_PATH / 'public' / dst_url
        self.fetch_and_save_media(src_url, requests_headers, dst, force=force)
        setattr(self, 'thumbnailUrl', str(dst_url))


@dataclass
class IdMixin:
    # id: Optional[str]  # In Kitsu it's a UUID
    # In Python 3.10 it will be possible to use this, and make id actually Optional
    # id: Optional[uuid.UUID] = field(default_factory=get_new_uuid)
    name: str

    @staticmethod
    def get_new_uuid() -> str:
        return str(uuid.uuid4())

    def __post_init__(self):
        self.id = self.id or self.get_new_uuid()


@dataclass
class AssetType(IdMixin):
    """Asset Type such as prop, character, etc."""

    id: Optional[str] = None


@dataclass
class TaskType(IdMixin):
    """Task Type such as layout, animation, lighting etc."""

    color: str  # A hex color
    for_shots: bool = False
    id: Optional[str] = None


@dataclass
class TaskStatus(IdMixin):
    """Task Status such as todo, in_progress, review, etc"""

    color: str  # A hex color
    id: Optional[str] = None


@dataclass
class User(StaticPreviewMixin, IdMixin):
    """Members of a project, associated to tasks."""

    has_avatar: bool = False
    id: Optional[str] = None
    thumbnailUrl: Optional[str] = None

    @property
    def full_name(self):
        return self.name

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'full_name': self.full_name,
            'has_avatar': self.has_avatar,
        }


@dataclass
class Project(StaticPreviewMixin, IdMixin):
    """A film, short film, etc."""

    ratio: str
    resolution: str
    asset_types: List[str] = field(default_factory=list)
    task_types: List[str] = field(default_factory=list)
    task_statuses: List[str] = field(default_factory=list)
    team: List[str] = field(default_factory=list)
    id: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    fps: float = 24


@dataclass
class JsonMixin:
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_list(self, key) -> list:
        """We expect that key is in the dict, and that the value is a list."""
        return self.to_dict()[key]


@dataclass
class Task:
    """A task associated with a Shot or an Asset."""

    task_status_id: str
    task_type_id: str
    assignees: List[str] = field(default_factory=list)  # Maps to User ID
    id: Optional[str] = None

    @staticmethod
    def get_new_uuid() -> str:
        return str(uuid.uuid4())

    def __post_init__(self):
        self.id = self.id or self.get_new_uuid()


@dataclass
class Asset(StaticPreviewMixin, IdMixin):
    """An entity such as a character, set, prop, etc."""

    asset_type_id: str
    tasks: List[Task] = field(default_factory=list)
    id: Optional[str] = None
    thumbnailUrl: Optional[str] = None


class ShotData(TypedDict):
    """Shot metadata (usually custom defined in the production tracker)"""

    frame_in: int
    frame_out: int


@dataclass
class Shot(StaticPreviewMixin, IdMixin):
    """A shot, the reference point for tasks."""

    sequence_id: str
    data: ShotData
    tasks: List[Task] = field(default_factory=list)
    startFrame: int = 0
    durationSeconds: float = 0
    id: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    fps: float = 24

    def __post_init__(self):
        super(Shot, self).__post_init__()
        self.startFrame = int(self.data['frame_in'])
        self.durationSeconds = (int(self.data['frame_out']) - self.startFrame) / self.fps


@dataclass
class ShotCasting:
    """The relationship between assets and shots."""

    shot: Shot
    assets: List[Asset] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {'shot_id': self.shot.id, 'asset_ids': [a.id for a in self.assets]}


@dataclass
class Sequence(IdMixin):
    id: Optional[str] = None


@dataclass
class Edit:
    """The complete cut of the project."""

    project: Project
    totalFrames: int
    frameOffset: int
    sourceName: Optional[str] = None
    sourceType: str = 'video/mp4'

    def __post_init__(self):
        if not self.sourceName:
            self.sourceName = f"data/projects/{self.project.id}/edit.mp4"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'totalFrames': self.totalFrames,
            'frameOffset': self.frameOffset,
            'sourceName': self.sourceName,
            'sourceType': self.sourceType,
        }
