from markdown import markdown

from hub import db
from hub.models.membership import Person
from hub.services import email


email_recipients = db.Table('email_recipients', 
    db.Column('email_id', db.Integer, db.ForeignKey('email.id'), primary_key=True),
    db.Column('person_id', db.String(10), db.ForeignKey('person.id'), primary_key=True)
)


class Email(db.Model):
    
    id                 = db.Column(db.Integer, primary_key=True)
    subject            = db.Column(db.String(1024))
    from_user_id       = db.Column(db.String(10))
    created_at         = db.Column(db.DateTime)
    body               = db.Column(db.Text)
    sent_at            = db.Column(db.DateTime, nullable=True)
    hold_until         = db.Column(db.DateTime, nullable=True)
    status             = db.Column(db.String(10))
    type               = db.Column(db.String(3), default='STD')
    to_all_members     = db.Column(db.Boolean, default=False)

    recipients = db.relationship('Person', secondary=email_recipients, lazy='subquery', 
                                  backref=db.backref('emails', lazy=True))


    def send(self):
        if self.status in ('SENT', 'DRAFT', 'DELETED', 'ARCHIVED'):
            return

        html = markdown(self.body)

        if self.to_all_members:
            subs = People.query.all()
        else:
            subs = self.recipients

        for recipient in subs:
            email.send_email(recipient=str(recipient),
                             subject=self.subject,
                             body_html=html,
                             body_text=self.body)

