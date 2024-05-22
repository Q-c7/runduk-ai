import datetime

import requests
import orjson
import pandas as pd
from time import sleep, perf_counter

from typing import Any

import logging

from tqdm import tqdm

from picker.scraping.constants import (
    MANUAL_LOCK_SECONDS,
)


def _parse_match(match: dict[Any, Any]) -> dict[str, Any] | None:
    if len(match['radiant_team']) + len(match['dire_team']) != 10:
        logging.debug(
            f"Wrong number of players for match ID {match['match_id']}, seq_num {match['match_seq_num']}"
        )
        return None

    # ret = dict()
    # for name in (
    #     "match_id",
    #     "match_seq_num",
    #     "game_mode",
    #     "start_time",
    #     "duration",
    #     "avg_rank_tier",
    #     "avg_mmr",
    # ):
    #     ret[name] = match[name]
    # ret["bans"] = None
    # if "picks_bans" in match:
    #     pbs: list[dict[str, int | bool]] = match["picks_bans"]
    #     ret["bans"] = [pb["hero_id"] for pb in pbs if not pb["is_pick"]]
    # ret["winner_team"] = []
    # ret["loser_team"] = []
    # for idx, p in enumerate(match["players"]):
    #     nam = "winner_team" if p["win"] else "loser_team"
    #     ret[nam].append(p["hero_id"])
    # ret["radiant_won"] = match["players"][0]["win"]

    return match


def _get_web_datetime(dt: datetime.datetime) -> str:
    return (
        "%27"
        + dt.strftime("%Y-%m-%dT%H")
        + "%3A"
        + dt.strftime("%M")
        + "%3A"
        + dt.strftime("%S.000Z")
        + "%27"
    )


def _generate_request(
    left_ts: datetime.datetime, right_ts: datetime.datetime, matches_count: int = 20000
) -> str:
    left_ts_str = _get_web_datetime(left_ts)
    right_ts_str = _get_web_datetime(right_ts)

    request = f"""https://api.opendota.com/api/explorer?sql=SELECT%0Ajson_agg(m)%20public_matches
    %0AFROM%20(%0A%20%20SELECT%20match_id%2C%20match_seq_num%2C%20duration
    %2C%20start_time%2C%20game_mode%2C%20avg_rank_tier%2C%20radiant_team%2C%20dire_team%2C%20radiant_win%20
    FROM%20public_matches
    %20%0A%20%20WHERE%20TRUE%20%0A%20%20AND%20start_time%20%3E%20
    extract(epoch%20from%20timestamp%20{left_ts_str})
    %0A%20%20AND%20start_time%20%3C%20
    extract(epoch%20from%20timestamp%20{right_ts_str})
    %0A%20%20AND%20duration%20%3E%20900%20%0A%20%20
    %0A%20%20LIMIT%20{matches_count})%20m""".replace(
        "\n", ""
    )

    return request


def request_matches_by_time(
    left_ts: datetime.datetime, right_ts: datetime.datetime
) -> list[dict[str, Any]]:
    req = _generate_request(left_ts, right_ts)
    retries = 0

    while True:
        msg = requests.get(req)
        sleep(1)

        if msg.status_code == 200:
            break
        elif msg.status_code == 400:
            logging.warning("Statement got timed out, retrying in 5 seconds...")
            logging.warning(f"Response text: {msg.text}")
            sleep(5)
            retries += 1
            if retries > 10:
                logging.error(
                    "Can't download DATA using more than 10 retries, skipping..."
                )
                return []
        elif msg.status_code == 429:
            logging.warning("Rate limit exceeded, retrying in 1 minute...")
            logging.warning(f"Response text: {msg.text}")
            sleep(60)
            retries += 1
            if retries > 10:
                logging.error(
                    "Can't download DATA using more than 10 retries, skipping..."
                )
                return []
        else:
            assert False, f"Unknown status code {msg.status_code}"

    msg_dict = orjson.loads(msg.text)
    raw_matches = msg_dict["rows"][0]["public_matches"]
    parsed_matches = []

    if raw_matches is not None:
        for m in raw_matches:
            parsed_m = _parse_match(m)
            if parsed_m is not None:
                parsed_matches.append(parsed_m)

    return parsed_matches


def request_matches(
    left_ts: datetime.datetime, right_ts: datetime.datetime, freq_dt: datetime.timedelta
) -> pd.DataFrame:
    data = []
    tmp_df = pd.DataFrame()
    last_req_time = -1

    for start in tqdm(pd.date_range(start=left_ts, end=right_ts, freq=freq_dt)):
        end = start + freq_dt
        req_time = perf_counter()
        diff = req_time - last_req_time

        if diff < MANUAL_LOCK_SECONDS:
            sleep(MANUAL_LOCK_SECONDS - diff)

        last_req_time = perf_counter()

        data.extend(request_matches_by_time(left_ts=start, right_ts=end))

    tmp_df = pd.concat((tmp_df, pd.DataFrame(data)), axis=0)
    tmp_df.to_parquet(path=f'DATA/tmp_{left_ts.strftime("%m.%d.%Y.%H.%M.%S")}.parquet')
    return tmp_df
