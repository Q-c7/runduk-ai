import argparse
import datetime
import logging
import os

from picker.scraping.opendota import request_matches


def parse_date(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s, "%Y-%m-%d")


def parse_freq(s: str) -> datetime.timedelta:
    unit = s[-1]
    value = int(s[:-1])
    match unit:
        case "h":
            return datetime.timedelta(hours=value)
        case "d":
            return datetime.timedelta(days=value)
        case "m":
            return datetime.timedelta(minutes=value)
        case _:
            raise ValueError(
                f"Unknown freq unit '{unit}', use h/d/m (e.g. 6h, 1d, 30m)"
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape Dota 2 public match data from OpenDota API",
    )
    parser.add_argument(
        "--start", type=parse_date, required=True, help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end", type=parse_date, required=True, help="End date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output parquet path (default: DATA/raw_{start}_{end}.parquet)",
    )
    parser.add_argument(
        "--freq",
        type=parse_freq,
        default=datetime.timedelta(hours=6),
        help="Time window per API request (default: 6h)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if args.output is None:
        os.makedirs("DATA", exist_ok=True)
        start_str = args.start.strftime("%Y-%m-%d")
        end_str = args.end.strftime("%Y-%m-%d")
        args.output = f"DATA/raw_{start_str}_{end_str}.parquet"

    logging.info(f"Scraping matches from {args.start} to {args.end}")
    logging.info(f"Frequency: {args.freq}, output: {args.output}")

    df = request_matches(
        left_ts=args.start,
        right_ts=args.end,
        freq_dt=args.freq,
    )

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    df.to_parquet(args.output)
    logging.info(f"Saved {len(df)} matches to {args.output}")


if __name__ == "__main__":
    main()
