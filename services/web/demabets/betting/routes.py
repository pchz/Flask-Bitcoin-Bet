import uuid
from datetime import datetime

from flask import redirect, url_for, request, flash
from flask_login import login_required, current_user

from demabets import db
from demabets.betting import betting_blueprint
from demabets.models import Bet, Game, Transaction
from demabets.frontpage.frontpage_service import update_odds


@betting_blueprint.route('/bet', methods=['GET', 'POST'])
@login_required
def bet_post():
    if request.form.getlist('gameIdentifier'):
        for gameid, amount, winner_choice in zip(request.form.getlist('gameIdentifier'),
                                                 request.form.getlist('bet_amount'),
                                                 request.form.getlist('winner_choice')):

            date = datetime.now().timestamp()
            email = current_user.email
            account_id = current_user.id
            status = "RECEIVED"
            bet_won = False
            if amount == '':
                amount = 0.0
            else:
                try:
                    amount = int(float(amount) * 100000000)
                except:
                    amount = 0.0

            if winner_choice == "True":
                winner_choice = True  # No sheeeeeeeeeeet
            elif winner_choice == "False":
                winner_choice = False
            else:
                flash('You need to choose a winner', 'is-danger')
                return redirect(url_for('frontpage.index'))

            # Maybe we can just say that if they try to bet on a game that doesn't exist, they deserve to lose their
            # money ?

            game_data = Game.query.get(gameid)

            # Catching errors
            if (datetime.now().timestamp() * 1000) - game_data.start_time > 600000:
                flash('Bets are closed', 'is-danger')
                return redirect(url_for('frontpage.index'))
            elif game_data is None:
                flash('Invalid Game ID', 'is-danger')
                return redirect(url_for('frontpage.index'))
            elif not amount:
                flash('You need to enter an amount', 'is-danger')
                return redirect(url_for('frontpage.index'))
            elif not gameid:
                flash('Invalid Game ID', 'is-danger')
                return redirect(url_for('frontpage.index'))
            elif amount == 0.0:
                flash("Amount can't be equal to 0", 'is-danger')
                return redirect(url_for('frontpage.index'))
            elif amount > current_user.balance:
                flash('Insuficient funds.', 'is-danger')
                return redirect(url_for('frontpage.index'))
            # Everything is good probably
            else:
                bet_id = str(uuid.uuid4())

                # Withdraw bet amount from the user balance

                previous_balance = current_user.balance
                new_balance = previous_balance - amount
                current_user.balance = new_balance
                current_user.amount_inplay += amount

                new_bet = Bet(id=bet_id, gameid=gameid, date=date, email=email, account_id=account_id, status=status,
                              bet_won=bet_won, bet_amount=amount, winner_choice=winner_choice, name=game_data.pseudo)

                new_tx = Transaction(type="Bet", user_id=account_id, amount=amount, previous_balance=previous_balance,
                                     new_balance=new_balance)

                db.session.add(new_tx)
                db.session.add(new_bet)

                if current_user.first_bet:
                    current_user.first_bet = False

                db.session.commit()
                update_odds()
                flash('Bet confirmed.', 'is-info')

        return redirect(url_for('frontpage.index'))

    else:
        flash('Betting slip is empty', 'is-danger')
        return redirect(url_for('frontpage.index'))
