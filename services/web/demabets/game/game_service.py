import logging
from typing import TypedDict

from demabets.utils import readjson

logger = logging.getLogger(__name__)


class GameDto(TypedDict):
    gameid: int
    gameStartTime: int
    winner: int
    finished: bool
    participants: list
    pseudo: str
    pseudo_team: int
    pseudo_win: bool


class ParticipantDto(TypedDict):
    summonerName: str
    teamId: int
    championId: str


def check_summoner_exist(summoner_name) -> bool:
    """
    Check if summoner name matches a player in our ladder.json file
    :param summoner_name
    :return: Bool
    """
    d = readjson(f'ladder.json')
    do_exist = False
    for player in d:
        if player['account']['summoner_name'] == summoner_name:
            do_exist = True
    return do_exist


def update_matches(app):
    logger.info('Game scanning task started')
    # Adds and updates the games
    # Redacted
