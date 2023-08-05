"""
Code for running a docker container containing a mongodb database.

This module assumes the testcontainers package is installed. Do not import it into environments where testcontainers
will not be available, for example, in any code that needs to run outside automated testing or the SwaggerUI interface.
"""
from contextlib import ExitStack
from testcontainers.mongodb import MongoDbContainer

from .collection import query_fixtures, query_content
from .testenv import RegistryContainerConfig
from ..db.mongo import MongoManager, replace_id_with_object_id
from ..util import retry
from .docker import DockerImages, get_exposed_port, get_bridge_ip
from array import array
from io import BytesIO
from typing import Optional, List, Mapping
from bson import ObjectId
from heaobject import root
from docker.errors import APIError
import gridfs
import logging


class DockerMongoManager(MongoManager):
    """
    Database manager for starting a mongo database in a docker container and connecting to it on the docker bridge
    network.
    """
    def __init__(self):
        """
        No-arg constructor. Subclasses must call this constructor.
        """
        super().__init__()
        self.__mongo = None
        self.__mongodb_connection_string = None

    @retry(APIError)
    def start_database(self, context_manager: ExitStack):
        """
        Starts the database container, using the image defined in DockerImages.MONGODB. This must be called prior to
        calling get_config_file_section().

        :param context_manager: the context manager to which to attach this container. The container will shut down
        automatically when the context manager is closed.
        """
        logger = logging.getLogger(__name__)
        mongo_container = MongoDbContainer(DockerImages.MONGODB.value)
        self.__mongo = context_manager.enter_context(mongo_container)
        self.__mongodb_connection_string = f'mongodb://test:test@{self.__mongo.get_container_host_ip()}:{get_exposed_port(self.__mongo, 27017)}/hea?authSource=admin'
        logger.info('Mongo has connection string %s', self.__mongodb_connection_string)
        super().start_database(context_manager)

    def insert_desktop_objects(self, desktop_objects: Optional[Mapping[str, List[root.DesktopObjectDict]]]):
        """
        Inserts the provided HEA desktop objects into the mongo database.

        :param desktop_objects: a mapping from the mongo collection string to the desktop objects to insert.
        """
        assert self.started, 'Database not started'
        super().insert_desktop_objects(desktop_objects)
        db_ = self.__mongo.get_connection_client().hea
        for coll, objs in query_fixtures(desktop_objects, db_manager=self).items():
            if objs:
                db_[coll].insert_many(replace_id_with_object_id(obj) for obj in objs)

    def insert_content(self, content: Optional[Mapping[str, Mapping[str, bytes]]]):
        """
        Inserts the provided content into the mongo database.

        :param content: a mapping from the mongo collection string to the id of the desktop object to the content to
        insert.
        """
        assert self.started, 'Database not started'
        super().insert_content(content)
        db_ = self.__mongo.get_connection_client().hea
        content_ = content if content is not None else {}
        for key, contents in query_content(content_, db_manager=self).items():
            fs = gridfs.GridFSBucket(db_, bucket_name=key)
            for id_, d in contents.items():
                if isinstance(d, (bytes, bytearray, array)):
                    with BytesIO(d) as b:
                        fs.upload_from_stream_with_id(ObjectId(id_), id_, b)

    def get_env_vars(self) -> dict[str, str]:
        """
        Returns a dictionary of environment variable names and values for configuring a HEA microservice to connect
        to this mongo database. These environment variables should be set in the docker container. HEA microservice
        containers have a parameterized HEA config file that expects these environment variables.

        To configure a HEA microservice that is not running in docker, use get_config_file_section() instead.

        :return: a dict of environment variable name -> value.
        """
        assert self.__mongo is not None, 'Database not started'
        result = super().get_env_vars()
        result.update({
            'MONGO_HEA_DATABASE': 'hea',
            'MONGO_HEA_USERNAME': 'test',
            'MONGO_HEA_PASSWORD': 'test',
            'MONGO_HOSTNAME': get_bridge_ip(self.__mongo)
        })
        return result

    def get_config_file_section(self) -> str:
        """
        Gets a MongoDB HEA config file section suitable for configuring a HEA microservice that is running outside of
        docker to connect to a mongo database running in a container. You must call start_database() before calling
        this method.

        :return: the config file section string.
        """
        assert self.__mongodb_connection_string is not None, 'Database not started'
        result = super().get_config_file_section()
        result += f"""
    [MongoDB]
    ConnectionString = {self.__mongodb_connection_string}
    """
        return result


class RealRegistryContainerConfig(RegistryContainerConfig):
    """
    Creates a registry service configured to access another docker container containing a mongodb database. This
    class depends on the testcontainers package being installed.

    This class assumes that the testcontainers package is installed. Do not create instances of it when testcontainers
    will not be available, for example, in any code that needs to run outside automated testing or the SwaggerUI
    interface. Using it as a type annotation for optional parameters and the like where no actual instances of it
    will be created is okay, however.

    :param image: the label of the docker image to use (required).
    """
    def __init__(self, image: str):
        super().__init__(image=image, port=8080, check_path='/components', db_manager_cls=DockerMongoManager)
