from hub.exts import ma
from hub.models.membership import Person
from hub.models.finance import Payment

class PersonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        exclude = (
            "ward_id",
            "constituency_id",
            "district_id",
            "stripe_customer_id",
            "stripe_payment_id",
            "password_hash",
            "created_at"
        )

    id              = ma.auto_field(dump_only=True)
    created_at      = ma.auto_field(dump_only=True)

    first_name      = ma.auto_field(load_only=True)
    last_name       = ma.auto_field(load_only=True)
    landlord        = ma.auto_field(load_only=True)
    own_house       = ma.auto_field(load_only=True)
    pays_rent       = ma.auto_field(load_only=True)
    restricted_job  = ma.auto_field(load_only=True)

    full_name = ma.Str(dump_only=True)
    email = ma.Email(attribute="primary_email")
    password = ma.Str(load_only=True)