"""Blank HCD PDF asset download and cache helpers."""

import logging
from pathlib import Path

import httpx

from src.settings import settings

logger = logging.getLogger(__name__)

HCD_BLANK_FORMS: tuple[tuple[str, str, str], ...] = (
    (
        "476-6g",
        "hcd-rt-476-6g.pdf",
        "https://www.hcd.ca.gov/sites/default/files/docs/manufactured-and-mobilehomes/hcd-rt-476-6g.pdf",
    ),
    (
        "476-6",
        "hcd-rt-476-6.pdf",
        "https://www.hcd.ca.gov/sites/default/files/docs/manufactured-and-mobilehomes/hcd-rt-476-6.pdf",
    ),
    (
        "480-5",
        "hcd-rt-480-5.pdf",
        "https://www.hcd.ca.gov/sites/default/files/docs/manufactured-and-mobilehomes/hcd-rt-480-5.pdf",
    ),
)


def _forms_dir() -> Path:
    base = Path(settings.forms_dir)
    if base.is_absolute():
        return base
    api_root = Path(__file__).resolve().parents[2]
    return api_root / base


async def ensure_form_assets() -> dict[str, Path]:
    """Ensure all blank HCD forms exist locally, downloading if needed."""
    forms_dir = _forms_dir()
    forms_dir.mkdir(parents=True, exist_ok=True)

    out: dict[str, Path] = {}
    timeout = httpx.Timeout(20.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        for form_id, filename, url in HCD_BLANK_FORMS:
            dest = forms_dir / filename
            if dest.is_file():
                out[form_id] = dest
                continue
            if not settings.forms_download_enabled:
                raise RuntimeError(
                    f"form template missing and download disabled: {filename}"
                )
            tmp = dest.with_suffix(dest.suffix + ".part")
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                tmp.write_bytes(resp.content)
                tmp.replace(dest)
            except (httpx.HTTPError, OSError) as exc:
                try:
                    if tmp.exists():
                        tmp.unlink()
                except OSError:
                    pass
                raise RuntimeError(f"failed to download {filename} from {url}") from exc
            out[form_id] = dest
    return out


async def warm_cache_on_startup() -> None:
    """Best-effort prefetch of blank templates; never raises."""
    try:
        assets = await ensure_form_assets()
        logger.info("hcd forms ready: %s", ", ".join(sorted(assets)))
    except (RuntimeError, OSError, httpx.HTTPError):
        logger.warning(
            "hcd form warm-cache failed; continuing without startup cache",
            exc_info=True,
        )
