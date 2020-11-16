from hub.resources import (
    base,
    verify,
    person,
    auth
)


def load_routes(api):
    """
    Load all routes
    """

    # Base API routes
    api.add_resource(base.RootApi, '/', endpoint='_root')
    api.add_resource(base.BaseApi, '/api', endpoint='_base')

    # Auth routes
    api.add_resource(auth.LoginApi, '/api/login')
    api.add_resource(verify.VerifyApi, '/api/verify/<string:address_text>')

    # Person
    api.add_resource(person.PeopleApi, '/api/people')
    api.add_resource(person.PersonApi, '/api/people/<string:person_id>')