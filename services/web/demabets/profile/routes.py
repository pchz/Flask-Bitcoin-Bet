import logging
from datetime import datetime

import xxhash
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash

from demabets import db
from demabets.models import Transaction, Bet, Chat, Withdrawal
from demabets.profile import profile_blueprint
from demabets.utils import getBtcPrice
from demabets.wallet.wallet_service import get_newaddress

logger = logging.getLogger(__name__)


@profile_blueprint.route('/profile')
@login_required
def profile():
    refferal_code = current_user.affiliation.uuid
    transactions = current_user.transactions.order_by(Transaction.time_created.desc())
    unconfirmed = 0
    for tx in current_user.btc_received.all():
        if tx.confirmations <= 2:
            unconfirmed += tx.amount

    if current_user.deposit_address is None:
        current_user.deposit_address = get_newaddress(current_user.email)
        db.session.commit()

    btc_balance = round(current_user.balance) / 100000000
    inplay_btc = round(current_user.amount_inplay) / 100000000
    unconfirmed_balance = round(unconfirmed) / 100000000

    transactions_count = transactions.count()

    return render_template('profile.html', title="Profile", name=current_user.username,
                           btc_balance=round(btc_balance, 8),
                           receive_addr=current_user.deposit_address, in_play=round(inplay_btc, 8),
                           refferal_code=refferal_code,
                           transactions=transactions, transactions_count=transactions_count,
                           unconfirmed_balance=unconfirmed_balance)


@profile_blueprint.route('/history')
@login_required
def history():
    btc_balance = round(current_user.balance) / 100000000
    messages = Chat.query.all()
    bets = Bet.query.filter_by(account_id=current_user.id)
    bets_fancy_list = []
    for bet in bets:

        # data from database but fancier to display.

        bets_fancy = {}

        bets_fancy["amount"] = round(round(bet.bet_amount) / 100000000, 8)
        bets_fancy["payout"] = round(round(bet.payout) / 100000000, 8)
        bets_fancy["name"] = bet.name

        if bet.winner_choice:
            bets_fancy["winner_choice"] = f"{bet.name} to Win"
        else:
            bets_fancy["winner_choice"] = f"{bet.name} to Lose"

        if bet.status == 'IN_PLAY':
            bets_fancy["status"] = "In play"
            if not bet.bet_won:
                bets_fancy["bet_won"] = "Ongoing"
            if bet.bet_won:
                bets_fancy["bet_won"] = "Ongoing"
        elif bet.status == 'PENDING':
            bets_fancy["status"] = "Pending"
            if not bet.bet_won:
                bets_fancy["bet_won"] = "Ongoing"
            if bet.bet_won:
                bets_fancy["bet_won"] = "Ongoing"
        elif bet.status == 'CANCELED':
            bets_fancy["status"] = "Canceled"
            if not bet.bet_won:
                bets_fancy["bet_won"] = "Refund"
            if bet.bet_won:
                bets_fancy["bet_won"] = "Refund"
        elif bet.status == "FINISHED":
            bets_fancy["status"] = "Finished"
            if not bet.bet_won:
                bets_fancy["bet_won"] = "Lost"
            if bet.bet_won:
                bets_fancy["bet_won"] = "Won"

        bets_fancy['date'] = datetime.fromtimestamp(bet.date).strftime('%Y-%m-%d %H:%M:%S')
        bets_fancy['id'] = xxhash.xxh32(bet.id).hexdigest()

        bets_fancy_list.append(bets_fancy)

    return render_template('history.html', title="History", btc_balance=round(btc_balance, 8), bets=bets_fancy_list,
                           messages=messages, btc_usd=getBtcPrice("USD"))


@profile_blueprint.route('/withdraw', methods=['POST'])
@login_required
def send():
    withdraw_addr = request.form.get('withdrawal_address')
    amount = float(request.form.get('amount'))
    amount = amount * 100000000
    amount = int(amount)
    password_form = request.form.get('password')

    # This needs to be a form.

    if not request.form.get('amount') and withdraw_addr:
        flash("Fields can't be empty", 'is-danger')
        return redirect(url_for('profile.profile'))
    elif not request.form.get('amount') or not withdraw_addr:
        flash("Fields can't be empty", 'is-danger')
        return redirect(url_for('profile.profile'))
    elif amount == 0.0:
        flash("Amount can't be equal to 0", 'is-danger')
        return redirect(url_for('profile.profile'))
    elif amount > current_user.balance:
        flash('Insuficient funds.', 'is-danger')
        return redirect(url_for('profile.profile'))
    elif not check_password_hash(current_user.password, password_form):
        flash('Wrong password.', 'is-danger')
        return redirect(url_for('profile.profile'))
    elif amount <= current_user.balance:
        try:
            previous_balance = current_user.balance
            new_balance = previous_balance - amount

            new_withdrawal = Withdrawal(user_id=current_user.id, amount=amount, address=withdraw_addr,
                                        previous_balance=previous_balance, new_balance=new_balance)

            db.session.add(new_withdrawal)
            db.session.commit()

            flash('Withdrawal sent. It may take up to 2 hours for the transaction to be confirmed',
                  'is-info')

            return redirect(url_for('profile.profile'))

        except Exception as e:
            logger.error(e)

            flash('An error occured', 'is-danger')

            return redirect(url_for('profile.profile'))

    return redirect(url_for('profile.profile'))
