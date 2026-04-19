"""Filesystem layout per job."""

from pathlib import Path

from src.settings import settings


class JobPaths:
    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self.root = Path(settings.job_root) / job_id

    @property
    def title_pdf(self) -> Path:
        return self.root / "title.pdf"

    @property
    def title_png(self) -> Path:
        return self.root / "title.png"

    @property
    def filled_dir(self) -> Path:
        return self.root / "filled"

    @property
    def thumbs_dir(self) -> Path:
        return self.root / "thumbs"

    @property
    def zip_path(self) -> Path:
        return self.root / "packet.zip"

    def ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.filled_dir.mkdir(parents=True, exist_ok=True)
        self.thumbs_dir.mkdir(parents=True, exist_ok=True)
