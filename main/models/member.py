# -*- coding: utf-8 -*-
import random
import string
import hashlib
from datetime import datetime
from database import db
from common import Log


class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, default='')
    postal_code = db.Column(db.String(20), nullable=False, default='')
    province_name = db.Column(db.String(50), nullable=False, default='')
    city_name = db.Column(db.String(50), nullable=False, default='')
    county_name = db.Column(db.String(50), nullable=False, default='')
    detail_info = db.Column(db.String(200), nullable=False, default='')
    national_code = db.Column(db.String(20), nullable=False, default='')
    tel_number = db.Column(db.String(30), nullable=False, default='')
    uid = db.Column(db.Integer, db.ForeignKey('member.id'))

    def __repr__(self):
        return "<Model Address `{}`>".format(self.name)

    def __str__(self):
        return self.name + ' ' \
               + self.province_name + ' ' + self.city_name + ' ' + self.county_name + ' ' + self.detail_info + ' ' \
               + self.tel_number


class Member(db.Model):
    """Represents protected member."""
    __tablename__ = 'member'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    national_id = db.Column(db.String(20), nullable=False, default='', index=True)
    nickname = db.Column(db.String(50), nullable=False, default='')
    birthday = db.Column(db.String(20))
    mobile = db.Column(db.String(20), nullable=False, index=True)
    password = db.Column(db.String(50), nullable=False, default='')
    sex = db.Column(db.Integer, default=0)
    avatar = db.Column(db.String(200))
    salt = db.Column(db.String(32))
    reg_ip = db.Column(db.String(20))
    status = db.Column(db.Integer, nullable=False, default=0)
    blocked_info = db.Column(db.Text)
    language = db.Column(db.String(20))
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_time = db.Column(db.DateTime, default=datetime.now)
    addresses = db.relationship('Address', backref='member', lazy='dynamic')

    def __repr__(self):
        return "<Model Member `{}`>".format(self.nickname)

    def __str__(self):
        return self.nickname

    @property
    def gene_Salt(self):
        key_list = [random.choice((string.ascii_letters + string.digits)) for i in range(20)]
        return "".join(key_list)

    @property
    def gene_Token(self):
        m = hashlib.md5()
        temp = "%s-%s-%s" % (str(self.id), self.salt, self.status)
        m.update(temp.encode("utf-8"))
        return m.hexdigest()
