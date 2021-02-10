import logging
import os
from dataclasses import dataclass
from time import time

import jwt
from flask_login import UserMixin

from demabets.utils import generate_simple_uuid
from . import db

logger = logging.getLogger(__name__)

# Redacted

class User(db.Model, UserMixin):
    """Model that represents a user"""

    def __repr__(self):
        return f"<User (id='{self.id}', username='{self.username}')>"


referrals = db.Table(
    'referral',
    db.Column('referring', db.String(8), db.ForeignKey('affiliation.uuid')),
    db.Column('referred', db.String(8), db.ForeignKey('affiliation.uuid')),
    db.PrimaryKeyConstraint('referring', 'referred', name='referrals_pk')
)


class Affiliation(db.Model):
    """Model that represents an Affiliation"""

    def __repr__(self):
        return f"<Affiliation (id='{self.user.id}', username='{self.user.username}')>"


class Bet(db.Model):
    """Model that represents a Bet"""


class Chat(db.Model):
    """Model that represents a Chat message"""

    def __repr__(self):
        return f"<Chat (id='{self.id}', username='{self.username}')>"


class Transaction(db.Model):
    """Model that represents a Transaction"""

    def __repr__(self):
        return f"<Tx (id='{self.id}', username='{self.user.username}')>"


class Comission(db.Model):
    """Model that represents a Comission"""


class Withdrawal(db.Model):
    """Model that represents a Btc withdrawal. Executes the withdrawal on init"""


class Deposit(db.Model):
    """Model that represents a Deposit"""


class BitcoinReceived(db.Model):
    """Model that represents all incoming transactions"""




class Promocodes(db.Model):



@dataclass
class Game(db.Model):
    """Model that represents a game."""

