import os.path
from collections import defaultdict

import pandas as pd
import pickle

import logging

from picker.app.old_python_gui.stub import AbstractFrame


class TeamManager:
    AVAILABLE_UI_ELEMENTS = [
        "hero_adder",
        "players_display",
        "player_adder",
        "team_controls",
        "team_heroes_display",
        "player_menu",
    ]

    def __init__(self, pq_path="team.pickle"):
        self.team: pd.DataFrame

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(script_dir, pq_path)
        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                self.team = pickle.load(f)
        else:
            self.team = self._create_empty_df()

        self.current_pos = 1
        self.current_player: str | None = None

        self.ui_elements: dict[str, AbstractFrame] = {}

    def get_current_pos(self) -> int:
        return self.current_pos

    def add_ui_element(self, name: str, element: AbstractFrame) -> None:
        assert name in self.AVAILABLE_UI_ELEMENTS
        self.ui_elements[name] = element

    def _update_ui_element(self, names: list[str]) -> None:
        for name in names:
            if name in self.ui_elements:
                self.ui_elements[name].update_ui()

    def set_current_pos(self, current_pos: int) -> None:
        assert current_pos in range(1, 6)
        self.current_pos = current_pos
        self._update_ui_element(["hero_adder"])

    def get_current_player(self) -> str | None:
        return self.current_player

    def set_current_player(self, current_player: str | None) -> None:
        assert current_player in self.team.index or current_player is None
        self.current_player = current_player
        self._update_ui_element(
            ["hero_adder", "players_display", "team_controls", "team_heroes_display"]
        )

    def has_player(self, player: str) -> bool:
        return player in self.team.index

    @staticmethod
    def _create_empty_df() -> pd.DataFrame:
        table_dict = {"name": [], "is_active": []}
        for i in range(1, 6):
            table_dict[f"good_pos{i}"] = []
            table_dict[f"ok_pos{i}"] = []  # not used at the moment

        df = pd.DataFrame(table_dict)

        df["name"] = df["name"].astype(str)
        df["is_active"] = df["is_active"].astype(bool)

        return pd.DataFrame(table_dict).set_index("name")

    def add_player(self, name: str) -> None:
        table_dict = {"name": [name], "is_active": [False]}
        for i in range(1, 6):
            table_dict[f"good_pos{i}"] = [[]]
            table_dict[f"ok_pos{i}"] = [[]]  # not used at the moment

        row = pd.DataFrame(table_dict)

        row["is_active"] = row["is_active"].astype(bool)

        row = row.set_index("name")
        self.team = pd.concat((self.team, row))
        self.team["is_active"] = self.team["is_active"].astype(bool)

        self._update_ui_element(["player_menu"])

    def remove_player(self, name: str) -> None:
        self.team.drop(name, axis=0, inplace=True)
        if self.current_player is not None:
            self.current_player = None
            self._update_ui_element(self.AVAILABLE_UI_ELEMENTS)

    def get_inactive_players(self) -> list[str]:
        if self.team["is_active"].sum() == self.team["is_active"].size:
            return []
        return self.team[self.team.is_active is False].index.tolist()

    def get_active_players(self) -> list[str]:
        if self.team["is_active"].sum() == 0:
            return []
        return self.team[self.team.is_active].index.tolist()

    def is_active(self, name: str) -> bool:
        return self.team.loc[name, "is_active"]

    def get_all_players(self) -> list[str]:
        return self.team.index.tolist()

    def get_player_preferences(self, name: str) -> dict[int, list[int]]:
        return {i: self.team.loc[name, f"good_pos{i}"] for i in range(1, 6)}

    def get_all_preferences(self) -> dict[int, list[int]]:
        if self.team.is_active.sum() == 0:
            return {i: [] for i in range(1, 6)}

        ret = {}
        for i in range(1, 6):
            column = self.team.loc[self.team.is_active, f"good_pos{i}"]
            if column.empty:
                ret[i] = []
                continue
            ret[i] = column.explode().dropna().unique().tolist()

        return ret

    def add_preference(self, name: str, hero_id: int, position: int) -> None:
        if hero_id in self.team.loc[name, f"good_pos{position}"]:
            logging.warning(
                f"{name} is already proficient with {hero_id} in position {position}"
            )
            return
        self.team.loc[name, f"good_pos{position}"].append(hero_id)
        self._update_ui_element(["hero_adder", "team_heroes_display"])

    def remove_preference(self, name: str, hero_id: int, position: int) -> None:
        if hero_id not in self.team.loc[name, f"good_pos{position}"]:
            logging.warning(
                f"{name} is already not proficient with {hero_id} in position {position}"
            )
            return
        self.team.loc[name, f"good_pos{position}"].remove(hero_id)
        self._update_ui_element(["hero_adder", "team_heroes_display"])

    def set_active_status(self, name: str, status: bool) -> None:
        if self.team["is_active"].sum() > 5 and status:
            logging.warning("Trying to fit more than 5 people in a same team")
            return

        self.team.loc[name, "is_active"] = status
        self._update_ui_element(
            ["players_display", "team_controls", "team_heroes_display"]
        )

    def change_status(self, name: str) -> None:
        new_status = not self.team.loc[name, "is_active"]
        self.set_active_status(name=name, status=new_status)

    def save_team(self) -> None:
        with open(self.path, "wb") as f:
            pickle.dump(self.team, f)

    def get_reversed_preferences(self) -> dict[int, list[int]]:
        """
        key: hero_id
        value: hero_pos
        """
        reversed_prefs = self.get_all_preferences()

        ret = defaultdict(list)
        for hero_pos, heroes_list in reversed_prefs.items():
            for hero_id in heroes_list:
                ret[hero_id].append(hero_pos)

        return ret
