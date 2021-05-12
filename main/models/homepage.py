# -*- coding: utf-8 -*-
from datetime import datetime
from trialcenter.models import db
from trialcenter.models.trial import Trial


class Focus(db.Document):
    """Represents protected member."""
    meta = {
        'collection': 'focus',
        'ordering': ['order'],
    }

    order = db.IntField(min_value=1, unique=True)
    title = db.StringField(required=True)
    image = db.StringField(max_length=200)
    source_type = db.StringField(default='', max_length=10)  # 焦点类型，试用、报告
    trial_id = db.ObjectIdField()
    updated_time = db.DateTimeField(default=datetime.now())
    created_time = db.DateTimeField(default=datetime.now())

    @property
    def active(self):
        if self.source_type == 'trial':
            if Trial.objects(id=self.trial_id).first().end_time > datetime.now():
                return True
        return False

    def __repr__(self):
        return "<Model Focus `{}`>".format(self.title)

    def __str__(self):
        return self.title


class Banner(db.Document):
    """Represents protected member."""
    meta = {
        'collection': 'banner',
    }
    position = db.IntField(default=1)
    click = db.StringField(max_length=200)
    image = db.StringField(max_length=200)
    created_time = db.DateTimeField(default=datetime.now())

    def __repr__(self):
        return "<Model Banner `{}`>".format(self.click)

    def __str__(self):
        return self.click
