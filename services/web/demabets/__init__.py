import eventlet

eventlet.monkey_patch()
import logging
import os
from flask import Flask, send_from_directory
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_admin import Admin
from flask_adminlte3 import AdminLTE3
from werkzeug.middleware.proxy_fix import ProxyFix
from demabets.config import Config
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

logging.basicConfig(level=logging.INFO)
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
socketio = SocketIO()
csrf = CSRFProtect()
mail = Mail()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)
admin = Admin(name='Dashboard', template_mode='bootstrap4', base_template='myadmin3/my_master.html')
adminlt3 = AdminLTE3()
login_manager = LoginManager()

login_manager.login_view = 'auth.login'
login_manager.session_protection = "strong"
login_manager.login_message_category = "danger"


def create_app(appconfig=Config):
    """
    Factory method for creating the Demabets Flask app.
    https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories/
    """

    app = Flask(__name__)
    app.config.from_object(appconfig)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

    from demabets.models import User
    from demabets.admindash.admin_service import AdminView
    from demabets.admindash.admin_service import MyAdminIndexView

    admin.init_app(app, index_view=MyAdminIndexView())
    adminlt3.init_app(app)
    db.init_app(app)
    socketio.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """
        Loader used to reload the user object from the user ID stored in the session.
        https://flask-login.readthedocs.io/en/latest/#how-it-works
        """
        return User.query.get(int(user_id))

    @app.context_processor
    def utility_processor():
        def round_num(num):
            return round(num)

        def image_exist(pseudo):
            if os.path.isfile(f'demabets/static/img/players/{pseudo}.jpg'):
                return pseudo
            else:
                pseudo = 'missing'
            return pseudo

        def epoch_datetime(epoch):
            import datetime
            epoch = epoch / 1000
            return datetime.datetime.utcfromtimestamp(epoch).strftime('%d %b %Y - %H:%M')

        def datetime_humanize(date):
            return date.strftime('%d %b %Y - %H:%M')

        def now_epoch():
            from datetime import datetime
            return datetime.now().timestamp() * 1000

        return dict(round_num=round_num, image_exist=image_exist, epoch_datetime=epoch_datetime, reversed=reversed,
                    now_epoch=now_epoch, datetime_humanize=datetime_humanize)

    @app.route("/static/<path:filename>")
    def staticfiles(filename):
        return send_from_directory(app.config["STATIC_FOLDER"], filename)

    from demabets.auth import auth_blueprint
    from demabets.admindash import admindash_blueprint
    from demabets.betting import betting_blueprint
    from demabets.chat import chat_blueprint
    from demabets.email_factory import email_blueprint
    from demabets.frontpage import frontpage_blueprint
    from demabets.game import game_blueprint
    from demabets.notifications import notifications_blueprint
    from demabets.profile import profile_blueprint
    from demabets.refferals import refferals_blueprint
    from demabets.wallet import wallet_blueprint
    from demabets.cli import cli_app_group

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(admindash_blueprint)
    app.register_blueprint(betting_blueprint)
    app.register_blueprint(chat_blueprint)
    app.register_blueprint(email_blueprint)
    app.register_blueprint(frontpage_blueprint)
    app.register_blueprint(game_blueprint)
    app.register_blueprint(notifications_blueprint)
    app.register_blueprint(profile_blueprint)
    app.register_blueprint(refferals_blueprint)
    app.register_blueprint(wallet_blueprint)
    app.cli.add_command(cli_app_group)

    @app.before_first_request
    def init_app():
        from demabets.utils import get_btc_price_data
        from demabets.game.game_service import update_matches
        from demabets.wallet.wallet_service import get_tx_receive
        from demabets.utils import create_first_user

        with app.app_context():
            create_first_user()

        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        logger.info('Task scheduler started')
        cron = BackgroundScheduler(job_defaults=job_defaults)
        cron.add_job(get_btc_price_data, "cron", minute="10")
        cron.add_job(update_matches, "cron", args=[app], second="59")
        cron.add_job(get_tx_receive, "cron", args=[app], second="59")
        get_btc_price_data()
        cron.start()
        atexit.register(lambda: cron.shutdown())

    return app
