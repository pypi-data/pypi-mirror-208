from concurrent.futures import ThreadPoolExecutor
from heaobject.activity import AWSActivity, Status
from mypy_boto3_s3 import S3Client
"""
Manages folders stored in Amazon Simple Storage Service (S3) buckets.

Technically, folders do not exist in S3. Instead, S3 objects have a key with forward slashes that acts like a path.
Calls to get a folder will return a folder object if there exists at least one S3 object with that folder in its
key/path. Creating a folder will create a content-less S3 object, just so the other folder APIs work.
"""

from heaserver.service.runner import init_cmd_line, routes, start
from heaserver.service.db import awsservicelib, aws
from heaserver.service.db.database import get_options
from heaserver.service.wstl import builder_factory, action, add_run_time_action
from heaserver.service import response
from heaserver.service.heaobjectsupport import new_heaobject_from_type
from heaserver.service.messagebroker import publisher_cleanup_context_factory, publish_desktop_object
from heaserver.service.appproperty import HEA_DB
from heaserver.service.oidcclaimhdrs import SUB
from heaobject.awss3key import KeyDecodeException, decode_key, split, encode_key, join, is_object_in_folder
from heaserver.service.sources import AWS_S3
from heaobject.folder import AWSS3FolderFileItem, AWSS3Folder
from heaobject.data import AWSS3FileObject
from heaobject.user import NONE_USER
from heaobject.aws import S3StorageClass
from heaobject.error import DeserializeException
from aiohttp import web, hdrs
from typing import Union, Any
from multidict import istr
from aiohttp.client_exceptions import ClientError
from botocore.exceptions import ParamValidationError, ClientError as BotoClientError
from yarl import URL
from functools import partial
import logging
import asyncio

_logger = logging.getLogger(__name__)


@routes.get('/ping')
async def ping(request: web.Request) -> web.Response:
    """
    For testing whether the service is up.

    :param request: the HTTP request.
    :return: Always returns status code 200.
    """
    return response.status_ok()


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{folder_id}/items')
@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{folder_id}/items/')
@action(name='heaserver-awss3folders-item-get-actual', rel='hea-actual', path='{+actual_object_uri}')
async def get_items(request: web.Request) -> web.Response:
    """
    Gets the items of the folder with the specified id.
    :param request: the HTTP request.
    :return: the requested items, or Not Found if the folder was not found.
    ---
    summary: All items in a folder.
    tags:
        - heaserver-folders-folder-items
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - name: folder_id
          in: path
          required: true
          description: The id of the folder to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A folder id
              value: root
    responses:
      '200':
        $ref: '#/components/responses/200'
      '403':
        $ref: '#/components/responses/403'
    """
    return await _get_items(request)


@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{folder_id}/items/{id}')
async def get_item_options(request: web.Request) -> web.Response:
    """
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-folders-folder-items
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - name: folder_id
          in: path
          required: true
          description: The id of the folder to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A folder id
              value: root
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            text/plain:
                schema:
                    type: string
                    example: "200: OK"
      '403':
        $ref: '#/components/responses/403'
      '404':
        $ref: '#/components/responses/404'
    """
    return await response.get_options(request, ['GET', 'DELETE', 'HEAD', 'OPTIONS'])


@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{folder_id}/items')
@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{folder_id}/items/')
async def get_items_options(request: web.Request) -> web.Response:
    """
    Gets the allowed HTTP methods for a folder items resource.

    :param request: the HTTP request (required).
    :return: the HTTP response.
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-folders-folder-items
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - name: folder_id
          in: path
          required: true
          description: The id of the folder to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A folder id
              value: root
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            text/plain:
                schema:
                    type: string
                    example: "200: OK"
      '403':
        $ref: '#/components/responses/403'
      '404':
        $ref: '#/components/responses/404'
    """
    return await response.get_options(request, ['GET', 'POST', 'DELETE', 'HEAD', 'OPTIONS'])


@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}')
async def get_folder_options(request: web.Request) -> web.Response:
    """
    Gets the allowed HTTP methods for a folder resource.

    :param request: the HTTP request (required).
    :return: the HTTP response.
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            text/plain:
                schema:
                    type: string
                    example: "200: OK"
      '404':
        $ref: '#/components/responses/404'
    """
    return await response.get_options(request, ['GET', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{folder_id}/items/{id}')
@action(name='heaserver-awss3folders-item-get-actual', rel='hea-actual',
        path='{+actual_object_uri}')  # Maybe have a different syntax when we do not want to encode.
@action(name='heaserver-awss3folders-item-get-volume', rel='hea-volume', path='/volumes/{volume_id}')
async def get_item(request: web.Request) -> web.Response:
    """
    Gets the requested item from the given folder.

    :param request: the HTTP request. Required.
    :return: the requested item, or Not Found if it was not found.
    ---
    summary: A specific folder item.
    tags:
        - heaserver-folders-folder-items
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - name: folder_id
          in: path
          required: true
          description: The id of the folder to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A folder id
              value: root
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '403':
        $ref: '#/components/responses/403'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_item_response(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/duplicator')
@action(name='heaserver-awss3folders-folder-duplicate-form')
async def get_folder_duplicator(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested folder.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested folder was not found.
    ---
    summary: A folder to duplicate.
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_folder_move_template(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/archive')
@action(name='heaserver-awss3folders-folder-archive-form')
async def get_folder_archive(request: web.Request) -> web.Response:
    """
    Gets a form template for archiving the requested file.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested file was not found.
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_folder_move_template(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/mover')
@action(name='heaserver-awss3folders-folder-move-form')
async def get_folder_mover(request: web.Request) -> web.Response:
    """
    Gets a form template for moving the requested folder.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested folder was not found.
    ---
    summary: A folder to move.
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_folder_move_template(request)

@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/archive')
async def post_folder_archive(request: web.Request) -> web.Response:
    """
    Posts the provided file to archive it.

    :param request: the HTTP request.
    :return: a Response object with a status of No Content.
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    requestBody:
        description: The new name of the file and target for archiving it.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: The new name of the file and target for archiving it.
                  value: {
                    "template": {
                      "data": [
                      {
                        "name": "storage_class",
                        "value": "DEEP_ARCHIVE"
                      }
                      ]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: The new name of the file and target for moving it.
                  value: {
                    "target": "http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/my-bucket/awss3files/"
                  }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.archive_object(request)


@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/unarchive')
async def unarchive_folder(request: web.Request) -> web.Response:
    """

    :param request:
    :return: a Response object with status 202 Accept

    ---
    summary: A specific Folder.
    tags:
        - heaserver-folders-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.unarchive_object(request=request, activity_cb=publish_desktop_object)


@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/mover')
async def post_folder_mover(request: web.Request) -> web.Response:
    """
    Posts the provided folder to move it.

    :param request: the HTTP request.
    :return: a Response object with a status of No Content.
    ---
    summary: A specific folder.
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    requestBody:
        description: The new name of the folder and target for moving it.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: The new name of the folder and target for moving it.
                  value: {
                    "template": {
                      "data": [
                      {
                        "name": "target",
                        "value": "http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/my-bucket/awss3folders/"
                      }]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: The new name of the folder and target for moving it.
                  value: {
                    "target": "http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/my-bucket/awss3folders/"
                  }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _move_object(request)


@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/duplicator')
async def post_folder_duplicator(request: web.Request) -> web.Response:
    """
    Posts the provided item for duplication.

    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    ---
    summary: A specific folder item.
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    requestBody:
        description: The new name of the folder and target for duplicating it.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: The new name of the folder and target for duplicating it.
                  value: {
                    "template": {
                      "data": [
                      {
                        "name": "target",
                        "value": "http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/my-bucket"
                      }]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: The new name of the folder and target for moving it.
                  value: {
                    "target": "http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/my-bucket"
                  }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _duplicate_object(request)


@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{folder_id}/items')
@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{folder_id}/items/')
async def post_item_in_folder(request: web.Request) -> web.Response:
    """
    Creates a new folder item.

    :param request: the HTTP request. The body of the request is expected to be an item or an actual object.
    :return: the response, with a 204 status code if an item was created or a 400 if not. If an item was created, the
    Location header will contain the URL of the created item.
    ---
    summary: A specific folder item.
    tags:
        - heaserver-folders-folder-items
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - name: folder_id
          in: path
          required: true
          description: The id of the folder.
          schema:
            type: string
          examples:
            example:
              summary: A folder id
              value: root
    requestBody:
        description: A new folder item object.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: Item example
                  value: {
                    "template": {
                      "data": [{
                        "name": "created",
                        "value": null
                      },
                      {
                        "name": "derived_by",
                        "value": null
                      },
                      {
                        "name": "derived_from",
                        "value": []
                      },
                      {
                        "name": "description",
                        "value": null
                      },
                      {
                        "name": "display_name",
                        "value": "Bob"
                      },
                      {
                        "name": "invited",
                        "value": []
                      },
                      {
                        "name": "modified",
                        "value": null
                      },
                      {
                        "name": "name",
                        "value": "bob"
                      },
                      {
                        "name": "owner",
                        "value": "system|none"
                      },
                      {
                        "name": "shares",
                        "value": []
                      },
                      {
                        "name": "source",
                        "value": null
                      },
                      {
                        "name": "version",
                        "value": null
                      },
                      {
                        "name": "actual_object_id",
                        "value": "666f6f2d6261722d71757578"
                      },
                      {
                        "name": "actual_object_type_name",
                        "value": "heaobject.data.AWSS3FileObject"
                      },
                      {
                        "name": "actual_object_uri",
                        "value": "/volumes/666f6f2d6261722d71757578/buckets/my-bucket/folders/666f6f2d6261722d71757578"
                      },
                      {
                        "name": "type",
                        "value": "heaobject.folder.AWSS3FolderFileItem"
                      }]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: Item example
                  value: {
                    "created": null,
                    "derived_by": null,
                    "derived_from": [],
                    "description": null,
                    "display_name": "Joe",
                    "invited": [],
                    "modified": null,
                    "name": "joe",
                    "owner": "system|none",
                    "shares": [],
                    "source": null,
                    "type": "heaobject.folder.AWSS3Item",
                    "version": null,
                    "folder_id": "root",
                    "actual_object_id": "666f6f2d6261722d71757578",
                    "actual_object_type_name": "heaobject.registry.Component",
                    "actual_object_uri": "/volumes/666f6f2d6261722d71757578/buckets/my-bucket/folders/666f6f2d6261722d71757578"
                  }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _post_item_in_folder(request)


@routes.delete('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{folder_id}/items/{id}')
async def delete_item(request: web.Request) -> web.Response:
    """
    Deletes the item with the specified id and its corresponding desktop object.

    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: Folder item deletion
    tags:
        - heaserver-folders-folder-items
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - name: folder_id
          in: path
          required: true
          description: The id of the folder.
          schema:
            type: string
          examples:
            example:
              summary: A folder id
              value: root
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.delete_object(request, recursive=True, activity_cb=publish_desktop_object)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}')
@action(name='heaserver-awss3folders-folder-get-open-choices', rel='hea-opener-choices hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/opener')
@action(name='heaserver-awss3folders-folder-get-properties', rel='hea-properties hea-context-menu')
@action(name='heaserver-awss3folders-folder-duplicate', rel='hea-duplicator hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/duplicator')
@action(name='heaserver-awss3folders-folder-move', rel='hea-mover hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/mover')
@action(name='heaserver-awss3folders-folder-get-create-choices', rel='hea-creator-choices hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/creator')
@action(name='heaserver-awss3folders-folder-get-trash', rel='hea-trash hea-context-menu',
        path='/volumes/{volume_id}/awss3trash')
@action(name='heaserver-awss3folders-folder-get-self', rel='self',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}')
@action(name='heaserver-awss3folders-folder-get-volume', rel='hea-volume', path='/volumes/{volume_id}')
@action(name='heaserver-awss3folders-folder-get-awsaccount', rel='hea-account',
        path='/volumes/{volume_id}/awsaccounts/me')
@action(name='heaserver-awss3folders-folder-archive', rel='hea-archive hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/archive')
@action(name='heaserver-awss3folders-folder-unarchive', rel='hea-unarchive hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/unarchive')
async def get_folder(request: web.Request) -> web.Response:
    """
    Gets the folder with the specified id.

    :param request: the HTTP request.
    :return: the requested folder or Not Found.
    ---
    summary: A specific folder.
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_folder(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/byname/{name}')
@action(name='heaserver-awss3folders-folder-get-self', rel='self',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}')
@action(name='heaserver-awss3folders-folder-get-volume', rel='hea-volume', path='/volumes/{volume_id}')
@action(name='heaserver-awss3folders-folder-get-awsaccount', rel='hea-account',
        path='/volumes/{volume_id}/awsaccounts/me')
async def get_folder_by_name(request: web.Request) -> web.Response:
    """
    Gets the folder with the specified name.

    :param request: the HTTP request.
    :return: the requested folder or Not Found.
    ---
    summary: A specific folder.
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/name'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_folder_by_name(request)


@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders')
@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/')
async def post_folder(request: web.Request) -> web.Response:
    """
    Creates a new folder.

    :param request: the HTTP request. The body of the request is expected to be a folder.
    :return: the response, with a 204 status code if a folder was created or a 400 if not. If a folder was created, the
    Location header will contain the URL of the created folder.
    ---
    summary: A specific folder.
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
    requestBody:
        description: A new folder object.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: Folder example
                  value: {
                    "template": {
                      "data": [{
                        "name": "created",
                        "value": null
                      },
                      {
                        "name": "derived_by",
                        "value": null
                      },
                      {
                        "name": "derived_from",
                        "value": []
                      },
                      {
                        "name": "description",
                        "value": null
                      },
                      {
                        "name": "display_name",
                        "value": "Bob"
                      },
                      {
                        "name": "invited",
                        "value": []
                      },
                      {
                        "name": "modified",
                        "value": null
                      },
                      {
                        "name": "name",
                        "value": "bob"
                      },
                      {
                        "name": "owner",
                        "value": "system|none"
                      },
                      {
                        "name": "shares",
                        "value": []
                      },
                      {
                        "name": "source",
                        "value": null
                      },
                      {
                        "name": "version",
                        "value": null
                      },
                      {
                        "name": "type",
                        "value": "heaobject.folder.AWSS3Folder"
                      }]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: Item example
                  value: {
                    "created": null,
                    "derived_by": null,
                    "derived_from": [],
                    "description": null,
                    "display_name": "Joe",
                    "invited": [],
                    "modified": null,
                    "name": "joe",
                    "owner": "system|none",
                    "shares": [],
                    "source": null,
                    "type": "heaobject.folder.AWSS3Folder",
                    "version": null
                  }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.create_object(request, AWSS3Folder)


@routes.put('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}')
async def put_folder(request: web.Request) -> web.Response:
    logger = logging.getLogger(__name__)
    try:
        volume_id = request.match_info['volume_id']
        bucket_id = request.match_info['bucket_id']
        id_ = request.match_info.get('id')
    except KeyError as e:
        return response.status_bad_request(f'{e} is required')

    try:
        key = decode_key(id_)
    except KeyDecodeException as e:
        return response.status_bad_request(f'Invalid id {id_}')
    if not awsservicelib.is_folder(key):
        return response.status_bad_request(f'Object {key} not a folder')

    try:
        folder = await new_heaobject_from_type(request, AWSS3Folder)
    except TypeError:
        return response.status_bad_request(f'Expected type {AWSS3FileObject}; actual object was {await request.text()}')

    s3_client: S3Client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(10) as pool:
        try:
            if key != folder.key:
                async for object in awsservicelib.list_objects(s3_client, bucket_id, key, max_keys=1000, loop=loop):
                    source_key = object['Key']
                    actual_key = source_key.removeprefix(key)
                    target_key = f'{folder.key}{actual_key}'
                    logger.debug('Copying %s/%s to %s', bucket_id, source_key, target_key)
                    await loop.run_in_executor(pool, partial(s3_client.copy_object, Bucket=bucket_id, CopySource=f'{bucket_id}/{source_key}', Key=target_key))
                    await loop.run_in_executor(pool, partial(s3_client.delete_object, Bucket=bucket_id, Key=source_key))
        except BotoClientError as e:
            return awsservicelib.handle_client_error(e)

    return await response.put(True)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders')
@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/')
@action('heaserver-awss3folders-folder-get-open-choices', rel='hea-opener-choices hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/opener')
@action(name='heaserver-awss3folders-folder-get-properties', rel='hea-properties hea-context-menu')
@action(name='heaserver-awss3folders-folder-duplicate', rel='hea-duplicator hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/duplicator')
@action(name='heaserver-awss3folders-folder-move', rel='hea-mover hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/mover')
@action(name='heaserver-awss3folders-folder-get-create-choices', rel='hea-creator-choices hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/creator')
@action(name='heaserver-awss3folders-folder-get-trash', rel='hea-trash hea-context-menu',
        path='/volumes/{volume_id}/awss3trash')
@action(name='heaserver-awss3folders-folder-get-self', rel='self',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}')
@action(name='heaserver-awss3folders-folder-archive', rel='hea-archive hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/archive')
@action(name='heaserver-awss3folders-folder-unarchive', rel='hea-unarchive hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/unarchive')
async def get_folders(request: web.Request) -> web.Response:
    """
    Gets all folders in the bucket.

    :param request: the HTTP request.
    :return: the requested folder or Not Found.
    ---
    summary: All folders.
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_all_folders(request)


@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{bucket_id}/awss3folders')
@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/')
async def get_folders_options(request: web.Request) -> web.Response:
    """
    Gets the allowed HTTP methods for a folders resource.

    :param request: the HTTP request (required).
    :response: the HTTP response.
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            text/plain:
                schema:
                    type: string
                    example: "200: OK"
      '403':
        $ref: '#/components/responses/403'
      '404':
        $ref: '#/components/responses/404'
    """
    return await response.get_options(request, ['GET', 'DELETE', 'HEAD', 'OPTIONS'])


@routes.delete('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}')
async def delete_folder(request: web.Request) -> web.Response:
    """
    Deletes the folder with the specified id.

    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: Folder deletion
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _delete_folder(request)


@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/newfolder')
@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/newfolder/')
async def post_new_folder(request: web.Request) -> web.Response:
    """
    Posts form for creating a new folder within this one.

    :param request: the HTTP request. Required.
    :return: the current folder, with a template for creating a child folder or Not Found if the requested item does not
    exist.
    ---
    summary: A folder.
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    requestBody:
        description: A new folder.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: Folder example
                  value: {
                    "template": {
                      "data": [
                      {
                        "name": "display_name",
                        "value": "Bob"
                      },
                      {
                        "name": "type",
                        "value": "heaobject.folder.AWSS3Folder"
                      }]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: Item example
                  value: {
                    "display_name": "Joe",
                    "type": "heaobject.folder.AWSS3Folder"
                  }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _post_folder_in_parent(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/newfolder')
@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/newfolder/')
@action('heaserver-awss3folders-folder-new-form')
async def get_new_folder_form(request: web.Request) -> web.Response:
    """
    Gets form for creating a new folder within this one.

    :param request: the HTTP request. Required.
    :return: the current folder, with a template for creating a child folder or Not Found if the requested item does not
    exist.
    ---
    summary: A folder.
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_folder(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/creator')
@action('heaserver-awss3folders-folder-create-folder', rel='hea-creator hea-default application/x.folder',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/newfolder')
async def get_folder_creator(request: web.Request) -> web.Response:
    """
    Opens the requested folder.

    :param request: the HTTP request. Required.
    :return: the opened folder, or Not Found if the requested item does not exist.
    ---
    summary: Folder creator choices
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '300':
        $ref: '#/components/responses/300'
      '404':
        $ref: '#/components/responses/404'
    """
    try:
        folder = await _get_folder_helper(request)
        return await response.get_multiple_choices(request, folder.to_dict())
    except ClientError as e:
        return awsservicelib.handle_client_error(e)
    except web.HTTPClientError as e:
        return e


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/opener')
@action('heaserver-awss3folders-folder-open-default', rel='hea-opener hea-default application/x.folder',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/items/')
async def get_folder_opener(request: web.Request) -> web.Response:
    """
    Opens the requested folder.

    :param request: the HTTP request. Required.
    :return: the opened folder, or Not Found if the requested item does not exist.
    ---
    summary: Folder opener choices
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '300':
        $ref: '#/components/responses/300'
      '404':
        $ref: '#/components/responses/404'
    """
    try:
        folder = await _get_folder_helper(request)
        return await response.get_multiple_choices(request, folder.to_dict())
    except ClientError as e:
        return awsservicelib.handle_client_error(e)
    except web.HTTPClientError as e:
        return e


def main():
    config = init_cmd_line(description='Repository of folders', default_port=8080)
    start(package_name='heaserver-folders-aws-s3',
          db=aws.S3Manager, wstl_builder_factory=builder_factory(__package__),
          cleanup_ctx=[publisher_cleanup_context_factory(config)],
          config=config)


async def _get_folder(request: web.Request) -> web.Response:
    """
    Gets the folder with the specified id.

    :param request: the HTTP request.
    :return: the requested folder or Not Found.
    """
    try:
        folder = await _get_folder_helper(request)
        return await response.get(request, folder.to_dict())
    except ClientError as e:
        return awsservicelib.handle_client_error(e)
    except web.HTTPClientError as e:
        return e


async def _get_folder_by_name(request: web.Request) -> web.Response:
    """
    Gets the requested folder. The volume id must be in the volume_id entry of the request's match_info dictionary.
    The bucket id must be in the bucket_id entry of the request's match_info dictionary. The folder name must be in the
    name entry of the request's match_info dictionary.

    :param request: the HTTP request (required).
    :return: the HTTP response with a 200 status code if the bucket exists and the heaobject.folder.AWSS3Folder in the body,
    403 if access was denied, 404 if no such folder was found, or 500 if an internal error occurred. The body's format
    depends on the Accept header in the request.
    """
    return await _get_folder(request)


async def _get_item_response(request) -> web.Response:
    """
    Gets the item with the specified id and in the specified folder.

    :param request: the HTTP request.
    :return: a response containing the returned item or an empty body.
    """
    return await _get_item(request)


async def _duplicate_object(request: web.Request) -> web.Response:
    return await awsservicelib.copy_object(request)


async def _move_object(request: web.Request) -> web.Response:
    copy_response = await _duplicate_object(request)
    match copy_response.status:
        case 201:
            return await awsservicelib.delete_object(request, recursive=True)
        case _:
            return response.status_generic(copy_response.status, copy_response.text)


async def _post_item_in_folder(request: web.Request) -> web.Response:
    try:
        item = await new_heaobject_from_type(request, AWSS3FolderFileItem)
    except DeserializeException as e:
        return response.status_bad_request(str(e).encode())
    return await _post_object(request, item)


async def _get_items(request: web.Request) -> web.Response:
    """
    Gets the requested folder items. The volume id must be in the volume_id entry of the request's match_info dictionary.
    The bucket id must be in the bucket_id entry of the request's match_info dictionary. The folder id must be in the
    folder_id entry of the request's match_info dictionary.

    :param request: the HTTP request (required).
    :return: the HTTP response with a 200 status code if the bucket exists and a list of
    heaobject.folder.AWSS3FileFolderItem objects in the body, 403 if access was denied, or 500 if an internal error
    occurred. The body's format depends on the Accept header in the request.
    """

    logger = logging.getLogger(__name__)

    if 'volume_id' not in request.match_info:
        return response.status_bad_request('volume_id is required')
    if 'bucket_id' not in request.match_info:
        return response.status_bad_request('bucket_id is required')
    if 'folder_id' not in request.match_info:
        return response.status_bad_request('folder_id is required')
    volume_id = request.match_info['volume_id']
    bucket_name = request.match_info['bucket_id']
    folder_id_ = request.match_info['folder_id']

    s3 = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    folder_key = awsservicelib.decode_folder(folder_id_)
    loop = asyncio.get_running_loop()
    try:
        if folder_key is None:
            # We couldn't decode the folder_id, and we need to check if the user can access the bucket in order to
            # decide which HTTP status code to respond with (Forbidden vs Not Found).
            return await awsservicelib.return_bucket_status_or_not_found(bucket_name, loop, s3)
        logger.debug('Getting all folders in item %s in bucket %s', folder_key, bucket_name)
        folders: dict[str, AWSS3FolderFileItem] = {}
        async for obj in awsservicelib.list_objects(s3, bucket_id=bucket_name, prefix=folder_key, loop=loop):
            key = obj['Key']
            key_ = key.removeprefix(folder_key)
            try:
                if key_ == '':  # The folder
                    continue
                actual_key = key_[:key_.index('/') + 1]  # A folder
                is_folder_ = True
            except ValueError:
                actual_key = key_  # Not a folder
                is_folder_ = False
            actual_id = encode_key(folder_key + actual_key)
            logger.debug('Found item %s in bucket %s', actual_key, bucket_name)
            item = AWSS3FolderFileItem()
            item.id = actual_id
            item.modified = obj['LastModified']
            item.created = obj['LastModified']
            item.owner = request.headers.get(SUB, NONE_USER)
            item.actual_object_id = actual_id
            item.folder_id = folder_id_
            item.storage_class = S3StorageClass[obj['StorageClass']] if not is_folder_ else None
            item.bucket_id = bucket_name
            item.source = AWS_S3
            item.volume_id = volume_id
            if is_folder_:
                item.actual_object_uri = str(
                    URL('/volumes') / volume_id / 'buckets' / bucket_name / 'awss3folders' / actual_id)
                item.actual_object_type_name = AWSS3Folder.get_type_name()
            else:
                item.actual_object_uri = str(
                    URL('/volumes') / volume_id / 'buckets' / bucket_name / 'awss3files' / actual_id)
                item.actual_object_type_name = AWSS3FileObject.get_type_name()
                item.size = obj['Size']
            if actual_key in folders:
                item_ = folders[actual_key]
                if item_.modified is not None and item.modified is not None:
                    item_.modified = max(item_.modified, item.modified)
                elif item.modified is not None:
                    item_.modified = item.modified
            else:
                folders[actual_key] = item
        return await response.get_all(request, list(i.to_dict() for i in folders.values()))
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)
    except ParamValidationError as e:
        return response.status_bad_request(str(e))


async def _has_item(request: web.Request) -> web.Response:
    """
    Checks for the existence of the requested folder item. The volume id must be in the volume_id entry of the
    request's match_info dictionary. The bucket id must be in the bucket_id entry of the request's match_info
    dictionary. The folder id must be in the folder_id entry of the request's match_info dictionary. The item id must
    be in the id entry of the request's match_info dictionary.

    :param request: the HTTP request (required).
    :return: the HTTP response with a 200 status code if the item exists, 403 if access was denied, or 500 if an
    internal error occurred.
    """
    logger = logging.getLogger(__name__)

    if 'volume_id' not in request.match_info:
        return response.status_bad_request('volume_id is required')
    if 'bucket_id' not in request.match_info:
        return response.status_bad_request('bucket_id is required')
    if 'folder_id' not in request.match_info:
        return response.status_bad_request('folder_id is required')
    if 'id' not in request.match_info:
        return response.status_bad_request('id is required')

    volume_id = request.match_info['volume_id']
    folder_id_ = request.match_info['folder_id']
    bucket_name = request.match_info['bucket_id']

    s3 = await request.app[HEA_DB].get_client(request, 's3', volume_id)

    loop = asyncio.get_running_loop()

    if folder_id_ == awsservicelib.ROOT_FOLDER.id:
        folder_id = ''
    else:
        try:
            folder_id = decode_key(folder_id_)
            if not awsservicelib.is_folder(folder_id):
                folder_id = None
        except KeyDecodeException:
            # Let the bucket query happen so that we consistently return Forbidden if the user lacks permissions
            # for the bucket.
            folder_id = None
    try:
        if folder_id is None:
            # We couldn't decode the folder_id, and we need to check if the user can access the bucket in order to
            # decide which HTTP status code to respond with (Forbidden vs Not Found).
            await loop.run_in_executor(None, partial(s3.head_bucket, Bucket=bucket_name))
            return response.status_not_found()
        item_id = decode_key(request.match_info['id'])
        if item_id.startswith(folder_id):
            item_id_ = item_id.removeprefix(folder_id)
            if len(item_id_) > 1 and '/' in item_id_[:-1]:
                return response.status_not_found()
        else:
            return response.status_not_found()
        logger.debug('Checking if item %s in folder %s in bucket %s exists', item_id, folder_id, bucket_name)
        response_ = await loop.run_in_executor(None, partial(s3.list_objects_v2, Bucket=bucket_name, Prefix=item_id,
                                                             MaxKeys=1))
        if response_['KeyCount'] > 0:
            return response.status_ok()
        return await response.get(request, None)
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)
    except KeyDecodeException:
        return response.status_not_found()


async def _has_folder(request: web.Request) -> web.Response:
    """
    Checks for the existence of the requested folder. The volume id must be in the volume_id entry of the request's
    match_info dictionary. The bucket id must be in the bucket_id entry of the request's match_info dictionary. The
    folder id must be in the id entry of the request's match_info dictionary.

    :param request: the HTTP request (required).
    :return: the HTTP response with a 200 status code if the folder exists, 403 if access was denied, 404 if the folder
    was not found, or 500 if an internal error occurred.
    """
    if 'volume_id' not in request.match_info:
        return response.status_bad_request('volume_id is required')
    if 'bucket_id' not in request.match_info:
        return response.status_bad_request('bucket_id is required')
    if 'id' not in request.match_info and 'folder_id' not in request.match_info:
        return response.status_bad_request('id or folder_id is required')
    volume_id = request.match_info['volume_id']
    bucket_name = request.match_info['bucket_id']
    folder_name = request.match_info['id'] if 'id' in request.match_info else request.match_info['folder_id']

    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    if folder_name == awsservicelib.ROOT_FOLDER.id:
        return response.status_ok()
    else:
        try:
            folder_id: str | None = decode_key(folder_name)
            if not awsservicelib.is_folder(folder_id):
                folder_id = None
        except KeyDecodeException:
            # Let the bucket query happen so that we consistently return Forbidden if the user lacks permissions
            # for the bucket.
            folder_id = None

    try:
        if folder_id is None:
            # We couldn't decode the folder_id, and we need to check if the user can access the bucket in order to
            # decide which HTTP status code to respond with (Forbidden vs Not Found).
            s3_client.head_bucket(Bucket=bucket_name)
            return response.status_not_found()
        response_ = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_id, MaxKeys=1)
        logging.debug('Result of has_folder: %s', response_)
        if response_['KeyCount'] == 0:
            return response.status_not_found()
        return response.status_ok()
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)


async def _get_all_folders(request: web.Request) -> web.Response:
    """
    Gets all folders in a bucket. The volume id must be in the volume_id entry of the request's
    match_info dictionary. The bucket id must be in the bucket_id entry of the request's match_info dictionary.

    :param request: the HTTP request (required).
    :return: the HTTP response with a 200 status code if the bucket exists and a Collection+JSON document in the body
    containing any heaobject.folder.AWSS3Folder objects, 403 if access was denied, or 500 if an internal error occurred. The
    body's format depends on the Accept header in the request.
    """
    logger = logging.getLogger(__name__)
    if 'volume_id' not in request.match_info:
        return response.status_bad_request('volume_id is required')
    if 'bucket_id' not in request.match_info:
        return response.status_bad_request('bucket_id is required')
    volume_id = request.match_info['volume_id']
    bucket_name = request.match_info['bucket_id']
    s3 = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    loop = asyncio.get_running_loop()
    try:
        logger.debug('Getting all folders from bucket %s', bucket_name)
        folders = []
        async for obj in awsservicelib.list_objects(s3, bucket_name, loop=loop):
            key = obj['Key']
            if awsservicelib.is_folder(key):
                encoded_key = encode_key(key)
                logger.debug('Found folder %s in bucket %s', key[:-1], bucket_name)
                folder = _new_folder(bucket_name, obj, encoded_key, request)
                folders.append(folder.to_dict())
        return await response.get_all(request, folders)
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)


async def _delete_folder(request: web.Request, recursive=False) -> web.Response:
    """
    Deletes the requested folder and optionally all contents. The volume id must be in the volume_id entry of the
    request's match_info dictionary. The bucket id must be in the bucket_id entry of the request's match_info
    dictionary. The folder id must be in the id entry of the request's match_info dictionary.

    :param request: the aiohttp Request (required).
    :param recursive: if True, this function will delete the folder and all of its contents, otherwise it will return
    a 400 error if the folder is not empty.
    :return: the HTTP response with a 204 status code if the folder was successfully deleted, 403 if access was denied,
    404 if the folder was not found, or 500 if an internal error occurred.
    """
    return await awsservicelib.delete_object(request, recursive=recursive)


def _new_folder(bucket_name: str, contents: dict[str, Any], encoded_key: str,
                request: web.Request) -> AWSS3Folder:
    folder = AWSS3Folder()
    folder.id = encoded_key
    folder.modified = contents['LastModified']
    folder.created = contents['LastModified']
    folder.owner = request.headers.get(SUB, NONE_USER)
    folder.bucket_id = bucket_name
    folder.source = AWS_S3
    return folder


async def _get_folder_helper(request: web.Request) -> AWSS3Folder:
    if 'volume_id' not in request.match_info:
        raise web.HTTPBadRequest(text='volume_id is required')
    if 'bucket_id' not in request.match_info:
        raise web.HTTPBadRequest(text='bucket_id is required')
    if 'id' not in request.match_info and 'name' not in request.match_info:
        raise web.HTTPBadRequest(text='either id or name is required')
    volume_id = request.match_info['volume_id']
    bucket_name = request.match_info['bucket_id']
    folder_name = request.match_info['id'] if 'id' in request.match_info else request.match_info['name']

    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    try:
        folder_id: str | None = decode_key(folder_name)
        if not awsservicelib.is_folder(folder_id):
            folder_id = None
    except KeyDecodeException:
        # Let the bucket query happen so that we consistently return Forbidden if the user lacks permissions
        # for the bucket.
        folder_id = None
    if folder_id is None:
        # We couldn't decode the folder_id, and we need to check if the user can access the bucket in order to
        # decide which HTTP status code to respond with (Forbidden vs Not Found).
        s3_client.head_bucket(Bucket=bucket_name)
        raise web.HTTPNotFound
    response_ = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_id, MaxKeys=1)
    logging.debug('Result of get_folder: %s', response_)
    if folder_id is None or response_['KeyCount'] == 0:
        raise web.HTTPNotFound
    contents = response_['Contents'][0]
    encoded_key = encode_key(response_['Prefix'])
    return _new_folder(bucket_name, contents, encoded_key, request)


async def _post_folder_in_parent(request: web.Request) -> web.Response:
    """
    Creates a new folder in a bucket. The volume id must be in the volume_id entry of the request.match_info dictionary.
    The bucket id must be in the bucket_id entry of request.match_info. The folder id must be in the id entry of
    request.match_info.

    :param request: the HTTP request (required).
    :return: the HTTP response, with a 201 status code if successful with the URL to the new item in the Location
    header, 403 if access was denied, 404 if the volume or bucket could not be found, or 500 if an internal error
    occurred.
    """
    logger = logging.getLogger(__name__)

    try:
        folder = await new_heaobject_from_type(request, AWSS3Folder)
    except DeserializeException as e:
        logger.exception('Invalid new folder')
        return response.status_bad_request(f'Invalid new folder: {str(e)}')
    if folder.display_name is None:
        return response.status_bad_request("display_name is required")
    if 'volume_id' not in request.match_info:
        return response.status_bad_request('volume_id is required')
    if 'bucket_id' not in request.match_info:
        return response.status_bad_request('bucket_id is required')
    if 'id' not in request.match_info:
        return response.status_bad_request('id is required')
    if folder is None:
        return response.status_bad_request('folder is a required field')
    volume_id = request.match_info['volume_id']
    bucket_id = request.match_info['bucket_id']
    id_ = request.match_info['id']

    if id_ is None:
        return response.status_bad_request('folder_id cannot be None')

    if '/' in folder.display_name:
        return response.status_bad_request(f"The item's display name may not have slashes in it")
    if id_ == awsservicelib.ROOT_FOLDER.id:
        item_folder_id = ''
    else:
        try:
            item_folder_id = decode_key(id_)
            if not awsservicelib.is_folder(item_folder_id):
                item_folder_id = None
        except KeyDecodeException:
            item_folder_id = None
    item_name = join(item_folder_id, folder.display_name)
    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    loop = asyncio.get_running_loop()
    try:
        if item_folder_id is None:
            await loop.run_in_executor(None, partial(s3_client.head_bucket, Bucket=bucket_id))
            return response.status_not_found()
        if folder.type == AWSS3Folder.get_type_name():
            item_name += '/'
        else:
            return response.status_bad_request(f'Unsupported type {folder.get_type_name()}')
        response_ = await loop.run_in_executor(None, partial(s3_client.head_object, Bucket=bucket_id,
                                                             Key=item_name))  # check if folder exists, if not throws an exception
        logger.debug('Result of post_object: %s', response_)
        return response.status_bad_request(body=f"Item {item_name} already exists")
    except BotoClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == awsservicelib.CLIENT_ERROR_404:  # folder doesn't exist
            await loop.run_in_executor(None, partial(s3_client.put_object, Bucket=bucket_id, Key=item_name))
            logger.info('Added folder %s', item_name)
            return await response.post(request, encode_key(item_name),
                                       f"volumes/{volume_id}/buckets/{bucket_id}/awss3folders")
        elif error_code == awsservicelib.CLIENT_ERROR_NO_SUCH_BUCKET:
            return response.status_not_found()
        else:
            return response.status_bad_request(str(e))


async def _get_item(request: web.Request) -> web.Response:
    """
    Gets the requested folder item. The volume id must be in the volume_id entry of the request's match_info dictionary.
    The bucket id must be in the bucket_id entry of the request's match_info dictionary. The folder id must be in the
    folder_id entry of the request's match_info dictionary. The item id must be in the id entry of the request's
    match_info dictionary.

    :param request: the HTTP request (required).
    :param add_actions_hook: a callable for adding run-time actions to the returned JSON document. Use this for WeSTL
    actions that may be optionally added to the WeSTL document depending on the value of the item's
    actual_object_type_name. The callable should call heaserver.service.wstl.add_run_time_action to add actions.
    :return: the HTTP response with a 200 status code if the bucket exists and the heaobject.folder.AWSS3FileFolderItem
    object in the body, 403 if access was denied, or 500 if an internal error occurred. The body's format depends on
    the Accept header in the request.
    """
    logger = logging.getLogger(__name__)

    if 'volume_id' not in request.match_info:
        return response.status_bad_request('volume_id is required')
    if 'bucket_id' not in request.match_info:
        return response.status_bad_request('bucket_id is required')
    if 'folder_id' not in request.match_info:
        return response.status_bad_request('folder_id is required')
    if 'id' not in request.match_info:
        return response.status_bad_request('id is required')

    volume_id = request.match_info['volume_id']
    folder_id_ = request.match_info['folder_id']
    bucket_name = request.match_info['bucket_id']

    decoded_folder_key, decoded_key, folder_or_item_not_found = _check_folder_and_object_keys(folder_id_, request)

    s3 = await request.app[HEA_DB].get_client(request, 's3', volume_id)

    try:
        loop = asyncio.get_running_loop()

        if folder_or_item_not_found:
            return await awsservicelib.return_bucket_status_or_not_found(bucket_name, loop, s3)

        logger.debug('Getting item %s in folder %s in bucket %s', decoded_key, decoded_folder_key, bucket_name)
        response_ = await loop.run_in_executor(None, partial(s3.list_objects_v2, Bucket=bucket_name, Prefix=decoded_key,
                                                             MaxKeys=1))
        def _second_to_last(text, pattern):
            return text.rfind(pattern, 0, text.rfind(pattern))

        if response_['KeyCount'] > 0:
            for obj in response_['Contents']:
                id_ = obj['Key']
                is_folder_ = awsservicelib.is_folder(id_)
                id_encoded = encode_key(id_)
                logger.debug('Found item %s in bucket %s', id_, bucket_name)

                item = AWSS3FolderFileItem()
                item.id = id_encoded
                item.modified = obj['LastModified']
                item.created = obj['LastModified']
                item.owner = request.headers.get(SUB, NONE_USER)
                item.folder_id = folder_id_
                item.actual_object_id = id_encoded
                item.storage_class = S3StorageClass[obj['StorageClass']] if not is_folder_ else None
                item.bucket_id = bucket_name
                item.source = AWS_S3
                item.volume_id = volume_id
                if is_folder_:
                    item.actual_object_uri = str(
                        URL('/volumes') / volume_id / 'buckets' / bucket_name / 'awss3folders' / id_encoded)
                    item.actual_object_type_name = AWSS3Folder.get_type_name()
                else:
                    item.actual_object_uri = str(
                        URL('/volumes') / volume_id / 'buckets' / bucket_name / 'awss3files' / id_encoded)
                    item.actual_object_type_name = AWSS3FileObject.get_type_name()
                    item.size = obj['Size']
                return await response.get(request, item.to_dict())
        return await response.get(request, None)
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)


def _check_folder_and_object_keys(folder_id_: str | None, request: web.Request) -> tuple[str | None, str | None, bool]:
    folder_or_item_not_found = False
    decoded_folder_key = awsservicelib.decode_folder(folder_id_)
    if decoded_folder_key is None:
        folder_or_item_not_found = True
    try:
        decoded_key = decode_key(request.match_info['id'])
        if not is_object_in_folder(decoded_key, decoded_folder_key):
            folder_or_item_not_found = True
    except KeyDecodeException as e:
        decoded_key = None
        folder_or_item_not_found = True

    return decoded_folder_key, decoded_key, folder_or_item_not_found


async def _get_folder_move_template(request: web.Request) -> web.Response:
    logger = logging.getLogger(__name__)
    id_ = request.match_info['id']
    try:
        id = encode_key(split(awsservicelib.decode_folder(id_))[0])
        add_run_time_action(request, name='heaserver-awss3folders-folder-get-target', rel='headata-target', path=(
            '/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/' + id) if id else '/volumes/{volume_id}/buckets/{bucket_id}')
        return await _get_folder(request)
    except KeyDecodeException as e:
        logger.exception('Error getting parent key')
        return response.status_not_found()


async def _post_object(request: web.Request, item: AWSS3FolderFileItem) -> web.Response:
    """
    Creates a new object in a bucket. The volume id must be in the volume_id entry of the request.match_info dictionary.
    The bucket id must be in the bucket_id entry of request.match_info. The folder id must be in the folder_id entry of
    request.match_info.

    :param request: the HTTP request (required).
    :param item: the heaobject.folder.AWSS3FileFolderItem to create (required).
    :return: the HTTP response, with a 201 status code if successful with the URL to the new item in the Location
    header, 403 if access was denied, 404 if the volume or bucket could not be found, or 500 if an internal error
    occurred.
    """
    logger = logging.getLogger(__name__)
    if item.display_name is None:
        return response.status_bad_request("display_name is required")
    if 'volume_id' not in request.match_info:
        return response.status_bad_request('volume_id is required')
    if 'bucket_id' not in request.match_info:
        return response.status_bad_request('bucket_id is required')
    if 'folder_id' not in request.match_info:
        return response.status_bad_request('folder_id is required')
    if item is None:
        return response.status_bad_request('item is a required field')
    volume_id = request.match_info['volume_id']
    bucket_id = request.match_info['bucket_id']
    folder_id = request.match_info['folder_id']

    if item.folder_id is not None and folder_id != item.folder_id:
        return response.status_bad_request(
            f'folder_id in object was {item.folder_id} but folder_id in URL was {folder_id}')
    if folder_id is None:
        return response.status_bad_request('folder_id cannot be None')
    if item.folder_id is not None and item.folder_id != folder_id:
        return response.status_bad_request(
            f'Inconsistent folder_id in URL versus item: {folder_id} vs {item.folder_id}')
    if '/' in item.display_name:
        return response.status_bad_request(f"The item's display name may not have slashes in it")
    if folder_id == awsservicelib.ROOT_FOLDER.id:
        item_folder_id = ''
    else:
        try:
            item_folder_id = decode_key(folder_id)
            if not awsservicelib.is_folder(item_folder_id):
                item_folder_id = None
        except KeyDecodeException:
            item_folder_id = None

    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    loop = asyncio.get_running_loop()
    try:
        if item_folder_id is None:
            await loop.run_in_executor(None, partial(s3_client.head_bucket, Bucket=bucket_id))
            return response.status_not_found()
        item_name = f'{item_folder_id}{item.display_name}'
        if item.actual_object_type_name == AWSS3Folder.get_type_name():
            item_name += '/'
        elif item.actual_object_type_name == AWSS3FileObject.get_type_name():
            pass
        else:
            return response.status_bad_request(f'Unsupported actual_object_type_name {item.actual_object_type_name}')
        response_ = await loop.run_in_executor(None, partial(s3_client.head_object, Bucket=bucket_id,
                                                             Key=item_name))  # check if item exists, if not throws an exception
        logger.debug('Result of post_object: %s', response_)
        return response.status_bad_request(body=f"Item {item_name} already exists")
    except BotoClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == awsservicelib.CLIENT_ERROR_404:  # folder doesn't exist
            await loop.run_in_executor(None, partial(s3_client.put_object, Bucket=bucket_id, Key=item_name))
            logger.info('Added folder %s', item_name)
            return await response.post(request, encode_key(item_name),
                                       f"volumes/{request.match_info['volume_id']}/buckets/{request.match_info['bucket_id']}/awss3folders/{folder_id}/items")
        elif error_code == awsservicelib.CLIENT_ERROR_NO_SUCH_BUCKET:
            return response.status_not_found()
        else:
            return response.status_bad_request(str(e))
