import logging
import os
from datetime import datetime

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from demabets import db
from demabets import limiter
from demabets.auth import auth_blueprint
from demabets.auth.forms import LoginForm, SignupForm, ResetPasswordRequestForm, ResetPasswordForm
from demabets.email_factory.email_service import send_confirmation_email
from demabets.email_factory.email_service import send_password_reset_email
from demabets.models import User, Affiliation
from demabets.refferals.refferals_service import get_affiliation_user
from demabets.wallet.wallet_service import get_newaddress

logger = logging.getLogger(__name__)


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR']

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, form.password.data):
            logger.info(f'Failed login attempt from {ip}')
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=form.remember.data)
        logger.info(f'Successful login attempt from {ip} for {user.id}')
        if user.first_login:
            user.first_login = False
            db.session.commit()
            return redirect(url_for('frontpage.index'))
        else:
            return redirect(url_for('frontpage.index'))

    return render_template('login.html', form=form, title='Login')


@auth_blueprint.route('/signup', methods=['GET', 'POST'])
@limiter.limit("5 per day")
def signup():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR']

    try:
        referring_uuid = request.cookies.get('referring_uuid')

    except:
        referring_uuid = False

    form = SignupForm()
    if form.validate_on_submit():
        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        # noinspection PyArgumentList
        deposit_address = get_newaddress(form.email.data)
        new_user = User(email=form.email.data, username=form.username.data,
                        password=generate_password_hash(form.password.data, method='sha256'),
                        deposit_address=deposit_address)

        db.session.add(new_user)
        db.session.commit()
        user = User.query.filter_by(email=form.email.data).first()
        referred_user = Affiliation(user.id)
        db.session.add(referred_user)
        db.session.commit()

        if bool(os.getenv("SEND_MAIL")):
            send_confirmation_email(user)
        else:
            user.confirmed = True
            user.confirmed_on = datetime.now()
            db.session.commit()

        if referring_uuid:
            referring_user = get_affiliation_user(referring_uuid)
            referring_user.referred.append(referred_user)
            db.session.commit()

        logger.info(f'Signup from {ip}')

        return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form, title='Signup')


@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('frontpage.index'))


@auth_blueprint.route('/request_reset', methods=['GET', 'POST'])
@limiter.limit("5 per day")
def request_reset():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR']

    if current_user.is_authenticated:
        logout_user()

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bool(os.getenv("SEND_MAIL_RESET")):
                send_password_reset_email(user)
            else:
                flash('Password reset is disabled')
                return redirect(url_for('auth.login'))

            logger.info(f'Password reset sent from {ip} for user {user.id}')

        else:
            logger.info(f'Unsuccessful password reset request from {ip}')

        flash('Check your email for the instructions to reset your password')

        return redirect(url_for('auth.login'))

    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@auth_blueprint.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR']

    if current_user.is_authenticated:
        return redirect(url_for('frontpage.index'))

    user = User.verify_reset_password_token(token)

    if not user:
        logger.info(f'Failed password reset by {ip} for user {user.id}')
        return redirect(url_for('frontpage.index'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        logger.info(f'Successful password reset by {ip} for user {user.id}')
        db.session.commit()
        flash('Your password has been reset.')

        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', form=form, title='Reset Password')


@auth_blueprint.route('/confirm/<token>')
def confirm_email(token):
    user = User.verify_confirmation_token(token)
    if not user:
        return 'Sup', 418
    else:
        if not user.confirmed:
            user.confirmed = True
            user.confirmed_on = datetime.now()
            return redirect(url_for('frontpage.index'))
        else:
            return redirect(url_for('frontpage.index'))
