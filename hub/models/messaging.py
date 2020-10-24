from markdown import markdown
import chevron

from hub import db
from hub.models.membership import Person
from hub.services import email


email_recipients = db.Table('email_recipients', 
    db.Column('email_id', db.Integer, db.ForeignKey('email.id'), primary_key=True),
    db.Column('person_id', db.String(10), db.ForeignKey('person.id'), primary_key=True)
)


class Email(db.Model):
    
    id             = db.Column(db.Integer, primary_key=True)
    subject        = db.Column(db.String(1024))
    from_person_id = db.Column(db.String(10), db.ForeignKey('person.id'))
    created_at     = db.Column(db.DateTime)
    body           = db.Column(db.Text)
    sent_at        = db.Column(db.DateTime, nullable=True)
    hold_until     = db.Column(db.DateTime, nullable=True)
    status         = db.Column(db.String(10))
    type           = db.Column(db.String(3), default='STD')
    to_all_members = db.Column(db.Boolean, default=False)
    link           = db.Column(db.String, nullable=True)
    link_text      = db.Column(db.String, nullable=True)
    preview_text   = db.Column(db.Text, nullable=True)
    title          = db.Column(db.String, nullable=True)

    recipients = db.relationship('Person', secondary=email_recipients, lazy='subquery', 
                                  backref=db.backref('emails_received', lazy=True))

    sender = db.relationship('Person', backref=db.backref('emails_sent', lazy=True), lazy=True)

    def __init__(self, sender, subject, body):
        self.status  = 'CREATED'
        self.sender  = sender
        self.subject = subject
        self.body    = body

    def get_html(self, to):
        template = email.get_email_template('base.html.mustache')

        data = {
            'email': self.__dict__,
            'to': to.__dict__,
            'from': self.sender.__dict__
        }

        html = chevron.render(
            template=self.body, 
            data=data
        )

        html = markdown(html)

        main = chevron.render(
            template=template,
            data={
                'body': html,
                **data
            }
        )

        return main

    def send(self):
        if self.status in ('SENT', 'DRAFT', 'DELETED', 'ARCHIVED'):
            return

        if self.to_all_members:
            subs = Person.query.all()
        else:
            subs = self.recipients

        for recipient in subs:
            if recipient.primary_email is None:
                continue
            
            email.send_email(
                recipient   = recipient.primary_email,
                subject     = self.subject,
                body_html   = self.get_html(recipient),
                body_text   = self.body,
                sender_name = '"{:s} (PeTU)"'.format(self.sender.legal_name)
            )

        self.status = 'SENT'

