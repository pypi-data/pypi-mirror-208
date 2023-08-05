"""
Classes and functions for mocking Amazon S3 buckets.

This module assumes the moto package is installed. Do not import it into environments where moto will
not be available, for example, in any code that needs to run outside automated testing.
"""
import configparser
from configparser import ConfigParser
from contextlib import contextmanager, AbstractContextManager, ExitStack
from typing import Optional, Tuple, Generator, AsyncGenerator, Union, Mapping

from aiohttp import web
from heaobject.registry import Property

from heaserver.service.db.aws import S3, S3Manager

from heaobject.keychain import Credentials, CredentialTypeVar, AWSCredentials
from heaobject.volume import AWSFileSystem, Volume, FileSystem, DEFAULT_FILE_SYSTEM
from heaobject.root import DesktopObjectDict, DesktopObject
from heaobject.account import AWSAccount
from aiohttp.web import Request

import boto3
from moto import mock_s3, mock_organizations, mock_sts
from heaserver.service.db.database import InMemoryDatabase
from freezegun import freeze_time

from heaserver.service.testcase.collection import query_fixtures, query_content


class MockS3WithMongo(S3, InMemoryDatabase):

    def __init__(self, config: Optional[ConfigParser], **kwargs):
        super().__init__(config, **kwargs)

    # async def get_property(self, app: web.Application, name: str) -> Optional[Property]:
    #     return await self._wrapped.get_property(app=app, name=name)

    async def generate_cloud_credentials(self, request: Request, oidc_client: str, arn: str) -> Optional[AWSCredentials]:
        cred_dict_list = [cred_dict for cred_dict in self.get_desktop_objects_by_collection('credentials')]
        cred = None
        if cred_dict_list and len(cred_dict_list) > 1:
            cred_dict = cred_dict_list[1]
            cred = AWSCredentials()
            cred.from_dict(cred_dict)
        elif cred_dict_list and len(cred_dict_list) == 1:
            cred_dict = cred_dict_list[0]
            cred = AWSCredentials()
            cred.from_dict(cred_dict)

        return cred if cred else None


class MockS3WithMockMongo(MockS3WithMongo, InMemoryDatabase):
    """
    Overrides the S3 class' methods use moto instead of actual AWS. It also stores volume and filesystem desktop
    objects in an in-memory data structure and mocks AWS microservices' attempts to access the file system and volumes
    microservices while requesting a boto3/moto client. Moto is documented at https://github.com/spulec/moto.
    """

    def __init__(self, config: Optional[ConfigParser], **kwargs):
        super().__init__(config, **kwargs)
        section = super().get_config_section()
        if config and section in config:
            database_section = config[section]
            self.__region_name: Optional[str] = database_section.get('RegionName', None)
            self.__aws_access_key_id: Optional[str] = database_section.get('AWSAccessKeyId', None)
            self.__aws_secret_access_key: Optional[str] = database_section.get('AWSSecretAccessKey', None)
            self.__expiration: Optional[str] = database_section.get('Expiration', None)
            self.__session_token: Optional[str] = database_section.get('SessionToken', None)
        else:
            self.__region_name = None
            self.__aws_access_key_id = None
            self.__aws_secret_access_key = None
            self.__expiration = None
            self.__session_token = None

    async def get_file_system_and_credentials_from_volume(self, request: Request, volume_id: Optional[str]) -> Tuple[
        AWSFileSystem, Optional[CredentialTypeVar]]:

        if self.__aws_secret_access_key is not None or self.__aws_access_key_id is not None:
            creds = AWSCredentials()
            creds.where = self.__region_name
            creds.account = self.__aws_access_key_id
            creds.password = self.__aws_secret_access_key
            creds.expiration = self.__expiration
        else:
            creds = self._get_credential_by_volume(volume_id=volume_id)
        return AWSFileSystem(), creds

    async def get_volumes(self, request: Request, file_system_type_or_type_name: Union[str, type[FileSystem]]) -> \
        AsyncGenerator[Volume, None]:
        for volume_dict in self.get_desktop_objects_by_collection('volumes'):
            if issubclass(file_system_type_or_type_name, DesktopObject):
                file_system_type_name_ = file_system_type_or_type_name.get_type_name()
            else:
                file_system_type_name_ = str(file_system_type_or_type_name)
            if volume_dict.get('file_system_type', AWSFileSystem.get_type_name()) == file_system_type_name_:
                volume = Volume()
                volume.from_dict(volume_dict)
                yield volume

    async def get_account(self, request: Request, volume_id: str) -> AWSAccount | None:
        account_id = '123456789012'
        a = AWSAccount()
        a.id = account_id
        a.display_name = account_id
        a.name = account_id

        return a


    async def get_property(self, app: web.Application, name: str) -> Optional[Property]:
        prop_dict_list = [prop_dict for prop_dict in self.get_desktop_objects_by_collection('properties')
                          if prop_dict.get('name', None) == name]
        prop = None
        if prop_dict_list and len(prop_dict_list) > 0:
            prop_dict = prop_dict_list[0]
            prop = Property()
            prop.from_dict(prop_dict)
        return prop if prop else None

    async def update_credentials(self, request: Request, credentials: AWSCredentials) -> None:
        pass

    def _get_credential_by_volume(self, volume_id: str) -> Optional[AWSCredentials]:
        volume_dict = self.get_desktop_object_by_collection_and_id('volumes', volume_id)
        if volume_dict is None:
            raise ValueError(f'No volume found with id {volume_id}')
        volume = Volume()
        volume.from_dict(volume_dict)
        if volume.credential_id is None:
            creds = None
        else:
            credentials_dict = self.get_desktop_object_by_collection_and_id('credentials', volume.credential_id)
            if credentials_dict is None:
                raise ValueError(f'No credentials with id {volume.credential_id}')
            creds = AWSCredentials()
            creds.from_dict(credentials_dict)
        return creds


class MockS3Manager(S3Manager):
    """
    Database manager for mocking AWS S3 buckets with moto. Mark test fixture data that is managed in S3 buckets with
    this database manager in testing environments. Furthermore, connections to boto3/moto clients normally require
    access to the registry and volume microservices. This database manager does not mock those connections, and actual
    registry and volume microservices need to be running, as is typical in integration testing environments. For unit
    testing, see MockS3ManagerWithMockMongo, which also mocks the connections to the registry and volume microservices.
    """
    def __init__(self):
        super().__init__()
        self.__mock_s3 = None

    @classmethod
    def get_environment_updates(cls) -> dict[str, str]:
        result = super().get_environment_updates()
        result.update({'AWS_ACCESS_KEY_ID': 'testing',
                       'AWS_SECRET_ACCESS_KEY': 'testing',
                       'AWS_SECURITY_TOKEN': 'testing',
                       'AWS_SESSION_TOKEN': 'testing',
                       'AWS_DEFAULT_REGION': 'us-east-1'
                       })
        return result

    @classmethod
    def get_context(cls) -> list[AbstractContextManager]:
        result = super().get_context()
        result.extend([mock_s3(), mock_organizations(), mock_sts(), freeze_time("2022-05-17")])
        return result

    def insert_desktop_objects(self, desktop_objects: Optional[Mapping[str, list[DesktopObjectDict]]]):
        client = boto3.client('organizations')
        client.create_organization(FeatureSet='ALL')
        super().insert_desktop_objects(desktop_objects)

    @contextmanager
    def database(self, config: configparser.ConfigParser = None) -> Generator[S3, None, None]:
        yield MockS3WithMongo(config)


class MockS3ManagerWithMockMongo(MockS3Manager):
    """
    Database manager for mocking AWS S3 buckets with moto. Mark test fixture data that is managed in S3 buckets with
    this database manager in unit test environments. Furthermore, connections to boto3/moto clients normally require
    access to the registry and volume microservices. This database manager mocks those connections. Mark
    component, volume, and filesystem test collections with this database manager to make them available in unit
    testing environments. This class is not designed to be subclassed.
    """

    def __init__(self):
        super().__init__()
        self.__mock_s3 = None

    def start_database(self, context_manager: ExitStack) -> None:
        self.__mock_s3 = MockS3WithMockMongo(None)
        super().start_database(context_manager)

    @classmethod
    def get_context(cls) -> list[AbstractContextManager]:
        result = super().get_context()
        result.extend([mock_s3(), mock_organizations(), mock_sts(), freeze_time("2022-05-17")])
        return result

    def insert_desktop_objects(self, desktop_objects: Optional[Mapping[str, list[DesktopObjectDict]]]):
        client = boto3.client('organizations')
        client.create_organization(FeatureSet='ALL')
        self.__mock_s3.add_desktop_objects(query_fixtures(desktop_objects, db_manager=self))
        super().insert_desktop_objects(desktop_objects)

    def insert_content(self, content: Optional[Mapping[str, Mapping[str, bytes]]]):
        self.__mock_s3.add_content(query_content(content, db_manager=self))
        return super().insert_content(content)

    @contextmanager
    def database(self, config: configparser.ConfigParser = None) -> Generator[MockS3WithMockMongo, None, None]:
        yield self.__mock_s3

