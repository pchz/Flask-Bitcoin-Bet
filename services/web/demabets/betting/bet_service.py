from datetime import datetime

from demabets.refferals.refferals_service import get_reffered_by

from demabets import db
from demabets.models import Bet, Game, User, Transaction, Comission


def update_bets(gameid):
    admin = User.query.get(1)
    calculate_payout(gameid)
    game = Game.query.get(gameid)
    for bet in Bet.query.filter_by(gameid=gameid).all():
        if not bet.finished:
            if bet.status == "IN_PLAY":
                if game.pseudo_win == bet.winner_choice and game.finished is True:
                    bet.bet_won = True
                    bet.status = "FINISHED"
                    bet.finished = True
                    this_user = User.query.get(bet.account_id)

                    previous_balance = this_user.balance
                    new_balance = previous_balance + bet.payout
                    this_user.balance = new_balance

                    this_user.amount_inplay -= bet.bet_amount

                    new_tx = Transaction(type="Payout", user_id=bet.account_id, amount=bet.payout,
                                         previous_balance=previous_balance,
                                         new_balance=new_balance)

                    db.session.add(new_tx)

                    if bet.comission > 0:
                        refferer = get_reffered_by(this_user.affiliation.uuid)
                        if refferer:

                            website_comission = bet.comission * 0.7
                            refferer_comission = bet.comission * 0.3

                            new_comission_ref = Comission(this_user.id, refferer_comission, refferer[0],
                                                          this_user.affiliation.uuid)
                            new_comission_ws = Comission(this_user.id, website_comission, admin.affiliation.uuid,
                                                         this_user.affiliation.uuid)

                            db.session.add(new_comission_ref)
                            db.session.add(new_comission_ws)

                        else:
                            website_comission = bet.comission
                            new_comission_ws = Comission(this_user.id, website_comission, admin.affiliation.uuid,
                                                         this_user.affiliation.uuid)
                            db.session.add(new_comission_ws)

                    db.session.commit()

                elif game.pseudo_win != bet.winner_choice and game.finished is True:
                    this_user = User.query.get(bet.account_id)

                    this_user.amount_inplay -= bet.bet_amount

                    bet.bet_won = False
                    bet.status = "FINISHED"
                    db.session.commit()

            elif bet.status == "PENDING" and game.finished is True:
                bet.bet_won = False
                bet.status = "CANCELED"
                this_user = User.query.get(bet.account_id)
                previous_balance = this_user.balance
                new_balance = previous_balance + bet.bet_amount
                this_user.balance = new_balance

                this_user.amount_inplay -= bet.bet_amount

                new_tx = Transaction(type="Refund", user_id=bet.account_id, amount=bet.payout,
                                     previous_balance=previous_balance,
                                     new_balance=new_balance)

                db.session.add(new_tx)

                db.session.commit()


def cancel_game_bool(gameid):
    calculate_payout(gameid)
    game = Game.query.get(gameid)
    if (datetime.now().timestamp() * 1000) - game.start_time > 600000:
        if Bet.query.filter_by(gameid=gameid).count() >= 1:
            for bet in Bet.query.filter_by(gameid=gameid).all():
                if not bet.finished:
                    if bet.status == "PENDING":
                        return True
                    else:
                        return False
        else:
            return True

    else:
        return False


def calculate_payout(gameid):
    payout_win = 0
    payout_lose = 0
    this_game_bet = Bet.query.filter_by(gameid=gameid).all()
    for bet in this_game_bet:
        if bet.winner_choice:
            payout_win += bet.bet_amount
        else:
            payout_lose += bet.bet_amount

    if payout_lose > 0 and payout_win > 0:
        for bet in this_game_bet:
            bet.status = "IN_PLAY"
            if bet.winner_choice:
                bet.payout = (bet.bet_amount / payout_win * payout_lose) * 0.80 + bet.bet_amount
                bet.comission = (bet.bet_amount / payout_win * payout_lose) * 0.20
            else:
                bet.payout = (bet.bet_amount / payout_lose * payout_win) * 0.80 + bet.bet_amount
                bet.comission = (bet.bet_amount / payout_lose * payout_win) * 0.20
            db.session.commit()

    elif payout_win > 0 and payout_lose == 0:
        for bet in this_game_bet:
            bet.status = "PENDING"
            bet.payout = bet.bet_amount
            bet.comission = 0
            db.session.commit()
        # return 1, 1

    elif payout_win == 0 and payout_lose > 0:
        for bet in this_game_bet:
            bet.status = "PENDING"
            bet.payout = bet.bet_amount
            bet.comission = 0
            db.session.commit()
        # return 1, 1

    else:
        for bet in this_game_bet:
            bet.status = "PENDING"
            bet.payout = bet.bet_amount
            bet.comission = 0
            db.session.commit()


def calculate_odds(gameid):
    payout_win = 0
    payout_lose = 0
    this_game_bet = Bet.query.filter_by(gameid=gameid).all()

    for bet in this_game_bet:
        if bet.winner_choice:
            payout_win += bet.bet_amount
        else:
            payout_lose += bet.bet_amount

    if payout_lose > 0 and payout_win > 0:
        odds_lose: float = 1 + payout_win / payout_lose
        odds_win: float = 1 + payout_lose / payout_win
        bank = payout_win + payout_lose
        return round(odds_win, 2), round(odds_lose, 2), round(bank, 8)

    else:
        bank = payout_win + payout_lose
        return 1.0, 1.0, round(bank, 8)



