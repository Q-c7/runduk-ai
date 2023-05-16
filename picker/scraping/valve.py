import requests
import orjson
import pandas as pd
from time import sleep, perf_counter

from typing import Any

import logging

from scraping.constants import (
    VALVE_API_KEYS,
    MANUAL_LOCK_SECONDS,
    MATCHES_CHUNK,
    SECONDS_AFTER_429,
)


def _parse_match(match: dict[Any, Any]) -> dict[str, Any] | None:
    if len(match["players"]) != 10 or match["human_players"] != 10:
        logging.debug(
            f"Wrong number of players for match ID {match['match_id']}, seq_num {match['match_seq_num']}"
        )
        return None

    ret = dict()
    for name in (
        "match_id",
        "match_seq_num",
        "radiant_win",
        "game_mode",
        "start_time",
        "duration",
    ):
        ret[name] = match[name]
    ret["bans"] = None
    if "picks_bans" in match:
        pbs: list[dict[str, int | bool]] = match["picks_bans"]
        ret["bans"] = [pb["hero_id"] for pb in pbs if not pb["is_pick"]]
    ret["radiant_team"] = []
    ret["dire_team"] = []
    ret["num_leavers"] = 0
    for idx, p in enumerate(match["players"]):
        nam = "radiant_team" if idx < 5 else "dire_team"
        ret[nam].append(p["hero_id"])
        try:
            ret["num_leavers"] += not not p["leaver_status"]
        except KeyError:
            pass

    return ret


def request_100_matches(seq_num: int, key: int) -> list[dict[str, Any]]:
    assert key < len(VALVE_API_KEYS)
    while True:
        msg = requests.get(
            "http://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/v1",
            params={
                "start_at_match_seq_num": seq_num,
                "key": VALVE_API_KEYS[key],
                "matches_requested": 100,
            },
        )  # actually it's hard-coded as 100
        sleep(1)

        if msg.status_code == 200:
            break
        elif msg.status_code == 429:
            logging.warning(f"Spamming dota API too fast on seq_num {seq_num}")
            sleep(SECONDS_AFTER_429)
        elif msg.status_code == 503:
            logging.error("Something is wrong, server is busy")
            sleep(30)
        else:
            assert False, f"Unknown status code {msg.status_code}"

    msg_dict = orjson.loads(msg.text)
    raw_matches = msg_dict["result"]["matches"]
    parsed_matches = []
    for m in raw_matches:
        parsed_m = _parse_match(m)
        if parsed_m is not None:
            parsed_matches.append(parsed_m)

    return parsed_matches


def request_matches(
    start_seq_num: int, num_matches: int = 100, key: int = 0
) -> pd.DataFrame:
    data = []
    tmp_df = pd.DataFrame()
    last_req_time = -1
    _key = key

    for seq_num in range(start_seq_num, start_seq_num + num_matches, 100):
        req_time = perf_counter()
        diff = req_time - last_req_time

        if diff < MANUAL_LOCK_SECONDS:
            # print('before sleep', perf_counter())
            sleep(MANUAL_LOCK_SECONDS - diff)
            # print('after sleep', perf_counter())

        last_req_time = perf_counter()
        if key == -1:  # rotating keys
            _key = (_key + 1) % len(VALVE_API_KEYS)

        data.extend(request_100_matches(seq_num, _key))
        # key = (key + 1) % len(VALVE_API_KEYS)

        if len(data) > MATCHES_CHUNK:
            tmp_df = pd.concat((tmp_df, pd.DataFrame(data)), axis=0)
            tmp_df.to_parquet(path=f"DATA/tmp_{start_seq_num}.parquet")
            data = []

    tmp_df = pd.concat((tmp_df, pd.DataFrame(data)), axis=0)
    tmp_df.to_parquet(path=f"DATA/tmp_{start_seq_num}.parquet")
    return tmp_df
