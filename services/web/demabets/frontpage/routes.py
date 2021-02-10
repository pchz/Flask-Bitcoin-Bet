from flask import render_template, make_response
from flask_login import current_user

from demabets.frontpage import frontpage_blueprint
from demabets.models import Game, Chat
from demabets.utils import getBtcPrice


def get_games():
    return Game.query.filter_by(finished=False).order_by(Game.start_time.desc()).all()


def get_gamehistory():
    return Game.query.filter_by(finished=True).order_by(Game.start_time.desc()).limit(6)


@frontpage_blueprint.route('/')
def index():
    games_history = get_gamehistory()
    messages = Chat.query.all()
    if current_user.is_authenticated:
        btc_balance = round(current_user.balance) / 100000000
    else:
        btc_balance = 0.0

    return render_template('index.html', title="Best League Bets", games_history=games_history,
                           messages=messages, btc_balance=round(btc_balance, 8), btc_usd=getBtcPrice("USD"))


@frontpage_blueprint.route('/ref/<referring_uuid>')
def handle_referal(referring_uuid):
    games_history = get_gamehistory()
    messages = Chat.query.limit(20).all()
    if current_user.is_authenticated:
        btc_balance = round(current_user.balance) / 100000000
    else:
        btc_balance = 0.0

    resp = make_response(
        render_template('index.html', title="Best League Bets", games_history=games_history,
                        messages=messages, btc_balance=round(btc_balance, 8), btc_usd=getBtcPrice("USD")
                        )
    )

    resp.set_cookie('referring_uuid', referring_uuid, max_age=2592000, secure=True, httponly=True, samesite='Lax')
    return resp


@frontpage_blueprint.route('/privacy')
def privacy():
    if current_user.is_authenticated:
        btc_balance = round(current_user.balance) / 100000000
    else:
        btc_balance = 0.0

    return render_template('about.html', title="About", btc_balance=btc_balance)


@frontpage_blueprint.route('/terms')
def terms():
    if current_user.is_authenticated:
        btc_balance = round(current_user.balance) / 100000000
    else:
        btc_balance = 0.0

    return render_template('tos.html', title="TOS", btc_balance=btc_balance)


@frontpage_blueprint.route('/begginers')
def begginers():
    if current_user.is_authenticated:
        btc_balance = round(current_user.balance) / 100000000
    else:
        btc_balance = 0.0

    return render_template('begginers.html', title="Begginers guide", btc_balance=btc_balance)
