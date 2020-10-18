"""
Models for everything relating to people (users, members, etc)
"""


from hub import db


class Subscriber(db.Model):
    """
    A user who has subscribed to the mailing list
    """

    email     = db.Column(db.String(1024), primary_key=True)
    name      = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return '<Subscriber %s>' % self.email

    def __str__(self):
        return '%s <%s>' % str(self.name).title