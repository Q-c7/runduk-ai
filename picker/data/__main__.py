import argparse
import logging

from picker.data.preprocess import preprocess
from picker.scraping.constants import RELEVANT_GAME_MODES


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preprocess raw scraped Dota 2 match data for training",
    )
    parser.add_argument(
        "--input", type=str, required=True, help="Path to raw parquet file"
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Path for processed parquet output"
    )
    parser.add_argument(
        "--game-modes",
        type=int,
        nargs="+",
        default=None,
        help=f"Game mode IDs to keep (default: {RELEVANT_GAME_MODES})",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    game_modes = set(args.game_modes) if args.game_modes else None
    preprocess(input_path=args.input, output_path=args.output, game_modes=game_modes)


if __name__ == "__main__":
    main()
