from hub.resources import (
    base,
    verify
)


def load_routes(api):
    """
    Load all routes
    """

    # Base API routes
    api.add_resource(base.RootApi, '/', endpoint='_root')
    api.add_resource(base.BaseApi, '/api', endpoint='_base')

    # Auth routes
    api.add_resource(verify.VerifyApi, '/api/verify/<string:address_text>')
