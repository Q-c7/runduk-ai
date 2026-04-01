"""Download hero portrait images from Steam CDN.

Uses the OpenDota API to resolve hero IDs to their internal names,
then fetches the 256x144 portraits from Steam's CDN.

Usage:
    python -m picker.app.download_hero_pics [--force]
"""

import argparse
import logging
import os

import requests

from picker.app.constants import HEROES

HERO_PICS_DIR = os.path.join(
    os.path.dirname(__file__), "gui", "picker_frame", "hero_pics"
)
CDN_URL = "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/{}.png"
OPENDOTA_HEROES_URL = "https://api.opendota.com/api/heroes"


def _build_id_to_cdn_name() -> dict[int, str]:
    """Fetch OpenDota hero list and map opendota_id -> CDN slug."""
    resp = requests.get(OPENDOTA_HEROES_URL, timeout=15)
    resp.raise_for_status()
    return {
        h["id"]: h["name"].removeprefix("npc_dota_hero_")
        for h in resp.json()
    }


def download_all(force: bool = False) -> None:
    os.makedirs(HERO_PICS_DIR, exist_ok=True)

    id_to_cdn = _build_id_to_cdn_name()

    downloaded, skipped, failed = 0, 0, 0
    for hero in HEROES:
        if hero.id == 0:
            continue

        dest = os.path.join(HERO_PICS_DIR, f"{hero.name.lower()}.png")
        if os.path.exists(dest) and not force:
            skipped += 1
            continue

        cdn_name = id_to_cdn.get(hero.opendota_id)
        if cdn_name is None:
            logging.warning(f"No CDN mapping for {hero.name} (opendota_id={hero.opendota_id})")
            failed += 1
            continue

        url = CDN_URL.format(cdn_name)
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            with open(dest, "wb") as f:
                f.write(resp.content)
            downloaded += 1
            logging.info(f"Downloaded {hero.name}")
        except requests.RequestException as e:
            logging.warning(f"Failed to download {hero.name}: {e}")
            failed += 1

    logging.info(f"Done: {downloaded} downloaded, {skipped} skipped, {failed} failed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Dota 2 hero portraits from Steam CDN")
    parser.add_argument("--force", action="store_true", help="Re-download even if file exists")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    download_all(force=args.force)


if __name__ == "__main__":
    main()
