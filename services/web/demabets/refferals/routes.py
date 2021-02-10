from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required

from demabets import db
from demabets.models import Comission, Transaction
from demabets.refferals import refferals_blueprint
from demabets.refferals.refferals_service import get_referrals


@refferals_blueprint.route('/affiliate/dashboard')
@login_required
def dashboard():
    btc_balance = current_user.balance / 100000000
    refferal_code = current_user.affiliation.uuid
    total_earnings = float(current_user.affiliation.total_earnings / 100000000)
    available_earnings = float(current_user.affiliation.available_earnings / 100000000)
    reffered_users_count = get_referrals(refferal_code)
    comissions = current_user.affiliation.comissions.order_by(Comission.time_created.desc())
    comissions_count = comissions.count()

    return render_template('refferals_dashboard.html', title="Affiliate dashboard", btc_balance=btc_balance,
                           refferal_code=refferal_code, total_earnings=total_earnings,
                           available_earnings=available_earnings,
                           comissions=comissions, comissions_count=comissions_count,
                           reffered_users_count=reffered_users_count)


@refferals_blueprint.route('/affiliate/claim')
@login_required
def claim():
    amount = current_user.affiliation.available_earnings

    if amount > 0:
        previous_balance = current_user.balance
        new_balance = previous_balance + amount
        current_user.balance = new_balance
        current_user.affiliation.available_earnings = 0

        new_tx = Transaction(type="Comission Claim", user_id=current_user.id, amount=amount,
                             previous_balance=previous_balance, new_balance=new_balance)

        db.session.add(new_tx)
        db.session.commit()

        flash(f'{amount} satoshis have been added to your account balance', 'is-success')
        return redirect(url_for('refferals.dashboard'))

    else:
        flash("You have no claimable comissions", 'is-danger')
        return redirect(url_for('refferals.dashboard'))
