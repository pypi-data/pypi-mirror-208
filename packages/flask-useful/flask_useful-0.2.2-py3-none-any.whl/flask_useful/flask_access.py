from flask import current_app, request, abort
try:
    from flask_login import current_user
except ImportError:
    current_user = None


class FlaskAccess(object):
    property_name = 'is_public_endpoint'

    def __init__(self, app=None):
        self.app = None

        if app is not None:
            self.init_app(app)

    def _check_blueprint(self, endpoint):
        blueprint_name, _ = endpoint.rsplit('.', 1)
        bp = current_app.blueprints.get(blueprint_name)
        return bool(bp and getattr(bp, self.property_name, False))

    def login_required(self):
        endpoint = request.endpoint
        config = current_app.config
        login_manager = getattr(current_app, 'login_manager', None)

        if endpoint:
            rules = [
                lambda: current_user and current_user.is_authenticated,
                lambda: login_manager and login_manager.login_view == endpoint,
                lambda: endpoint in {'static', *config['ACCESS_STATIC_ENDPOINTS']},
                lambda: getattr(current_app.view_functions[endpoint], self.property_name, False),
                lambda: self._check_blueprint(endpoint),
            ]

            if not any((rule() for rule in rules)):
                if login_manager:
                    return current_app.login_manager.unauthorized()

                abort(401)

    def init_app(self, app):
        app.config.setdefault('ACCESS_STATIC_ENDPOINTS', [])
        app.before_request(self.login_required)

    def public_required(self, f):
        setattr(f, self.property_name, True)
        return f
