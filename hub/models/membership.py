"""
Models for everything relating to people (users, members, etc)
"""


from hub import db


class Person(db.Model):
    """
    A user who has subscribed to the mailing list
    """

    id        = db.Column(db.String(10), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name  = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)


    def __repr__(self):
        return '<Member %s>' % self.id

    