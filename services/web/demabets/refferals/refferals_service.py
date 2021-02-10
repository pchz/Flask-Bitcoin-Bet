from demabets import db
from demabets.models import Affiliation, referrals


def get_affiliation_user(uuid):
    return Affiliation.query.filter_by(uuid=uuid).one_or_none()


def get_referrals(uuid):
    affiliation_user = get_affiliation_user(uuid)
    return affiliation_user.referred.filter(
        referrals.c.referring == affiliation_user.uuid).count()


def get_reffered_by(uuid):
    referer = db.session.query(referrals.c.referring).filter(referrals.c.referred == uuid).one_or_none()
    return referer

