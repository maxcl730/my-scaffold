# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from contextlib import contextmanager


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()  # 事务
        except Exception as e:
            self.session.rollback()  # 回滚
            raise e


db = SQLAlchemy()


