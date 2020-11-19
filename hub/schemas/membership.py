from marshmallow import Schema, fields

class PersonSchema(Schema):
    id = fields.String()
    first_name = fields.String(load_only=True)
    last_name = fields.String(load_only=True)
    full_name = fields.Method("get_full_name", dump_only=True)
    primary_email = fields.Email()
    date_of_birth = fields.Date()
    password = fields.Str(load_only=True)

    def get_full_name(self, person):
        return f"{person.first_name} {person.last_name}"