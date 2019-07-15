import faulthandler
from os import path

from flask import Flask
from flask_restful import Api

from pj import PJ, UpdatePJ, Info
from pjcontroller import PJController
from config import Config

API_PREFIX = '/api/1'

faulthandler.enable()
if hasattr(faulthandler, 'register'):
    import signal

    faulthandler.register(signal.SIGUSR2, all_threads=True)

app = Flask(__name__)
api = Api(app)
cfg = Config('pyjvcpj')
resource_args = {
    'pj_controller': PJController(cfg)
}

# GET: get info
api.add_resource(Info, API_PREFIX + '/info', resource_class_kwargs=resource_args)
# GET: read only command
api.add_resource(PJ, API_PREFIX + '/pj/<command>', resource_class_kwargs=resource_args)
# PUT: write command
api.add_resource(UpdatePJ, API_PREFIX + '/pj', resource_class_kwargs=resource_args)


def main(args=None):
    """ The main routine. """
    logger = cfg.configure_logger()

    if cfg.use_twisted:
        import logging
        logger = logging.getLogger('twisted')
        from twisted.internet import reactor
        from twisted.web.resource import Resource
        from twisted.web import server
        from twisted.web.wsgi import WSGIResource
        from twisted.application import service
        from twisted.internet import endpoints

        class FlaskAppWrapper(Resource):
            """
            wraps the flask app as a WSGI resource while allow the react index.html (and its associated static content)
            to be served as the default page.
            """

            def __init__(self):
                super().__init__()
                self.wsgi = WSGIResource(reactor, reactor.getThreadPool(), app)

            def getChild(self, path, request):
                """
                Overrides getChild to allow the request to be routed to the wsgi app (i.e. flask for the rest api
                calls), the static dir (i.e. for the packaged css/js etc), the various concrete files (i.e. the public
                dir from react-app), the command icons or to index.html (i.e. the react app) for everything else.
                :param path:
                :param request:
                :return:
                """
                # allow CORS (CROSS-ORIGIN RESOURCE SHARING) for debug purposes
                request.setHeader('Access-Control-Allow-Origin', '*')
                request.setHeader('Access-Control-Allow-Methods', 'GET, PUT')
                request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
                request.setHeader('Access-Control-Max-Age', '2520')  # 42 hours
                logger.debug(f"Handling {path}")
                if path == b'api':
                    request.prepath.pop()
                    request.postpath.insert(0, path)
                    return self.wsgi
                else:
                    return None

            def render(self, request):
                return self.wsgi.render(request)

        application = service.Application('pyjvcpj')
        if cfg.is_access_logging is True:
            site = server.Site(FlaskAppWrapper(), logPath=path.join(cfg.config_path, 'access.log').encode())
        else:
            site = server.Site(FlaskAppWrapper())
        endpoint = endpoints.TCP4ServerEndpoint(reactor, cfg.port, interface='0.0.0.0')
        endpoint.listen(site)
        reactor.run()
    else:
        # get config from a flask standard place not our config yml
        app.run(debug=cfg.run_in_debug, host='0.0.0.0', port=cfg.port, use_reloader=False)


if __name__ == '__main__':
    main()
