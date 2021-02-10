from demabets import admin, db
from demabets.admindash.admin_service import AdminLTEModelView, UserView, TransactionView, TransactionBisView
from demabets.models import User, Transaction, Comission, Game, Bet, Withdrawal, Deposit, BitcoinReceived, Chat
from flask_admin.menu import MenuLink

admin.add_view(UserView(User, db.session))
admin.add_view(TransactionView(Transaction, db.session, category="Transactions"))
admin.add_view(TransactionBisView(Comission, db.session, category="Transactions"))
admin.add_view(TransactionBisView(Withdrawal, db.session, category="Transactions"))
admin.add_view(TransactionBisView(Deposit, db.session, category="Transactions"))
admin.add_view(TransactionBisView(BitcoinReceived, db.session, category="Transactions"))
admin.add_view(AdminLTEModelView(Chat, db.session))
admin.add_view(AdminLTEModelView(Game, db.session))
admin.add_view(AdminLTEModelView(Bet, db.session))

admin.add_link(MenuLink(name='Back Home', class_name='nav-item', endpoint='frontpage.index'))