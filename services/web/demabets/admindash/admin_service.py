from flask import redirect, url_for, request
from flask_admin import expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from demabets.models import Bet, User


class AdminView(ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_folder = 'static'

    def create_blueprint(self, admin):
        blueprint = super(AdminView, self).create_blueprint(admin)
        blueprint.name = '{}_admin'.format(blueprint.name)
        return blueprint

    def get_url(self, endpoint, **kwargs):
        if not (endpoint.startswith('.') or endpoint.startswith('admin.')):
            endpoint = endpoint.replace('.', '_admin.')
        return super(AdminView, self).get_url(endpoint, **kwargs)

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.admin:
            return True

        return False

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('frontpage.index', next=request.url))


class AdminLTEModelView(AdminView):
    list_template = 'flask-admin/model/list.html'
    create_template = 'flask-admin/model/create.html'
    edit_template = 'flask-admin/model/edit.html'
    details_template = 'flask-admin/model/details.html'

    create_modal_template = 'flask-admin/model/modals/create.html'
    edit_modal_template = 'flask-admin/model/modals/edit.html'
    details_modal_template = 'flask-admin/model/modals/details.html'


class MyAdminIndexView(AdminIndexView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        new_users = User.query.order_by(User.time_created.desc()).limit(10)
        total_earnings = float(current_user.affiliation.total_earnings / 100000000)
        user_count = User.query.count()
        bet_count = Bet.query.count()
        return self.render('myadmin3/my_index.html', new_users=new_users, total_earnings=total_earnings,
                           user_count=user_count, bet_count=bet_count)

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.admin:
            return True

        return False

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('frontpage.index', next=request.url))


class MyBaseModelview(AdminLTEModelView):
    page_size = 50  # the number of entries to display on the list view

    can_export = False
    can_view_details = True
    edit_modal = True
    create_modal = True
    details_modal = True


class UserView(AdminLTEModelView):
    column_exclude_list = ['password', ]
    column_searchable_list = ['username', 'email']
    can_export = True
    can_view_details = True
    edit_modal = True
    create_modal = True
    details_modal = True


class TransactionView(AdminLTEModelView):
    column_searchable_list = ['user_id', 'type']
    can_export = True
    can_view_details = True
    edit_modal = False
    create_modal = False
    details_modal = True
    can_create = False
    can_edit = False
    can_delete = False


class TransactionBisView(AdminLTEModelView):
    can_export = True
    can_view_details = True
    edit_modal = False
    create_modal = False
    details_modal = True
    can_create = False
    can_edit = False
    can_delete = False


class GameView(AdminLTEModelView):
    page_size = 50  # the number of entries to display on the list view
    column_searchable_list = ['riot_gameid', 'pseudo']
