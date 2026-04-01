# Runduk AI

Dota 2 draft assistant — predicts Radiant win probability from hero picks and rank using a Transformer model trained on OpenDota public match data.

## Installation

Requires Python >=3.13 and [uv](https://docs.astral.sh/uv/).

```shell
uv sync
source .venv/bin/activate
```

For training (adds matplotlib):

```shell
uv sync --extra train
```

## Pipelines

### 1. Scrape match data

Download public match data from the OpenDota API for a given date range:

```shell
python -m picker.scraping --start 2025-11-01 --end 2025-11-15
```

Output: `DATA/raw_2025-11-01_2025-11-15.parquet`

Options: `--freq 6h` (time window per request), `--output PATH`, `-v` (verbose).

### 2. Preprocess

Filter game modes, bucket rank tiers, and derive winner/loser teams:

```shell
python -m picker.data --input DATA/raw_2025-11-01_2025-11-15.parquet --output DATA/processed.parquet
```

Options: `--game-modes 1 2 3 4 22` (override default modes), `-v`.

### 3. Train model

```shell
python -m picker.model --data DATA/processed.parquet --name latest --epochs 100 --device cuda
```

Saves `latest.pth` (state dict) and `latest.raw_model` (full model for the GUI).

Options: `--batch-size 8192`, `--lr 3e-4`, `--num-layers 6`, `--num-heads 8`, `--hero-emb-dim 28`, `--rank-emb-dim 3`, `--mask-p 0.2`, `--test-split 0.05`, `--plot-dir plots/`.

## GUI

Download hero portrait images from Steam CDN (one-time, ~20 seconds):

```shell
python -m picker.app.download_hero_pics
```

Launch the Tkinter draft helper (requires a display server on Linux/WSL):

```shell
python -m picker.app.gui --model path/to/model.raw_model
```

The GUI has two screens:
- **Team screen** — manage players and their hero preferences per position.
- **Picker screen** — draft heroes, see real-time win probability predictions sorted by role.

Hero images are gitignored and downloaded on demand. Missing images get auto-generated placeholders.

## Project structure

```
picker/
├── scraping/              # OpenDota API client + CLI
│   ├── opendota.py
│   ├── constants.py
│   └── __main__.py
├── data/                  # Preprocessing pipeline
│   ├── preprocess.py
│   └── __main__.py
├── model/                 # Model definition + training
│   ├── transformer.py
│   ├── dataset.py
│   ├── constants.py
│   ├── train.py
│   └── __main__.py
└── app/                       # Application
    ├── constants.py           # Hero definitions (127 heroes, positions)
    ├── download_hero_pics.py  # Steam CDN image downloader
    ├── logic/
    │   └── core.py            # Inference engine (no GUI dependency)
    └── gui/                   # Tkinter desktop UI
        ├── main.py            # App entry, frame switching
        ├── logic/
        │   ├── core.py        # Desktop runner (extends inference engine)
        │   └── team.py        # Team/player preference manager
        ├── picker_frame/      # Draft screen widgets
        │   └── hero_pics/     # Hero portraits (gitignored, downloaded)
        └── team_frame/        # Team management screen widgets
legacy/                    # Archived notebooks and old model experiments
```
