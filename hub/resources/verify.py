import random, hashlib

from flask import Response, request, current_app
from flask_restful import Resource

from hub.exts import db
from hub.models.membership import EmailAddress, VerifyToken
from hub.models.messaging import Email


class VerifyApi(Resource):

    def get(self, address_text):
        addr = EmailAddress.query.filter(EmailAddress.email == address_text).first()

        if addr is None:
            return {}, 404
        
        if addr.verified:
            return {}, 204
        
        code = random.randint(10000,99999)
        token = VerifyToken(addr.email, code)

        db.session.add(token)
        db.session.commit()
        
        self._send_verification_email(addr, code)

        return {}, 204


    def post(self, address_text):
        addr = EmailAddress.query.filter(EmailAddress.email == address_text).first()

        if addr is None:
            return {}, 404
        
        if addr.verified:
            return {}, 204
        
        data = request.get_json()

        if data is None:
            return {
                "errors": ["Please provide a verification code."]
            }, 400

        if "code" not in data:
            return {
                "errors": ["Please provide a verification code."]
            }, 400

        if not addr.verify(data["code"]):
             return {
                "errors": ["That verification code was not recognised."]
            }, 400

        #db.session.commit()

        return {}, 204


    def _send_verification_email(self, address, code):
        if address.verified:
            return

        email = Email(
            None,
            'Email verification coded',
            """Your email verification code is:

# {:d}

Enter this on the website to continue.

If you were not expecting this code, please delete this email.""".format(code)
        )

        email.preview_text = 'Verification code is {:d}'.format(code)
        email.type_code = 'TRN'

        db.session.add(email)

        email.recipients.append(address.person)

        db.session.commit()

        email.send()