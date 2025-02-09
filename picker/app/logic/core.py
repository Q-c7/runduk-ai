import os
from time import perf_counter

import torch
import logging

from picker.app.constants import HEROES
from picker.model.transformer import TransformerModel
from picker.scraping.constants import RELEVANT_GAME_MODES


class ProgramRunnerWithoutGUI:
    def __init__(self, model_path="latest", debug: bool = False):
        self.rank = 4
        self._debug = debug
        self._my_team: list[int] = []
        self._my_bans: list[int] = []
        self._enemy_team: list[int] = []
        self._enemy_bans: list[int] = []

        logging.info("Loading _model...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(script_dir, model_path)
        self._model: TransformerModel = torch.load(
            full_path
        )  # FIXME change to a JIT script
        self._model.cpu().eval()
        logging.info("Model loaded")
        self.latest_predictions = {}
        self.prediction_display = None

    def swap_teams(self) -> None:
        tmp = self._my_team
        tmp2 = self._my_bans
        self._my_team = self._enemy_team
        self._my_bans = self._enemy_bans
        self._enemy_team = tmp
        self._enemy_bans = tmp2
        self._redraw_predictions()

    def container(self, is_enemy: bool, is_ban: bool) -> list[int]:
        if is_enemy and is_ban:
            return self._enemy_bans
        elif is_enemy:
            return self._enemy_team
        elif is_ban:
            return self._my_bans
        else:
            return self._my_team

    def is_in_game(self, hero_id: int) -> bool:
        return (
            hero_id in self._my_team
            or hero_id in self._enemy_team
            or hero_id in self._my_bans
            or hero_id in self._enemy_bans
        )

    def add_hero(self, hero_id: int, is_enemy: bool, is_ban: bool) -> None:
        assert 0 < hero_id < len(HEROES)
        container = self.container(is_enemy=is_enemy, is_ban=is_ban)
        max_len = 7 if is_ban else 5
        if len(container) >= max_len:
            name = "Bans" if is_ban else "Team"

            logging.warning(f"{name} #{int(is_enemy)} is already full!")
            return
        if self.is_in_game(hero_id):
            logging.warning(f"Hero #{hero_id} already in game!")
            return

        container.append(hero_id)
        self._redraw_predictions()

    def remove_hero(
        self, hero_id: int, is_enemy: bool = False, is_ban: bool = False
    ) -> None:
        assert 0 < hero_id < len(HEROES)

        container = self.container(is_enemy=is_enemy, is_ban=is_ban)
        name = "Bans" if is_ban else "Team"

        if not len(container):
            logging.warning(f"{name} #{int(is_enemy)} is already empty!")
            return
        if hero_id not in container:
            logging.warning(f"Hero #{hero_id} not in {name} #{int(is_enemy)}!")
            return

        container.remove(hero_id)
        self._redraw_predictions()

    def change_rank(self, new_rank: int) -> None:
        self.rank = new_rank
        self._redraw_predictions()

    def _redraw_predictions(self) -> None:
        self._refresh_predictions()
        if not self._debug:
            raise NotImplementedError

    def _refresh_predictions(self) -> None:
        if len(self._my_team) >= 5:
            logging.warning("Team is already full, cannot predict")
            return

        available_heroes = (
            set(range(1, len(HEROES)))
            - set(self._my_team)  # does not include 0
            - set(self._enemy_team)
            - set(self._my_bans)
            - set(self._enemy_bans)
        )

        my_team_pads = 4 - len(self._my_team)
        enemy_team_pads = 5 - len(self._enemy_team)

        batch = torch.as_tensor(
            [
                self._my_team
                + [hero]
                + [0] * my_team_pads
                + self._enemy_team
                + [0] * enemy_team_pads
                for hero in range(len(HEROES))  # this INCLUDES 0!
            ]
        )
        ranks = torch.as_tensor([self.rank] * batch.shape[0])

        time_counter = perf_counter()
        preds = torch.softmax(self._model((batch, ranks)), dim=-1)[
            list(available_heroes), 1
        ].tolist()
        logging.info(f"Predicted in {perf_counter() - time_counter} seconds")

        assert len(preds) == len(available_heroes)
        self.latest_predictions = dict(zip(available_heroes, preds))

        assert 0 not in self.latest_predictions.keys()
