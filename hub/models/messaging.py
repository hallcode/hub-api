from markdown import markdown

from hub import db
from hub.models.membership import Subscriber
from hub.services import email


subscr_recipients = db.Table('email_subscribers', 
    db.Column('email_id', db.Integer, db.ForeignKey('email.id'), primary_key=True),
    db.Column('subscriber', db.String(1024), db.ForeignKey('subscriber.email'), primary_key=True)
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
    to_all_subscribers = db.Column(db.Boolean, default=False)

    subscribers = db.relationship('Subscriber', secondary=subscr_recipients, lazy='subquery', 
                                  backref=db.backref('emails', lazy=True))


    def send(self):
        if self.status in ('SENT', 'DRAFT', 'DELETED', 'ARCHIVED'):
            return

        html = markdown(self.body)

        if self.to_all_subscribers:
            subs = Subscriber.query.all()
        else:
            subs = self.subscribers

        for recipient in subs:
            email.send_email(recipient=str(recipient),
                             subject=self.subject,
                             body_html=html,
                             body_text=self.body)

