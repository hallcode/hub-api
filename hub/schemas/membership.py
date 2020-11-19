from hub.exts import ma
from hub.models.membership import Person
from hub.models.finance import Payment

class PersonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Person