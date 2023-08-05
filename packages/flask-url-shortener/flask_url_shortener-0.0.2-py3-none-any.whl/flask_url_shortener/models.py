import os
from datetime import datetime


def init_models(db, endpoint: str, link_table_name: str, click_table_name: str, keep_ip: bool, keep_useragent: bool):
    class Link(db.Model):
        __tablename__ = link_table_name
        id = db.Column(db.Integer(), primary_key=True)
        url = db.Column(db.String(), nullable=False)
        title = db.Column(db.String, nullable=True)
        uid = db.Column(db.String(), unique=True, nullable=False)
        created = db.Column(db.DateTime(), default=datetime.utcnow)
        clicks = db.relationship('Click', back_populates='link')

        @property
        def link(self):
            return os.path.join(endpoint, self.uid)

        def __repr__(self):
            return f'<Link {self.uid}>'

    class Click(db.Model):
        __tablename__ = click_table_name
        id = db.Column(db.Integer(), primary_key=True)
        link_id = db.Column(db.Integer(), db.ForeignKey(f'{link_table_name}.id'))
        link = db.relationship('Link', back_populates='clicks')
        at = db.Column(db.DateTime(), default=datetime.utcnow)
        ip = db.Column(db.String())
        user_agent = db.Column(db.String())

        def __repr__(self):
            return f'<Click {self.at} for {self.link.uid}>'

    return Link, Click
