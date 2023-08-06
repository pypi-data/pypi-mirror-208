import configparser
from abc import ABC
from contextlib import contextmanager
from functools import partial
import jwt
import boto3
from aiohttp import hdrs, web
from aiohttp.web_request import Request
from botocore.exceptions import ClientError

from ..oidcclaimhdrs import SUB

from heaobject.account import AWSAccount
from heaobject.bucket import AWSBucket
from heaobject.keychain import AWSCredentials, Credentials, CredentialTypeVar
from heaobject.registry import Property
from heaobject.root import DesktopObjectDict
from heaobject.folder import AWSS3Folder
from heaobject.data import AWSS3FileObject
from heaobject.volume import AWSFileSystem, FileSystemTypeVar
from heaobject.user import NONE_USER
from ..heaobjectsupport import type_to_resource_url
from heaserver.service import client
from yarl import URL
from . import database
from .database import Database, MicroserviceDatabaseManager
from ..testcase.collection import query_fixtures, query_content
from heaobject.awss3key import decode_key
from typing import Optional, Any, Generator, Callable, Mapping, Tuple, List, Union
from configparser import ConfigParser
import asyncio
from io import BytesIO
import logging


class AWS(Database, ABC):
    """
    Connectivity to Amazon Web Services (AWS) for HEA microservices. Subclasses must call this constructor.
    """

    def __init__(self, config: Optional[configparser.ConfigParser], **kwargs) -> None:
        super().__init__(config, **kwargs)


class S3(AWS):
    """
    Connectivity to AWS Simple Storage Service (S3) for HEA microservices.
    """
    OIDC_CLIENT = "OIDC_CLIENT"
    # this is the buffer we give to refresh credentials in minutes on our end before they expire on aws
    EXPIRATION_LIMIT = 540
    MAX_DURATION_SECONDS = 43200

    def __init__(self, config: Optional[ConfigParser], **kwargs):
        super().__init__(config, **kwargs)

    async def update_credentials(self, request: Request, credentials: AWSCredentials) -> None:
        """
        This is a wrapper function to be extended by tests
        It obtains credential's url from the registry and that makes PUT

        :param request:
        :param credentials:
        :returns: None if it succeeds otherwise it will raise ValueError or HTTPError
        """
        resource_url = await type_to_resource_url(request, Credentials)
        if not resource_url:
            raise ValueError(f'No service for type {Credentials.get_type_name()}')
        await client.put(app=request.app, url=URL(resource_url) / credentials.id, data=credentials,
                         headers=request.headers)

    async def get_property(self, app: web.Application, name: str) -> Optional[Property]:
        """
        This is a wrapper function to be extended by tests
        Gets the Property with the given name from the HEA registry service.

        :param app: the aiohttp app.
        :param name: the property's name.
        :return: a Property instance or None (if not found).
        """
        return await client.get_property(app=app, name=name)

    async def generate_cloud_credentials(self, request: Request, oidc_client: str, arn: str) -> Optional[
        AWSCredentials]:
        return await generate_cloud_credentials(request=request, oidc_client=oidc_client, arn=arn)

    async def get_file_system_and_credentials_from_volume(self, request: Request, volume_id) -> Tuple[
        FileSystemTypeVar, Optional[CredentialTypeVar]]:
        return await database.get_file_system_and_credentials_from_volume(request, volume_id, AWSFileSystem,
                                                                          AWSCredentials)

    async def get_temporary_credentials(self, request: web.Request, credentials: AWSCredentials,
                                        aws_source: Union[boto3.client, boto3.resource],
                                        service_name: str, oidc_client_prop: Property) -> boto3.client:
        """
            Gets temporary credentials and returns the authorized client. In order to do that it
            gets the previous credential's role_arn and then assumes it.

            :param aws_source:
            :param request: the aiohttp request
            :param credentials: the aws credentials last saved
            :param service_name: The type of client to return
            :param oidc_client_prop: The property for the open id connect client
            :return: the boto3 client provided with credentials
            :raise ValueError if no previously saved credentials it raises ValueError
        """
        logger = logging.getLogger(__name__)
        oidc_client = oidc_client_prop.value
        loop = asyncio.get_running_loop()

        if credentials.has_expired(S3.EXPIRATION_LIMIT):
            logger.info("credentials need to be refreshed")
            cloud_creds = await self.generate_cloud_credentials(request=request, oidc_client=oidc_client,
                                                                arn=credentials.role_arn)
            if not cloud_creds:
                raise ValueError(f'Could not generate cloud credentials with {oidc_client} '
                                 f'and these params {credentials.role_arn}')
            logger.info("credentials successfully obtained from cloud:  %s" % cloud_creds.to_dict())
            credentials.account = cloud_creds.account
            credentials.password = cloud_creds.password
            credentials.session_token = cloud_creds.session_token
            credentials.expiration = cloud_creds.expiration
            await self.update_credentials(request=request, credentials=credentials)
            logger.info("credentials  updated in the database")
        return await loop.run_in_executor(None, partial(aws_source, service_name,
                                                        region_name=credentials.where,
                                                        aws_access_key_id=credentials.account,
                                                        aws_secret_access_key=credentials.password,
                                                        aws_session_token=credentials.session_token))

    async def get_client(self, request: Request, service_name: str, volume_id: str) -> Any:
        """
        Gets an AWS service client.  If the volume has no credentials, it uses the boto3 library to try and find them.
        This method is not designed to be overridden.

        :param request: the HTTP request (required).
        :param service_name: AWS service name (required).
        :param volume_id: the id string of a volume (required).
        :return: a Mongo client for the file system specified by the volume's file_system_name attribute. If no volume_id
        was provided, the return value will be the "default" Mongo client for the microservice found in the HEA_DB
        application-level property.
        :raise ValueError: if there is no volume with the provided volume id, the volume's file system does not exist,
        the volume's credentials were not found, or a necessary service is not registered.

        TODO: need a separate exception thrown for when a service is not registered (so that the server can respond with a 500 error).
        """
        logger = logging.getLogger(__name__)
        if volume_id is not None:
            file_system, credentials = \
                await self.get_file_system_and_credentials_from_volume(request, volume_id)
            logger.info("credentials retrieved from database checking if expired: %s" % credentials.to_dict()
                        if credentials else None)
            loop = asyncio.get_running_loop()
            if not credentials:  # delegate to boto3 to find the credentials
                return await loop.run_in_executor(None, boto3.client, service_name)

            oidc_client = await self.get_property(app=request.app, name=S3.OIDC_CLIENT)
            if oidc_client:  # generating temp creds from aws
                return await self.get_temporary_credentials(request=request,
                                                            credentials=credentials,
                                                            aws_source=boto3.client,
                                                            service_name=service_name, oidc_client_prop=oidc_client)
            # for permanent credentials
            return await loop.run_in_executor(None, partial(boto3.client, service_name,
                                                            region_name=credentials.where,
                                                            aws_access_key_id=credentials.account,
                                                            aws_secret_access_key=credentials.password))
        else:
            raise ValueError('volume_id is required')

    async def get_resource(self, request: Request, service_name: str, volume_id: str) -> Any:
        """
        Gets an AWS resource. If the volume has no credentials, it uses the boto3 library to try and find them. This
        method is not designed to be overridden.

        :param request: the HTTP request (required).
        :param service_name: AWS service name (required).
        :param volume_id: the id string of a volume (required).
        :return: a Mongo client for the file system specified by the volume's file_system_name attribute. If no volume_id
        was provided, the return value will be the "default" Mongo client for the microservice found in the HEA_DB
        application-level property.
        :raise ValueError: if there is no volume with the provided volume id, the volume's file system does not exist,
        the volume's credentials were not found, or a necessary service is not registered.
        """
        logger = logging.getLogger(__name__)
        if volume_id is not None:
            file_system, credentials = \
                await self.get_file_system_and_credentials_from_volume(request, volume_id)
            logger.info(
                "credentials retrieved from database checking if expired: %s" % credentials.to_dict() if credentials else None)
            loop = asyncio.get_running_loop()
            if not credentials:  # delegate to boto3 to find the credentials
                return await loop.run_in_executor(None, boto3.resource, service_name)

            oidc_client = await self.get_property(app=request.app, name=S3.OIDC_CLIENT)
            if oidc_client:  # generating temp creds from aws
                return await self.get_temporary_credentials(request=request,
                                                            credentials=credentials,
                                                            aws_source=boto3.resource,
                                                            service_name=service_name, oidc_client_prop=oidc_client)

            # for permanent credentials
            return await loop.run_in_executor(None, partial(boto3.resource, service_name,
                                                            region_name=credentials.where,
                                                            aws_access_key_id=credentials.account,
                                                            aws_secret_access_key=credentials.password))

        else:
            raise ValueError('volume_id is required')

    async def get_account(self, request: Request, volume_id: str) -> AWSAccount | None:
        """
        Gets the current user's AWS account dict associated with the provided volume_id.

        :param request: the HTTP request object (required).
        :param volume_id: the volume id (required).
        :return: the AWS account dict, or None if not found.
        """

        sts_client = await self.get_client(request, 'sts', volume_id)
        return await S3._get_account(sts_client, request.headers.get(SUB, NONE_USER))

    @staticmethod
    async def _get_account(sts_client, owner: str) -> AWSAccount:
        aws_object_dict = {}
        account = AWSAccount()

        loop = asyncio.get_running_loop()
        identity_future = loop.run_in_executor(None, sts_client.get_caller_identity)
        # user_future = loop.run_in_executor(None, iam_client.get_user)
        await asyncio.wait([identity_future])  # , user_future])
        aws_object_dict['account_id'] = identity_future.result().get('Account')
        # aws_object_dict['alias'] = next(iam_client.list_account_aliases()['AccountAliases'], None)  # Only exists for IAM accounts.
        # user = user_future.result()['User']
        # aws_object_dict['account_name'] = user.get('UserName')  # Only exists for IAM accounts.

        account.id = aws_object_dict['account_id']
        account.name = aws_object_dict['account_id']
        account.display_name = aws_object_dict['account_id']
        account.owner = owner
        # account.created = user['CreateDate']
        # FIXME this info coming from Alternate Contact(below) gets 'permission denied' with IAMUser even with admin level access
        # not sure if only root account user can access. This is useful info need to investigate different strategy
        # alt_contact_resp = account_client.get_alternate_contact(AccountId=account.id, AlternateContactType='BILLING' )
        # alt_contact =  alt_contact_resp.get("AlternateContact ", None)
        # if alt_contact:
        # account.full_name = alt_contact.get("Name", None)

        return account

class S3Manager(MicroserviceDatabaseManager):
    """
    Database manager for mock Amazon Web Services S3 buckets. It will not make any calls to actual S3 buckets. This
    class is not designed to be subclassed.
    """

    @contextmanager
    def database(self, config: configparser.ConfigParser = None) -> Generator[S3, None, None]:
        yield S3(config)

    def insert_desktop_objects(self, desktop_objects: Optional[Mapping[str, list[DesktopObjectDict]]]):
        super().insert_desktop_objects(desktop_objects)
        logger = logging.getLogger(__name__)
        for coll, objs in query_fixtures(desktop_objects, db_manager=self).items():
            logger.debug('Inserting %s collection object %s', coll, objs)
            inserters = self.get_desktop_object_inserters()
            if coll in inserters:
                inserters[coll](objs)

    def insert_content(self, content: Optional[Mapping[str, Mapping[str, bytes]]]):
        super().insert_content(content)
        if content is not None:
            client = boto3.client('s3')
            for key, contents in query_content(content, db_manager=self).items():
                if key == 'awss3files':
                    for id_, content_ in contents.items():
                        bucket_, actual_content = content_.split(b'|', 1)
                        bucket = bucket_.decode('utf-8')
                        with BytesIO(actual_content) as f:
                            client.upload_fileobj(Fileobj=f, Bucket=bucket, Key=decode_key(id_))
                else:
                    raise KeyError(f'Unexpected key {key}')

    @classmethod
    def get_desktop_object_inserters(cls) -> dict[str, Callable[[list[DesktopObjectDict]], None]]:
        return {'awsaccounts': cls.__awsaccount_inserter,
                'buckets': cls.__bucket_inserter,
                'awss3folders': cls.__awss3folder_inserter,
                'awss3files': cls.__awss3file_inserter}

    @classmethod
    def __awss3file_inserter(cls, v):
        for awss3file_dict in v:
            awss3file = AWSS3FileObject()
            awss3file.from_dict(awss3file_dict)
            cls.__create_awss3file(awss3file)

    @classmethod
    def __awss3folder_inserter(cls, v):
        for awss3folder_dict in v:
            awss3folder = AWSS3Folder()
            awss3folder.from_dict(awss3folder_dict)
            cls.__create_awss3folder(awss3folder)

    @classmethod
    def __bucket_inserter(cls, v):
        for bucket_dict in v:
            awsbucket = AWSBucket()
            awsbucket.from_dict(bucket_dict)
            cls.__create_bucket(awsbucket)

    @classmethod
    def __awsaccount_inserter(cls, v):
        pass  # moto automatically creates one account to use. Creating your own accounts doesn't seem to work.

    @staticmethod
    def __create_bucket(bucket: AWSBucket):
        client = boto3.client('s3')
        if bucket is not None:
            if bucket.name is None:
                raise ValueError('bucket.name cannot be None')
            else:
                if bucket.region != 'us-east-1' and bucket.region:
                    client.create_bucket(Bucket=bucket.name,
                                         CreateBucketConfiguration={'LocationConstraint': bucket.region})
                else:
                    client.create_bucket(Bucket=bucket.name)
                client.put_bucket_versioning(Bucket=bucket.name, 
                                             VersioningConfiguration={'MFADelete': 'Disabled', 'Status': 'Enabled'})

    @staticmethod
    def __create_awss3folder(awss3folder: AWSS3Folder):
        client = boto3.client('s3')
        client.put_object(Bucket=awss3folder.bucket_id, Key=awss3folder.key, StorageClass=awss3folder.storage_class.name)

    @staticmethod
    def __create_awss3file(awss3file: AWSS3FileObject):
        client = boto3.client('s3')
        client.put_object(Bucket=awss3file.bucket_id, Key=awss3file.key, StorageClass=awss3file.storage_class.name)


async def generate_cloud_credentials(request: Request, oidc_client: str, arn: str) -> Optional[
    AWSCredentials]:
    """
    :param request: the HTTP request (required).
    :param oidc_client: the name openidc client
    :param arn: The aws role arn that to be assumed
    :returns the AWSCredentials populated with the resource's content, None if no such resource exists, or another HTTP
    status code if an error occurred.
    """
    logger = logging.getLogger(__name__)
    sub = request.headers.get(SUB, None)
    if not arn:
        raise ValueError('Cannot get credentials arn which is required')
    auth: List[str] = request.headers.get(hdrs.AUTHORIZATION, '').split(' ')

    if not len(auth) == 2:
        raise ValueError("Bearer Token is required in header")
    token = jwt.decode(auth[1], options={"verify_signature": False})
    claim = token.get('resource_access', None)
    assumed_role_object = None
    try:
        if claim and arn in claim[oidc_client]['roles']:
            sts_client = boto3.client('sts')
            assumed_role_object = sts_client.assume_role_with_web_identity(
                WebIdentityToken=auth[1], RoleArn=arn,
                RoleSessionName=sub, DurationSeconds=S3.MAX_DURATION_SECONDS
            )
        else:
            raise ClientError("Permission Denied, invalid role")
    except ClientError as ce:
        ce_str = str(ce)
        logger.info(f"Permission Denied: {ce_str}")
        return None
    if not assumed_role_object.get('Credentials'):
        return None
    creds = AWSCredentials()
    creds.account = assumed_role_object.get('Credentials')['AccessKeyId']
    creds.password = assumed_role_object.get('Credentials')['SecretAccessKey']
    creds.session_token = assumed_role_object.get('Credentials')['SessionToken']
    creds.expiration = assumed_role_object.get('Credentials')['Expiration']

    return creds
