"""
Starts a HEA microservice.
"""

import logging.config
import argparse
from aiohttp import web, TCPConnector
import os.path
from heaserver.service import appproperty, appfactory
from heaserver.service import wstl
from heaserver.service.aiohttp import client_session
from typing import Callable, Iterable, Optional, Union, AsyncIterator, AsyncGenerator, Type
from yarl import URL

from .config import Configuration
from .db.database import MicroserviceDatabaseManager

from .defaults import DEFAULT_LOG_LEVEL, DEFAULT_PORT, DEFAULT_BASE_URL, DEFAULT_REGISTRY_URL
from ..service import client

routes = web.RouteTableDef()


def init(port: Union[int, str] = DEFAULT_PORT,
         base_url: Union[URL, str] = DEFAULT_BASE_URL,
         config_file: Optional[str] = None,
         config_string: Optional[str] = None,
         logging_level: Optional[str] = None) -> Configuration:
    """
    Sets a default logging level and returns a new Configuration object.

    :param port: the port the service will listen to. If omitted, the DEFAULT_PORT is used.
    :param base_url: the service's base URL. If omitted, the DEFAULT_BASE_URL is used.
    :param config_file:
    :param config_string:
    :param logging_level: configure the logging level. If omitted, logging will not be configured.
    :return:
    """
    if logging_level is not None:
        logging.basicConfig(level=logging_level)
    config = Configuration(base_url=base_url,
                           port=port,
                           config_file=config_file,
                           config_str=config_string)
    return config


def init_cmd_line(description: str = 'A HEA microservice', default_port: int = DEFAULT_PORT) -> Configuration:
    """
    Parses command line arguments and configures the service accordingly. Must be called before anything else, if you
    want to use command line arguments to configure the service.

    :param description: optional description that will appear when the script is passed the -h or --help option.
    :param default_port: the optional port on which to listen if none is specified by command line argument. If omitted
    and no port is specified by command line argument, port 8080 is used.
    :return: a Configuration object.
    :raises ValueError: if any arguments are invalid.

    The following command line arguments are accepted:
        -b or --baseurl, which optionally sets the base URL of the service. If unspecified, the default is
        http://localhost:<port>, where port is the 8080 or the port number set by the --port argument.
        -p or --port, which optionally sets the port the microservice will listen on. The default is 8080.
        -f or --configuration, which optionally sets an INI file to use for additional configuration.
        -l or --logging, which optionally sets a standard logging configuration INI file. If unspecified, the
            DEFAULT_LOG_LEVEL variable will be used to set the default log level.

    Microservices must not call logging.getLogger until init has been called.

    The INI configuration file is parsed by the built-in configparser module and may contain the following settings:

    ;Base URL for the HEA registry service (default is http://localhost:8080/heaserver-server-registry)
    Registry = url of the HEA registry service

    ;See the documentation for the db object that you passed in for the config file properties that it expects.
    """
    assert default_port is not None

    parser = argparse.ArgumentParser(description)
    parser.add_argument('-b', '--baseurl',
                        metavar='baseurl',
                        type=str,
                        default=str(DEFAULT_BASE_URL),
                        help='The base URL of the service')
    parser.add_argument('-p', '--port',
                        metavar='port',
                        type=int,
                        default=default_port,
                        help='The port on which the server will listen for connections')
    parser.add_argument('-f', '--configuration',
                        metavar='configuration',
                        type=str,
                        help='Path to a HEA configuration file in INI format')
    parser.add_argument('-l', '--logging',
                        metavar='logging',
                        type=str,
                        help='Standard logging configuration file')
    args = parser.parse_args()

    if args.logging and os.path.isfile(args.logging):
        logging.config.fileConfig(args.logging, disable_existing_loggers=False)
    else:
        logging.basicConfig(level=DEFAULT_LOG_LEVEL)

    logger = logging.getLogger(__name__)

    if args.configuration:
        logger.info('Parsing HEA config file %s', args.configuration)
    else:
        logger.info('No HEA config file found')

    if args.logging and os.path.isfile(args.logging):
        logger.info('Parsing logging config file %s', args.logging)
    else:
        logger.info('No logging config file found')

    baseurl_ = args.baseurl
    return Configuration(base_url=baseurl_[:-1] if baseurl_.endswith('/') else baseurl_,
                         config_file=args.configuration,
                         port=args.port)


def start(package_name: str | None = None,
          db: Optional[Type[MicroserviceDatabaseManager]] = None,
          wstl_builder_factory: Optional[Callable] = None,
          cleanup_ctx: Optional[Iterable[Callable[[web.Application], AsyncIterator[None]]]] = None,
          config: Optional[Configuration] = None) -> None:
    """
    Starts the microservice. It calls get_application() to get the AioHTTP app
    object, sets up a global HTTP client session object in the appproperty.HEA_CLIENT_SESSION property, and then calls
    AioHTTP's aiohttp.web.run_app() method with it to launch the service. It sets the
    application and request properties described in the documentation for get_application().

    :param package_name: the microservice's distribution package name. The HEA server framework uses this argument to
    register metadata about the microservice in the HEA registry service. Omit this argument if you do not want this
    microservice to register metadata about itself using this mechanism. For example, the registry service has to
    register itself using its own mechanism.
    :param db: a database manager type from the heaserver.server.db package, if database connectivity is needed. Sets
    the appproperty.HEA_DB application property to a database object created by this database manager.
    :param wstl_builder_factory: a zero-argument callable that will return a design-time WeSTL document. Optional if
    this service has no actions.
    :param cleanup_ctx: an iterable of asynchronous generators that will be passed into the aiohttp cleanup context.
    The generator should have a single yield statement that separates code to be run upon startup and code to be
    run upon shutdown. The shutdown code will run only if the startup code did not raise any exceptions. The startup
    code will run in sequential order. The shutdown code will run in reverse order.
    :param config: a Configuration instance.

    This function must be called after init.

    A 'registry' property is set in the application context with the registry service's base URL.
    """
    app = get_application(package_name, db=db() if db is not None else None, wstl_builder_factory=wstl_builder_factory,
                          cleanup_ctx=cleanup_ctx, config=config)
    app.cleanup_ctx.append(client_session_cleanup_ctx)
    web.run_app(app, port=config.port if config else DEFAULT_PORT)


def get_application(package_name: str | None = None,
                    db: Optional[MicroserviceDatabaseManager] = None,
                    wstl_builder_factory: Optional[Callable[[], wstl.RuntimeWeSTLDocumentBuilder]] = None,
                    cleanup_ctx: Optional[Iterable[Callable[[web.Application], AsyncIterator[None]]]] = None,
                    config: Optional[Configuration] = None) -> web.Application:
    """
    Gets the aiohttp application object for this microservice. It is called by start() during normal operations, and
    by test cases when running tests.

    It registers cleanup context generators that set the following application properties:
    HEA_DB: a database object from the heaserver.server.db package.
    HEA_CLIENT_SESSION: a aiohttp.web.ClientSession HTTP client object. This property is only set if the testing
    argument is False. If running test cases, testing should be set to True, and the HEAAioHTTPTestCase class will
    handle creating and destroying HTTP clients instead.
    HEA_REGISTRY: The base URL for the registry service.
    HEA_COMPONENT: This service's base URL.
    HEA_WSTL_BUILDER_FACTORY: the wstl_builder_factory argument.

    :param package_name: the microservice's distribution package name. If None, the service will not register its
    externally facing base URL with the registry service. This may be what you want in testing scenarios in which no
    registry service is running.
    :param db: a database object from the heaserver.server.db package, if database connectivity is needed.
    :param wstl_builder_factory: a zero-argument callable that will return a RuntimeWeSTLDocumentBuilder. Optional if
    this service has no actions. Typically, you will use the heaserver.service.wstl.get_builder_factory function to
    get a factory object.
    :param cleanup_ctx: an iterable of asynchronous generators that will be passed into the aiohttp cleanup context.
    The generator should have a single yield statement that separates code to be run upon startup and code to be
    run upon shutdown. The shutdown code will run only if the startup code did not raise any exceptions. Cleanup
    context generators cannot assume that any of the above application properties are available.
    :param config: a Configuration instance.
    :return: an aiohttp application object.

    This function must be called after init, and it is called by start.

    A 'registry' property is set in the application context with the registry service's base URL.
    """
    logger = logging.getLogger(__name__)

    logger.info('Starting HEA')

    if not config:
        config = init()

    app = appfactory.new_app()

    if db:
        async def _db(app: web.Application) -> AsyncGenerator:
            if db:
                with db.database(config.parsed_config if config is not None else None) as database:
                    app[appproperty.HEA_DB] = database
                    yield
            else:
                app[appproperty.HEA_DB] = None

        app.cleanup_ctx.append(_db)

    async def _hea_registry(app: web.Application) -> AsyncGenerator:
        app[appproperty.HEA_REGISTRY] = config.parsed_config['DEFAULT'].get('Registry',
                                                                            DEFAULT_REGISTRY_URL) if config else None
        yield

    app.cleanup_ctx.append(_hea_registry)

    async def _hea_component(app: web.Application) -> AsyncGenerator:
        external_base_url = str(config.base_url) if config else None
        app[appproperty.HEA_COMPONENT] = external_base_url
        if package_name is not None:
            # Needs its own client session because the main client session has not started yet.
            async with client_session(connector=TCPConnector(), connector_owner=True, raise_for_status=True) as session:
                component = await client.get_component_by_name(app, package_name, client_session=session)
                if component is not None:
                    component.external_base_url = external_base_url
                    logger.info(f'Registering external URL {external_base_url} for component {package_name}')
                    await client.put(app, URL(app[appproperty.HEA_REGISTRY]) / 'components' / component.id, component, client_session=session)
                    logger.info(f'Registering component {package_name} succeeded')
                else:
                    logger.warn(f'Component {package_name} is not registered with the HEA registry service')
        else:
            logger.info(f'Skipping registration of {external_base_url} with the HEA registry service')
        yield

    app.cleanup_ctx.append(_hea_component)

    app.add_routes(routes)

    async def _hea_wstl_builder_factory(app: web.Application) -> AsyncGenerator:
        if wstl_builder_factory is None:
            logger.debug('No design-time WeSTL loader was provided.')
            wstl_builder_factory_ = wstl.builder_factory()
        else:
            wstl_builder_factory_ = wstl_builder_factory

        app[appproperty.HEA_WSTL_BUILDER_FACTORY] = wstl_builder_factory_
        yield

    app.cleanup_ctx.append(_hea_wstl_builder_factory)

    if cleanup_ctx is not None:
        for cb in cleanup_ctx:
            app.cleanup_ctx.append(cb)
    return app


async def client_session_cleanup_ctx(app: web.Application) -> AsyncGenerator[None, None]:
    """
    Manages the global HTTP client session.

    :param app: the AioHTTP Application object.
    :return: an AsyncGenerator.
    """
    _logger = logging.getLogger(__name__)
    _logger.debug('Starting client session')
    async with client_session(connector=TCPConnector(), connector_owner=True, raise_for_status=True) as session:
        app[appproperty.HEA_CLIENT_SESSION] = session
        _logger.debug('Client session started')
        yield
        _logger.debug('Closing client session')
