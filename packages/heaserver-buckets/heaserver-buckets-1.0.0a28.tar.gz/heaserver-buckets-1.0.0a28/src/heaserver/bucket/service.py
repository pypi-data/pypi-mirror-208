"""
The HEA Server Buckets Microservice provides ...
"""
import logging

from heaserver.service import response, client
from heaserver.service.runner import init_cmd_line, routes, start, web
from heaserver.service.db import awsservicelib, aws
from heaserver.service.db.database import get_options, has_volume
from heaserver.service.wstl import builder_factory, action
from heaobject.folder import AWSS3BucketItem, Folder, AWSS3Folder
from heaobject.volume import AWSFileSystem
from heaobject.bucket import AWSBucket
from heaobject.error import DeserializeException
from heaobject.root import Tag
from heaserver.service.appproperty import HEA_DB
from heaserver.service.oidcclaimhdrs import SUB
from heaserver.service.heaobjectsupport import new_heaobject_from_type, type_to_resource_url
from heaserver.service.sources import AWS_S3
from botocore.exceptions import ClientError as BotoClientError
import asyncio
from typing import Generator, Any
from yarl import URL
from mypy_boto3_s3.client import S3Client
from functools import partial
from aiohttp.client_exceptions import ClientError, ClientResponseError
from datetime import datetime
from mypy_boto3_s3.service_resource import S3ServiceResource
from mypy_boto3_s3.type_defs import TagTypeDef
from concurrent.futures import ThreadPoolExecutor

MONGODB_BUCKET_COLLECTION = 'buckets'


@routes.get('/volumes/{volume_id}/buckets/{id}')
@action('heaserver-buckets-bucket-get-open-choices', rel='hea-opener-choices hea-context-menu',
        path='/volumes/{volume_id}/buckets/{id}/opener')
@action(name='heaserver-buckets-bucket-get-properties', rel='hea-properties hea-context-menu')
@action(name='heaserver-buckets-bucket-get-create-choices', rel='hea-creator-choices hea-context-menu',
        path='/volumes/{volume_id}/buckets/{id}/creator')
@action(name='heaserver-buckets-bucket-get-trash', rel='hea-trash hea-context-menu', path='/volumes/{volume_id}/awss3trash')
@action(name='heaserver-buckets-bucket-get-self', rel='self', path='/volumes/{volume_id}/buckets/{id}')
@action(name='heaserver-buckets-bucket-get-volume', rel='hea-volume', path='/volumes/{volume_id}')
@action(name='heaserver-buckets-bucket-get-awsaccount', rel='hea-account', path='/volumes/{volume_id}/awsaccounts/me')
async def get_bucket(request: web.Request) -> web.Response:
    """
    Gets the bucket with the specified id.
    :param request: the HTTP request.
    :return: the requested bucket or Not Found.
    ---
    summary: A specific bucket.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
      '404':
        $ref: '#/components/responses/404'
    """

    return await _get_bucket(request=request)


@routes.get('/volumes/{volume_id}/buckets/byname/{bucket_name}')
@action(name='heaserver-buckets-bucket-get-self', rel='self', path='/volumes/{volume_id}/buckets/{id}')
@action(name='heaserver-buckets-bucket-get-volume', rel='hea-volume', path='/volumes/{volume_id}')
@action(name='heaserver-buckets-bucket-get-awsaccount', rel='hea-account', path='/volumes/{volume_id}/awsaccounts/me')
async def get_bucket_by_name(request: web.Request) -> web.Response:
    """
    Gets the bucket with the specified name.
    :param request: the HTTP request.
    :return: the requested bucket or Not Found.
    ---
    summary: A specific bucket.
    tags:
        - heaserver-buckets
    parameters:
        - name: bucket_name
          in: path
          required: true
          description: The name of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: Name of the bucket
              value: hci-foundation
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_bucket(request=request)


@routes.get('/volumes/{volume_id}/buckets/{id}/opener')
@action('heaserver-buckets-bucket-open-content', rel=f'hea-opener hea-context-aws hea-default {Folder.get_mime_type()}',
        path='/volumes/{volume_id}/buckets/{id}/awss3folders/root/items/')
async def get_bucket_opener(request: web.Request) -> web.Response:
    """
    Gets bucket opener choices.

    :param request: the HTTP Request.
    :return: A Response object with a status of Multiple Choices or Not Found.
    ---
    summary: Bucket opener choices
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - $ref: '#/components/parameters/id'
    responses:
      '300':
        $ref: '#/components/responses/300'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _bucket_opener(request)


@routes.get('/volumes/{volume_id}/buckets/{id}/creator')
@action('heaserver-buckets-bucket-create-folder', rel='hea-creator hea-default application/x.folder',
        path='/volumes/{volume_id}/buckets/{id}/newfolder')
async def get_bucket_creator(request: web.Request) -> web.Response:
    """
    Gets bucket creator choices.

    :param request: the HTTP Request.
    :return: A Response object with a status of Multiple Choices or Not Found.
    ---
    summary: Bucket creator choices
    tags:
        - heaserver-buckets
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
        - $ref: '#/components/parameters/id'
    responses:
      '300':
        $ref: '#/components/responses/300'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _bucket_opener(request)


@routes.get('/volumes/{volume_id}/buckets/{id}/newfolder')
@routes.get('/volumes/{volume_id}/buckets/{id}/newfolder/')
@action('heaserver-buckets-bucket-new-folder-form')
async def get_new_folder_form(request: web.Request) -> web.Response:
    """
    Gets form for creating a new folder within this bucket.

    :param request: the HTTP request. Required.
    :return: the current folder, with a template for creating a child folder or Not Found if the requested item does not
    exist.
    ---
    summary: A folder.
    tags:
        - heaserver-buckets
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
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_bucket(request)


@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/newfolder')
@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/newfolder/')
async def post_new_folder(request: web.Request) -> web.Response:
    """
    Gets form for creating a new folder within this bucket.

    :param request: the HTTP request. Required.
    :return: the current folder, with a template for creating a child folder or Not Found if the requested item does not
    exist.
    ---
    summary: A folder.
    tags:
        - heaserver-buckets
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
    volume_id = request.match_info['volume_id']
    bucket_id = request.match_info['bucket_id']
    folder_url = await type_to_resource_url(request, AWSS3Folder, file_system_type_or_type_name=AWSFileSystem)
    if folder_url is None:
        raise ValueError('No AWSS3Folder service registered')
    headers = {SUB: request.headers[SUB]} if SUB in request.headers else None
    resource_base = str(URL(folder_url) / volume_id / 'buckets' / bucket_id / 'awss3folders' / 'root' / 'newfolder')
    folder = await new_heaobject_from_type(request, type_=AWSS3Folder)
    try:
        id_ = await client.post(request.app, resource_base, data=folder, headers=headers)
        return await response.post(request, id_, resource_base)
    except ClientResponseError as e:
        return response.status_generic(status=e.status, body=str(e))
    except ClientError as e:
        return response.status_generic(status=500, body=str(e))


@routes.get('/volumes/{volume_id}/buckets')
@routes.get('/volumes/{volume_id}/buckets/')
@action('heaserver-buckets-bucket-get-open-choices', rel='hea-opener-choices hea-context-menu',
        path='/volumes/{volume_id}/buckets/{id}/opener')
@action(name='heaserver-buckets-bucket-get-properties', rel='hea-properties hea-context-menu')
@action(name='heaserver-buckets-bucket-get-create-choices', rel='hea-creator-choices hea-context-menu',
        path='/volumes/{volume_id}/buckets/{id}/creator')
@action(name='heaserver-buckets-bucket-get-trash', rel='hea-trash hea-context-menu', path='/volumes/{volume_id}/awss3trash')
@action(name='heaserver-buckets-bucket-get-self', rel='self', path='/volumes/{volume_id}/buckets/{id}')
async def get_all_buckets(request: web.Request) -> web.Response:
    """
    Gets all buckets.
    :param request: the HTTP request.
    :return: all buckets.
    ---
    summary: get all buckets for a hea-volume associate with account.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_all_buckets(request)


@routes.get('/volumes/{volume_id}/bucketitems')
@routes.get('/volumes/{volume_id}/bucketitems/')
@action(name='heaserver-buckets-item-get-actual', rel='hea-actual', path='{+actual_object_uri}')
@action(name='heaserver-buckets-item-get-volume', rel='hea-volume', path='/volumes/{volume_id}')
async def get_all_bucketitems(request: web.Request) -> web.Response:
    """
    Gets all buckets.
    :param request: the HTTP request.
    :return: all buckets.
    ---
    summary: get all bucket items for a hea-volume associate with account.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_all_bucket_items(request)


@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{id}')
async def get_bucket_options(request: web.Request) -> web.Response:
    """
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-buckets
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
    return await get_options(request, ['GET', 'DELETE', 'HEAD', 'OPTIONS', 'PUT'], _has_bucket)


@routes.route('OPTIONS', '/volumes/{volume_id}/buckets')
@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/')
async def get_buckets_options(request: web.Request) -> web.Response:
    """
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-buckets
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
    return await get_options(request, ['GET', 'HEAD', 'POST', 'OPTIONS'], has_volume)


@routes.route('OPTIONS', '/volumes/{volume_id}/bucketitems')
@routes.route('OPTIONS', '/volumes/{volume_id}/bucketitems/')
async def get_bucketitems_options(request: web.Request) -> web.Response:
    """
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-buckets
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
    return await get_options(request, ['GET', 'HEAD', 'OPTIONS'], has_volume)


@routes.get('/ping')
async def ping(request: web.Request) -> web.Response:
    """
    For testing whether the service is up.

    :param request: the HTTP request.
    :return: Always returns status code 200.
    """
    return response.status_ok(None)


@routes.post('/volumes/{volume_id}/buckets')
@routes.post('/volumes/{volume_id}/buckets/')
async def post_bucket(request: web.Request) -> web.Response:
    """
    Posts the provided bucket.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    ---
    summary: Bucket Creation
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    requestBody:
      description: Attributes of new Bucket.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Bucket example
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
                    "value": "hci-test-bucket"
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
                    "value": "hci-test-bucket"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shared_with",
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
                    "name": "encrypted",
                    "value": true
                  },
                  {
                    "name": "versioned",
                    "value": false
                  },
                  {
                    "name": "locked",
                    "value": false
                  },
                  {
                    "name": "tags",
                    "value": []
                  },
                  {
                    "name": "region",
                    "value": us-west-2
                  },
                  {
                    "name": "permission_policy",
                    "value": null
                  },
                  {
                    "name": "type",
                    "value": "heaobject.bucket.AWSBucket"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Bucket example
              value: {
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": "This is a description",
                "display_name": "hci-test-bucket",
                "invited": [],
                "modified": null,
                "name": "hci-test-bucket",
                "owner": "system|none",
                "shared_with": [],
                "source": null,
                "type": "heaobject.bucket.AWSBucket",
                "version": null,
                encrypted: true,
                versioned: false,
                locked: false,
                tags: [],
                region: "us-west-2",
                permission_policy: null
              }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _post_bucket(request=request)


@routes.put('/volumes/{volume_id}/buckets/{id}')
async def put_bucket(request: web.Request) -> web.Response:
    """
    Updates the provided bucket. Only the tags may be updated.

    :param request: the HTTP request.
    :return: a Response object with a status of No Content, or Not Found if no
    bucket exists with that name, or Bad Request if there is a problem with the
    request.
    ---
    summary: Bucket update.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - $ref: '#/components/parameters/id'
    requestBody:
      description: Attributes of the bucket.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Bucket example
              value: {
                "template": {
                  "data": [
                  {
                    "name": "id",
                    "value": "hci-test-bucket"
                  },
                  {
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
                    "value": "hci-test-bucket"
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
                    "value": "hci-test-bucket"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shared_with",
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
                    "name": "encrypted",
                    "value": true
                  },
                  {
                    "name": "versioned",
                    "value": false
                  },
                  {
                    "name": "locked",
                    "value": false
                  },
                  {
                    "name": "tags",
                    "value": []
                  },
                  {
                    "name": "region",
                    "value": us-west-2
                  },
                  {
                    "name": "permission_policy",
                    "value": null
                  },
                  {
                    "name": "type",
                    "value": "heaobject.bucket.AWSBucket"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Bucket example
              value: {
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": "This is a description",
                "display_name": "hci-test-bucket",
                "invited": [],
                "modified": null,
                "name": "hci-test-bucket",
                "owner": "system|none",
                "shared_with": [],
                "source": null,
                "type": "heaobject.bucket.AWSBucket",
                "version": null,
                encrypted: true,
                versioned: false,
                locked: false,
                tags: [],
                region: "us-west-2",
                permission_policy: null
              }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    try:
        volume_id = request.match_info['volume_id']
        bucket_name = request.match_info['id']
    except KeyError as e:
        return response.status_bad_request(str(e))

    if not _has_bucket(request):
        return await response.put(False)

    try:
        b = await new_heaobject_from_type(request=request, type_=AWSBucket)
        if not b:
            return web.HTTPBadRequest(body="Put body is not an HEAObject AWSBucket")
        if not b.name:
            return web.HTTPBadRequest(body="Bucket name is required in the body")
        if b.name != bucket_name:
            return web.HTTPBadRequest(body='Bucket name in URL does not match bucket in body')
    except DeserializeException as e:
        return web.HTTPBadRequest(body=str(e))

    #We only support changing the bucket tags.
    try:
        await _put_bucket_tags(request, volume_id, bucket_name, b.tags)
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)
    return await response.put(True)




@routes.delete('/volumes/{volume_id}/buckets/{id}')
async def delete_bucket(request: web.Request) -> web.Response:
    """
    Deletes the bucket with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: A specific bucket.
    tags:
        - heaserver-buckets
    parameters:
        - name: id
          in: path
          required: true
          description: The id of the bucket to delete.
          schema:
            type: string
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
      '404':
        $ref: '#/components/responses/404'
    """
    return await _delete_bucket(request)


def main() -> None:
    config = init_cmd_line(description='a service for managing buckets and their data within the cloud',
                           default_port=8080)
    start(package_name='heaserver-buckets', db=aws.S3Manager,
          wstl_builder_factory=builder_factory(__package__), config=config)


async def _delete_bucket(request: web.Request) -> web.Response:
    """
    Deletes bucket and all contents

    :param request: the aiohttp Request (required).
    :return: the HTTP response.
    """
    logger = logging.getLogger(__name__)
    volume_id = request.match_info.get("volume_id", None)
    bucket_id = request.match_info.get("id", None)
    if not volume_id:
        return web.HTTPBadRequest(body="volume_id is required")
    if not bucket_id:
        return web.HTTPBadRequest(body="bucket_id is required")

    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    try:
        s3_client.head_bucket(Bucket=bucket_id)
        await _delete_bucket_objects(request, volume_id, bucket_id)
        del_bucket_result = s3_client.delete_bucket(Bucket=bucket_id)
        logger.info(del_bucket_result)
        return web.HTTPNoContent()
    except BotoClientError as e:
        logger.error(e)
        return web.HTTPNotFound()


async def _delete_bucket_objects(request: web.Request, volume_id: str, bucket_name: str,
                                 delete_versions: bool = False) -> web.Response:
    """
    Deletes all objects inside a bucket

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param bucket_name: Bucket to delete
    :param delete_versions: Boolean indicating if the versioning should be deleted as well, defaults to False
    :return: the HTTP response with a 204 status code if successful, or 404 if the bucket was not found.
    """
    try:
        s3_resource = await request.app[HEA_DB].get_resource(request, 's3', volume_id)
        s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
        s3_client.head_bucket(Bucket=bucket_name)
        s3_bucket = s3_resource.Bucket(bucket_name)
        if delete_versions:
            bucket_versioning = s3_resource.BucketVersioning(bucket_name)
            if bucket_versioning.status == 'Enabled':
                del_obj_all_result = s3_bucket.object_versions.delete()
                logging.info(del_obj_all_result)
            else:
                del_obj_all_result = s3_bucket.objects.all().delete()
                logging.info(del_obj_all_result)
        else:
            del_obj_all_result = s3_bucket.objects.all().delete()
            logging.info(del_obj_all_result)
        return web.HTTPNoContent()
    except BotoClientError as e:
        logging.error(e)
        return web.HTTPNotFound()


async def _get_all_bucket_items(request: web.Request) -> web.Response:
    """
    Gets all buckets as AWSS3BucketItem objects.

    :param request: the aiohttp Request (required).
    :return: An HTTP response with a list of available buckets.
    """

    try:
        volume_id = request.match_info.get("volume_id", None)
        if not volume_id:
            return web.HTTPBadRequest(body="volume_id is required")
        s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)

        resp = await asyncio.get_running_loop().run_in_executor(None, s3_client.list_buckets)

        def bucket_items() -> Generator[AWSS3BucketItem, None, None]:
            for bucket in resp['Buckets']:
                bucket_item = AWSS3BucketItem()
                bucket_item.bucket_id = bucket['Name']
                bucket_item.modified = bucket['CreationDate']
                bucket_item.created = bucket['CreationDate']
                bucket_item.actual_object_type_name = AWSBucket.get_type_name()
                bucket_item.actual_object_id = bucket['Name']
                bucket_item.actual_object_uri = str(URL('/volumes') / volume_id / 'buckets' / bucket['Name'])
                yield bucket_item

    except BotoClientError as e:
        logging.error(e)
        return response.status_bad_request()

    return await response.get_all(request, [buck.to_dict() for buck in bucket_items()])


async def _get_all_buckets(request: web.Request) -> web.Response:
    """
    List available buckets by name

    :param request: the aiohttp Request (required).
    :return: An HTTP response with a list of available buckets.
    """

    try:
        volume_id = request.match_info.get("volume_id", None)
        if not volume_id:
            return web.HTTPBadRequest(body="volume_id is required")
        s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
        s3_resource = await request.app[HEA_DB].get_resource(request, 's3', volume_id)

        resp = s3_client.list_buckets()
        async_bucket_list = []
        for bucket in resp['Buckets']:
            bucket_ = __get_bucket(volume_id=volume_id, bucket_name=bucket["Name"],
                                  s3_client=s3_client, s3_resource=s3_resource,
                                  creation_date=bucket['CreationDate'], sub=request.headers.get(SUB))
            if bucket_ is not None:
                async_bucket_list.append(bucket_)

        buck_list = await asyncio.gather(*async_bucket_list)
    except BotoClientError as e:
        logging.error(e)
        return response.status_bad_request()
    bucket_dict_list = [buck.to_dict() for buck in buck_list if buck is not None]

    return await response.get_all(request, bucket_dict_list)


async def _get_bucket(request: web.Request) -> web.Response:
    """
    List a single bucket's attributes

    :param request: the aiohttp Request (required).
    :return:  return the single bucket object requested or HTTP Error Response
    """
    if 'volume_id' not in request.match_info:
        raise ValueError('volume_id is required')
    if 'id' not in request.match_info and 'bucket_name' not in request.match_info:
        raise ValueError('id or bucket_name is required')
    volume_id = request.match_info['volume_id']
    bucket_id = request.match_info.get('id')
    bucket_name = request.match_info.get('bucket_name')
    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    s3_resource = await request.app[HEA_DB].get_resource(request, 's3', volume_id)

    try:
        bucket_result = await __get_bucket(volume_id=volume_id, s3_resource=s3_resource, s3_client=s3_client,
                                          bucket_name=bucket_name, bucket_id=bucket_id, sub=request.headers.get(SUB))
        if type(bucket_result) is AWSBucket:
            return await response.get(request=request, data=bucket_result.to_dict())
        return await response.get(request, data=None)
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)


async def __get_bucket(volume_id: str, s3_resource: S3ServiceResource, s3_client: S3Client,
                     bucket_name: str | None = None, bucket_id: str | None = None,
                     creation_date: datetime | None = None,
                     sub: str | None = None) -> AWSBucket | None:
    """
    :param volume_id: the volume id
    :param s3_client:  the boto3 client
    :param bucket_name: str the bucket name (optional)
    :param bucket_id: str the bucket id (optional)
    :param creation_date: str the bucket creation date (optional)
    :return: Returns either the AWSBucket or None for Not Found or Forbidden, else raises ClientError
    """
    logger = logging.getLogger(__name__)
    try:
        loop = asyncio.get_running_loop()
        if not volume_id or (not bucket_id and not bucket_name):
            raise ValueError("volume_id is required and either bucket_name or bucket_id")

        b = AWSBucket()
        b.name = bucket_id if bucket_id else bucket_name
        b.id = bucket_id if bucket_id else bucket_name
        if bucket_id is not None:
            b.display_name = bucket_id
        elif bucket_name is not None:
            b.display_name = bucket_name
        async_bucket_methods = []
        b_from_boto = await loop.run_in_executor(None, s3_resource.Bucket, b.name)
        b.created = creation_date if creation_date else b_from_boto.creation_date
        b.bucket_id = b.name
        b.source = AWS_S3
        b.arn = f'arn:aws:s3::{b.id}'
        b.owner = sub

        async def _get_version_status(b: AWSBucket):
            logger.debug('Getting version status of bucket %s', b.name)
            try:
                bucket_versioning = await loop.run_in_executor(None,
                                                               partial(s3_client.get_bucket_versioning, Bucket=b.name))
                logger.debug('bucket_versioning=%s', bucket_versioning)
                if 'Status' in bucket_versioning:
                    b.versioned = bucket_versioning['Status'] == 'Enabled'
                    logger.debug('Got version status of bucket %s successfully', b.name)
                else:
                    logger.debug('No version status information for bucket %s', b.name)
            except BotoClientError as ce:
                logger.exception('Error getting the version status of bucket %s')
                raise ce

        async_bucket_methods.append(_get_version_status(b))

        async def _get_region(b: AWSBucket):
            logger.debug('Getting region of bucket %s', b.name)
            try:
                loc = await loop.run_in_executor(None, partial(s3_client.get_bucket_location, Bucket=b.name))
                b.region = loc['LocationConstraint'] or 'us-east-1'
            except BotoClientError as ce:
                logging.exception('Error getting the region of bucket %s', b.name)
                raise ce
            logger.debug('Got region of bucket %s successfully', b.name)

        async_bucket_methods.append(_get_region(b))

        # todo how to find partition dynamically. The format is arn:PARTITION:s3:::NAME-OF-YOUR-BUCKET
        # b.arn = "arn:"+"aws:"+":s3:::"

        async def _get_tags(b: AWSBucket):
            logger.debug('Getting tags of bucket %s', b.name)
            try:
                tagging = await loop.run_in_executor(None, partial(s3_client.get_bucket_tagging, Bucket=b.name))
                b.tags = _from_aws_tags(aws_tags=tagging['TagSet'])
            except BotoClientError as ce:
                if ce.response['Error']['Code'] != 'NoSuchTagSet':
                    logging.exception('Error getting the tags of bucket %s', b.name)
                    raise ce
            logger.debug('Got tags of bucket %s successfully', b.name)

        async_bucket_methods.append(_get_tags(b))

        async def _get_encryption_status(b: AWSBucket):
            logger.debug('Getting encryption status of bucket %s', b.name)
            try:
                encrypt = await loop.run_in_executor(None, partial(s3_client.get_bucket_encryption, Bucket=b.name))
                rules: list = encrypt['ServerSideEncryptionConfiguration']['Rules']
                b.encrypted = len(rules) > 0
            except BotoClientError as e:
                if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                    b.encrypted = False
                else:
                    logger.exception('Error getting the encryption status of bucket %s', b.name)
                    raise e
            logger.debug('Got encryption status of bucket %s successfully', b.name)

        async_bucket_methods.append(_get_encryption_status(b))

        async def _get_bucket_policy(b: AWSBucket):
            logger.debug('Getting bucket policy of bucket %s', b.name)
            try:
                bucket_policy = await loop.run_in_executor(None, partial(s3_client.get_bucket_policy, Bucket=b.name))
                b.permission_policy = bucket_policy['Policy']
            except BotoClientError as e:
                if e.response['Error']['Code'] != 'NoSuchBucketPolicy':
                    logging.exception('Error getting the bucket policy of bucket %s', b.name)
                    raise e
            logger.debug('Got bucket policy of bucket %s successfully', b.name)

        async_bucket_methods.append(_get_bucket_policy(b))

        async def _get_bucket_lock_status(b: AWSBucket):
            logger.debug('Getting bucket lock status of bucket %s', b.name)
            try:
                lock_config = await loop.run_in_executor(None, partial(s3_client.get_object_lock_configuration,
                                                                       Bucket=b.name))
                b.locked = lock_config['ObjectLockConfiguration']['ObjectLockEnabled'] == 'Enabled'
            except BotoClientError as e:
                if e.response['Error']['Code'] != 'ObjectLockConfigurationNotFoundError':
                    logger.exception('Error getting the lock status of bucket %s', b.name)
                    raise e
                b.locked = False
            logger.debug('Got bucket lock status of bucket %s successfully', b.name)

        async_bucket_methods.append(_get_bucket_lock_status(b))

        # todo need to lazy load this these metrics
        total_size = None
        obj_count = None
        mod_date = None
        # FIXME need to calculate this metric data in a separate call. Too slow
        # s3bucket = s3_resource.Bucket(b.name)
        # for obj in s3bucket.objects.all():
        #     total_size += obj.size
        #     obj_count += 1
        #     mod_date = obj.last_modified if mod_date is None or obj.last_modified > mod_date else mod_date
        b.size = total_size
        b.object_count = obj_count
        b.modified = mod_date
        await asyncio.gather(*async_bucket_methods)
    except BotoClientError as e:
        error_code = e.response['Error']['Code']
        if error_code in ('403', '404', 'NoSuchBucket'):
            return None
        logger.exception(f'Error getting bucket %s', b.name)
        raise e
    return b


def _from_aws_tags(aws_tags: list[TagTypeDef]) -> list[Tag]:
    """
    :param aws_tags: Tags obtained from boto3 Tags api
    :return: List of HEA Tags
    """
    hea_tags = []
    for t in aws_tags:
        tag = Tag()
        tag.key = t['Key']
        tag.value = t['Value']
        hea_tags.append(tag)
    return hea_tags


async def _has_bucket(request: web.Request) -> web.Response:
    """
    Checks for the existence of the requested bucket. The volume id must be in the volume_id entry of the
    request's match_info dictionary. The bucket id must be in the id entry of the request's match_info
    dictionary.

    :param request: the HTTP request (required).
    :return: the HTTP response with a 200 status code if the bucket exists, 403 if access was denied, or 500 if an
    internal error occurred.
    """
    if 'volume_id' not in request.match_info:
        return response.status_bad_request('volume_id is required')
    if 'id' not in request.match_info and 'bucket_id' not in request.match_info:
        return response.status_bad_request('id or bucket_id must be provided')
    volume_id = request.match_info['volume_id']
    bucket_id = request.match_info.get('id', request.match_info.get('bucket_id', None))
    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    s3_resource = await request.app[HEA_DB].get_resource(request, 's3', volume_id)

    try:
        bucket_result = await __get_bucket(volume_id=volume_id, s3_resource=s3_resource, s3_client=s3_client,
                                          bucket_id=bucket_id, sub=request.headers.get(SUB))
        if type(bucket_result) is AWSBucket:
            return response.status_ok()
        else:
            return response.status_not_found()
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)

async def _bucket_opener(request: web.Request) -> web.Response:
    """
    Returns links for opening the bucket. The volume id must be in the volume_id entry of the request's
    match_info dictionary. The bucket id must be in the id entry of the request's match_info dictionary.

    :param request: the HTTP request (required).
    :return: the HTTP response with a 200 status code if the bucket exists and a Collection+JSON document in the body
    containing an heaobject.bucket.AWSBucket object and links, 403 if access was denied, 404 if the bucket
    was not found, or 500 if an internal error occurred.
    """
    if 'volume_id' not in request.match_info:
        return response.status_bad_request('volume_id is required')
    if 'id' not in request.match_info:
        return response.status_bad_request('id is required')
    volume_id = request.match_info['volume_id']
    bucket_id = request.match_info['id']
    bucket_name = request.match_info.get('bucket_name', None)

    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    s3_resource = await request.app[HEA_DB].get_resource(request, 's3', volume_id)

    try:
        bucket_result = await __get_bucket(volume_id=volume_id, s3_resource=s3_resource, s3_client=s3_client,
                                          bucket_name=bucket_name, bucket_id=bucket_id, sub=request.headers.get(SUB))
        return await response.get_multiple_choices(request,
                                                   bucket_result.to_dict() if bucket_result is not None else None)
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)


async def _post_bucket(request: web.Request):
    """
    Create an S3 bucket in a specified region. Will fail if the bucket with the given name already exists.
    If a region is not specified, the bucket is created in the S3 default region (us-east-1).

    The request must have either a volume id, which is the id string of the volume representing the user's AWS account,
    or an id, which is the account id.

    :param request: the aiohttp Request (required). A volume_id must be specified in its match info. The AWSBucket
    in the body of the request must have a name.
    """
    logger = logging.getLogger(__name__)
    volume_id = request.match_info.get('volume_id', None)
    if not volume_id:
        volume_id = await awsservicelib.get_volume_id_for_account_id(request)
        if not volume_id:
            return web.HTTPBadRequest(body="either id or volume_id is required")
    try:
        b = await new_heaobject_from_type(request=request, type_=AWSBucket)
        if not b:
            return web.HTTPBadRequest(body="Post body is not an HEAObject AWSBUCKET")
        if not b.name:
            return web.HTTPBadRequest(body="Bucket name is required")
    except DeserializeException as e:
        return web.HTTPBadRequest(body=str(e))

    s3_client: S3Client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    try:
        s3_client.head_bucket(Bucket=b.name)  # check if bucket exists, if not throws an exception
        return web.HTTPConflict()
    except BotoClientError as e:
        loop = asyncio.get_running_loop()
        try:
            # todo this is a privileged actions need to check if authorized
            error_code = e.response['Error']['Code']

            if error_code == '404':  # bucket doesn't exist
                create_bucket_params: dict[str, Any] = {'Bucket': b.name}
                put_bucket_policy_params = {
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
                if b.region:
                    create_bucket_params['CreateBucketConfiguration'] = {'LocationConstraint': b.region}
                if b.locked:
                    create_bucket_params['ObjectLockEnabledForBucket'] = True

                await loop.run_in_executor(None, partial(s3_client.create_bucket, **create_bucket_params))
                # make private bucket
                await loop.run_in_executor(None, partial(s3_client.put_public_access_block, Bucket=b.name,
                                                         PublicAccessBlockConfiguration=put_bucket_policy_params))

                await _put_bucket_encryption(b, loop, s3_client)
                # todo this is a privileged action need to check if authorized ( may only be performed by bucket owner)

                await _put_bucket_versioning(bucket_name=b.name, s3_client=s3_client, is_versioned=b.versioned)

                await _put_bucket_tags(request=request, volume_id=volume_id,
                                       bucket_name=b.name, new_tags=b.tags)

            elif error_code == '403':  # already exists
                logger.exception("A bucket named %s already exists", b.display_name)
                return web.HTTPBadRequest(body=f"A bucket named {b.display_name} already exists")
            else:
                logger.exception(str(e))
                return response.status_bad_request(str(e))
        except BotoClientError as e2:
            logger.exception(e2.response)
            try:
                await loop.run_in_executor(None, partial(s3_client.head_bucket, Bucket=b.name))
                del_bucket_result = await loop.run_in_executor(None, partial(s3_client.delete_bucket, Bucket=b.name))
                logging.info(f"deleted failed bucket {b.name} details: \n{del_bucket_result}")
            except BotoClientError:  # bucket doesn't exist so no clean up needed
                pass
            return web.HTTPBadRequest(body=f"Bucket named {b.display_name} was not created: {e2.response['Error'].get('Message')}")
        return await response.post(request, b.name, f'volumes/{volume_id}/buckets')


async def _put_bucket_encryption(b, loop, s3_client):
    if b.encrypted:
        SSECNF = 'ServerSideEncryptionConfigurationNotFoundError'
        try:
            await loop.run_in_executor(None, partial(s3_client.get_bucket_encryption, Bucket=b.name))
        except BotoClientError as e:
            if e.response['Error']['Code'] == SSECNF:
                config = \
                    {'Rules': [{'ApplyServerSideEncryptionByDefault':
                                    {'SSEAlgorithm': 'AES256'}, 'BucketKeyEnabled': False}]}
                await loop.run_in_executor(None, partial(s3_client.put_bucket_encryption, Bucket=b.name,
                                                         ServerSideEncryptionConfiguration=config))
            else:
                logging.error(e.response['Error']['Code'])
                raise e


async def _put_bucket_versioning(bucket_name: str, is_versioned: bool | None, s3_client: S3Client):
    """
    Use To change turn on or off bucket versioning settings. Note that if the Object Lock
    is turned on for the bucket you can't change these settings.

    :param bucket_name: The bucket name
    :param is_versioned: For toggling on or off the versioning
    :param s3_client: Pass the active client if exists (optional)
    :raises BotoClientError: if an error occurred setting version information.
    """
    logger = logging.getLogger(__name__)
    loop = asyncio.get_running_loop()
    vconfig = {
        'MFADelete': 'Disabled',
        'Status': 'Enabled' if is_versioned else 'Suspended',
    }
    vresp = await loop.run_in_executor(None, partial(s3_client.put_bucket_versioning, Bucket=bucket_name,
                                                     VersioningConfiguration=vconfig))
    logger.debug(vresp)


async def _put_bucket_tags(request: web.Request, volume_id: str, bucket_name: str,
                           new_tags: list[Tag] | None):
    """
    Creates or adds to a tag list for bucket

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account (required).
    :param bucket_name: The bucket (required).
    :param new_tags: new tags to be added tag list on specified bucket. Pass in the empty list or None to clear out
    the bucket's tags.
    :raises BotoClientError: if an error occurs interacting with S3.
    """
    if request is None:
        raise ValueError('request is required')
    if volume_id is None:
        raise ValueError('volume_id is required')
    if bucket_name is None:
        raise ValueError('bucket_name is required')
    aws_new_tags = await _to_aws_tags(new_tags or [])

    s3_resource = await request.app[HEA_DB].get_resource(request, 's3', volume_id)
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor()
    bucket_tagging = await loop.run_in_executor(executor, s3_resource.BucketTagging, bucket_name)
    await loop.run_in_executor(executor, bucket_tagging.delete)
    await loop.run_in_executor(executor, partial(bucket_tagging.put, Tagging={'TagSet': aws_new_tags}))


async def _to_aws_tags(hea_tags: list[Tag]) -> list[dict[str, str]]:
    """
    :param hea_tags: HEA tags to converted to aws tags compatible with boto3 api
    :return: aws tags
    """
    aws_tag_dicts = []
    for hea_tag in hea_tags:
        aws_tag_dict = {}
        aws_tag_dict['Key'] = hea_tag.key
        aws_tag_dict['Value'] = hea_tag.value
        aws_tag_dicts.append(aws_tag_dict)
    return aws_tag_dicts
