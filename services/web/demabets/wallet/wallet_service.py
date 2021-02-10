import logging
import os

from demabets import db
from demabets.models import Deposit, User, BitcoinReceived
from demabets.wallet.bitcoin import BitcoinRPC

logger = logging.getLogger(__name__)

rpc = BitcoinRPC(f'http://{os.getenv("BTC_SERVER")}:{os.getenv("BTC_PORT")}', f'{os.getenv("BTC_USER")}',
                 f'{os.getenv("BTC_PASS")}')


def get_newaddress(accountname):
    return rpc.getnewaddress(accountname)


def get_receivedby(accountname, minconf=2):
    return rpc.getreceivedbylabel(accountname, minconf)


def send_toaddress(toaddress, amount, comment, comment_to):
    # Sats to BTC
    amount = amount / 100000000
    return rpc.sendtoaddress(toaddress, amount, comment, comment_to, True)


def get_tx_receive(app):
    with app.app_context():
        data = rpc.listtransactions("*", 500)

        logger.info(f'  Transaction scanning task started')
        for tx in data:
            amount = tx['amount'] * 100000000
            deposit_tx = Deposit.query.filter_by(txid=tx['txid']).first()
            btc_received = BitcoinReceived.query.filter_by(txid=tx['txid']).first()

            # Check if tx corresponds to a label
            if 'label' in tx:
                # Check if label corresponds to a user
                user = User.query.filter_by(email=tx['label']).first()
                if user:
                    # BitcoinReceived to track confirmed and unconfirmed deposits
                    if btc_received:
                        btc_received.confirmations = tx['confirmations']
                        db.session.commit()
                    elif len(tx['label']) > 4 and not btc_received and tx['category'] == "receive":
                        btc_received = BitcoinReceived(txid=tx['txid'], category="receive", amount=int(amount),
                                                       user_email=tx['label'],
                                                       confirmations=tx['confirmations'],
                                                       timereceived=tx['timereceived'])
                        db.session.add(btc_received)
                        db.session.commit()

                    # Deposit to only track confirmed deposits (for lack of a better solution at 4 am)
                    if tx['confirmations'] > 2 and not deposit_tx and tx['category'] == "receive":
                        previous_balance = user.balance
                        new_balance = previous_balance + amount
                        new_btc_tx = Deposit(txid=tx['txid'], category="receive", amount=int(amount),
                                             user_email=tx['label'],
                                             confirmations=tx['confirmations'], timereceived=tx['timereceived'],
                                             new_balance=new_balance, previous_balance=previous_balance)
                        db.session.add(new_btc_tx)
                        db.session.commit()
