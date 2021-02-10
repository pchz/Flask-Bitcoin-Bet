import json
from flask_socketio import emit
from flask import json, request
from demabets.models import Game
from demabets.utils import image_exist, twitch_exist, get_player_info
from demabets.betting.bet_service import calculate_payout, calculate_odds


from demabets import socketio

def get_games():
    return Game.query.filter_by(finished=False).order_by(Game.start_time.desc()).all()


def get_gamehistory():
    return Game.query.filter_by(finished=True).order_by(Game.start_time.desc()).limit(20)

def update_games():
    games = get_games()

    games_updated = []
    for game in games:
        game_up = {}
        from datetime import datetime
        if datetime.now().timestamp() * 1000 - game.start_time < 600000:
            bet_status = 'Betting opened'
            is_open = True
        else:
            bet_status = 'Betting closed'
            is_open = False
        odds_win, odds_lose, bank = calculate_odds(game.gameid)
        calculate_payout(game.gameid)
        live_stream_url = twitch_exist(game.pseudo)
        player_info = get_player_info(game.pseudo)
        game_up['id'] = game.gameid
        game_up['displayName'] = game.pseudo
        game_up['name'] = game.pseudo.replace(" ", "")
        game_up['displayStatus'] = bet_status
        game_up['isOpen'] = is_open
        game_up['finished'] = game.finished
        game_up['country'] = player_info['country']
        game_up['displayImage'] = image_exist(game.pseudo)
        if live_stream_url:
            game_up['hasLivestream'] = True
            game_up['livestreamUrl'] = twitch_exist(game.pseudo)
        else:
            game_up['hasLivestream'] = False
        game_up['gameStartTime'] = game.start_time
        game_up['oddsLose'] = odds_lose
        game_up['oddsWin'] = odds_win
        game_up['bank'] = bank / 100000000
        game_up['marketTypeCode'] = "Lol_Euw_Mbt"
        games_updated.append(game_up)

    updated = json.dumps(games_updated)

    socketio.emit('data_update', updated, broadcast=True)


def update_odds():
    games = get_games()
    odds_updated = []
    for game in games:
        odd_update = {}
        odds_win, odds_lose, bank = calculate_odds(game.gameid)
        odd_update['oddsLose'] = odds_lose
        odd_update['oddsWin'] = odds_win
        odd_update['displayName'] = game.pseudo
        odd_update['name'] = game.pseudo.replace(" ", "")
        odd_update['bank'] = bank / 100000000
        odds_updated.append(odd_update)

    updated = json.dumps(odds_updated)
    socketio.emit('odds_update', updated, broadcast=True)


@socketio.on('connect')
def update_games_request():
    games = get_games()

    games_updated = []
    for game in games:
        game_up = {}
        from datetime import datetime
        if datetime.now().timestamp() * 1000 - game.start_time < 600000:
            bet_status = 'Betting opened'
            is_open = True
        else:
            bet_status = 'Betting closed'
            is_open = False
        odds_win, odds_lose, bank = calculate_odds(game.gameid)
        calculate_payout(game.gameid)
        live_stream_url = twitch_exist(game.pseudo)
        player_info = get_player_info(game.pseudo)
        game_up['id'] = game.gameid
        game_up['displayName'] = game.pseudo
        game_up['name'] = game.pseudo.replace(" ", "")
        game_up['displayStatus'] = bet_status
        game_up['isOpen'] = is_open
        game_up['finished'] = game.finished
        game_up['country'] = player_info['country']
        game_up['displayImage'] = image_exist(game.pseudo)
        if live_stream_url:
            game_up['hasLivestream'] = True
            game_up['livestreamUrl'] = twitch_exist(game.pseudo)
        else:
            game_up['hasLivestream'] = False
        game_up['gameStartTime'] = game.start_time
        game_up['oddsLose'] = odds_lose
        game_up['oddsWin'] = odds_win
        game_up['bank'] = bank / 100000000
        game_up['marketTypeCode'] = "Lol_Euw_Mbt"
        games_updated.append(game_up)

    updated = json.dumps(games_updated)
    emit('data_update', updated, room=request.sid)