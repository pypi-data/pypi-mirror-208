"""
This module defines functions that create HTTP responses.

All GET responses except for OPTIONS include Cache-Control, Pragma, and Expires headers to request no caching.
"""
from aiohttp import web, hdrs
from aiohttp.client_exceptions import ClientResponseError
from aiohttp.helpers import ETag
from hashlib import md5
from heaserver.service import requestproperty, appproperty
from heaserver.service.representor import factory as representor_factory
from heaserver.service.representor.representor import Link
from yarl import URL
import logging
from typing import Union, List, Optional, Dict, Any, Mapping
from .aiohttp import SupportsAsyncRead
from .wstl import RuntimeWeSTLDocumentBuilder
from heaobject.root import DesktopObjectDict
from multidict import istr, CIMultiDict, CIMultiDictProxy
from .caching_strategy import CachingStrategy

TEXT_PLAIN_HTTP_HEADERS: Union[Mapping[Union[str, istr], str], None] = {hdrs.CONTENT_TYPE: 'text/plain; charset=UTF-8'}
NO_CACHE_HEADERS = {hdrs.CACHE_CONTROL: 'no-cache, no-store, must-revalidate', hdrs.PRAGMA: 'no-cache', hdrs.EXPIRES: '0'}


def status_generic(status: int, body: Optional[Union[bytes, str]] = None, headers: Union[Mapping[Union[str, istr], str], CIMultiDict[str], CIMultiDictProxy[str], None] = None) -> web.Response:
    """
    Returns a newly created HTTP response object
    """
    body_ = body.encode() if isinstance(body, str) else body
    return web.Response(status=status, body=body_, headers=headers)


def status_not_found(body: Optional[Union[bytes, str]] = None,
                     headers: Union[Mapping[Union[str, istr], str], None] = None) -> web.Response:
    """
    Returns a newly created HTTP response object with status code 404 and an optional body.

    :param body: the body of the message, typically an explanation of what was not found.  If a string, this function
    will encode it to bytes using UTF-8 encoding.
    :param headers: any headers that you want to add to the response. In addition, the response will have a
    Content-Type header that should not be overridden.
    :return: aiohttp.web.Response with a 404 status code.
    """
    body_ = body.encode() if isinstance(body, str) else body
    headers_ = TEXT_PLAIN_HTTP_HEADERS if isinstance(body, str) else None
    if headers and 'Content-Type' in headers:
        return web.HTTPInternalServerError(body='The Content-Type header cannot be overridden')
    return web.HTTPNotFound(body=body_, headers=(headers_ | headers) if headers else headers_)


def status_multiple_choices(default_url: Union[URL, str], body: Optional[Union[bytes, str]] = None, content_type: str = 'application/json') -> web.Response:
    """
    Returns a newly created HTTP response object with status code 300. This is for implementing client-side content
    negotiation, described at https://developer.mozilla.org/en-US/docs/Web/HTTP/Content_negotiation.

    :param default_url: the URL of the default choice. Required.
    :param body: content with link choices.  If a string, this function will encode it to bytes using UTF-8 encoding.
    :param content_type: optional content_type (defaults to 'application/json'). Cannot be None.
    :return: aiohttp.web.Response object with a 300 status code.
    """
    body_ = body.encode() if isinstance(body, str) else body
    return web.HTTPMultipleChoices(str(default_url),
                                   body=body_,
                                   headers={hdrs.CONTENT_TYPE: content_type, hdrs.LOCATION: str(default_url if default_url else '#')})


def status_moved(location: str | URL):
    """
    Returns a newly created HTTP response object with status code 301.

    :param location: the URL for the client to redirect to.
    :return: aiohttp.web.Response object with a 301 status code.
    """
    return web.HTTPMovedPermanently(location=str(location))


def status_bad_request(body: Optional[Union[bytes, str]] = None) -> web.Response:
    """
    Returns a newly created HTTP response object with status code 400 and an optional body.

    :param body: the body of the message, typically an explanation of why the request is bad.  If a string, this
    function will encode it to bytes using UTF-8 encoding.
    :return: aiohttp.web.Response with a 400 status code.
    """
    body_ = body.encode() if isinstance(body, str) else body
    headers = TEXT_PLAIN_HTTP_HEADERS if isinstance(body, str) else None
    return web.HTTPBadRequest(body=body_, headers=headers)


def status_created(base_url: Union[URL, str], resource_base: str, inserted_id: str) -> web.Response:
    """
    Returns a newly created HTTP response object with status code 201 and the Location header set.

    :param base_url: the service's base URL (required).
    :param resource_base: the common base path fragment for all resources of this type (required).
    :param inserted_id: the id of the newly created object (required).

    :return: aiohttp.web.Response with a 201 status code and the Location header set to the URL of the created object.
    """
    if inserted_id is None:
        raise ValueError('inserted_id cannot be None')
    return web.HTTPCreated(headers={hdrs.LOCATION: str(URL(base_url) / resource_base / str(inserted_id))})


def status_ok(body: Optional[Union[bytes, str]] = None, content_type: str = 'application/json',
              headers: Union[Mapping[Union[str, istr], str], None] = None) -> web.Response:
    """
    Returns a newly created HTTP response object with status code 201, the provided Content-Type header, and the
    provided body.

    :param body: the body of the response. If a string, this function will encode it to bytes using UTF-8 encoding.
    :param content_type: the content type of the response (default is application/json).
    :param headers: any headers that you want to add to the response, in addition to the content type. If the content
    type is also in this dictionary, then its value will override that of the content_type argument. If the body is
    a string and no content type header is specified in either the content_type or headers argument, a default value
    for the content type will be used.
    :return: aiohttp.web.Response object with a 200 status code.
    """
    if isinstance(body, str):
        body_ = body.encode()
    else:
        body_ = body
    if content_type is not None:
        headers_ = {hdrs.CONTENT_TYPE: content_type}
    else:
        headers_ = {}
    if headers:
        headers_.update(headers)
    if isinstance(body, str) and hdrs.CONTENT_TYPE not in headers_:
        headers_.update(TEXT_PLAIN_HTTP_HEADERS)
    return web.HTTPOk(headers=headers_, body=body_)


def status_no_content() -> web.Response:
    """
    Returns a newly created HTTP response object with status code 204.

    :return: aiohttp.web.Response object with a 204 status code.
    """
    return web.HTTPNoContent()


def status_not_acceptable(body: Optional[Union[bytes, str]] = None) -> web.Response:
    """
    Returns a newly created HTTP response object with status code 406.

    :param body: the body of the message, typically an explanation of why the request is bad.  If a string, this
    function will encode it to bytes using UTF-8 encoding.
    :return: aiohttp.web.Response object with a 406 status code.
    """
    body_ = body.encode() if isinstance(body, str) else body
    return web.HTTPNotAcceptable(body=body_)


def status_internal_error(body: Optional[Union[bytes, str]] = None) -> web.Response:
    """
    Returns a newly created HTTP response object with status code 500.

    :param body: the body of the message, typically an explanation of why the request is bad.  If a string, this
    function will encode it to bytes using UTF-8 encoding.
    :return: aiohttp.web.Response object with a 500 status code.
    """
    body_ = body.encode() if isinstance(body, str) else body
    return web.HTTPInternalServerError(body=body_)


def status_from_exception(e: ClientResponseError) -> web.Response:
    """
    Generates a response from an aiohttp ClientResponseError, using the status code and message from the ClientResponse
    object.

    :param e: a ClientResponseError object.
    :return: aiohttp.web.Response object with the ClientResopnseError's status code.
    """
    return web.Response(status=e.status, reason=e.message)


def status_forbidden(body: Optional[Union[bytes, str]] = None) -> web.Response:
    """
    Returns a newly created HTTP response object with status code 403.

    :param body: the body of the message, typically an explanation of why the request is bad.  If a string, this
    function will encode it to bytes using UTF-8 encoding.
    :return: aiohttp.web.Response object with a 500 status code.
    """
    body_ = body.encode() if isinstance(body, str) else body
    return web.HTTPForbidden(body=body_)


async def get(request: web.Request, data: Optional[DesktopObjectDict]) -> web.Response:
    """
    Create and return a HTTP response object in response to a GET request for one or more HEA desktop object resources.

    :param request: the HTTP request (required).
    :param data: a HEA desktop object dict. May be None if you want no data to be included in the response.
    :return: aiohttp.web.Response object, with status code 200, containing a body with the HEA desktop object, or
    status code 404 if the data argument is None.
    """
    if data:
        return await _handle_get_result(request, data)
    else:
        return web.HTTPNotFound()


async def get_multiple_choices(request: web.Request,
                               result: Optional[Union[DesktopObjectDict, List[DesktopObjectDict]]],
                               caching_strategy: CachingStrategy = None) -> web.Response:
    """
    Create and return a HTTP response object in response to a GET request with information about different
    representations that are available for opening the requested HEA desktop object. Unlike the get function, this
    function sets the response's status code to 300 to indicate that is for the purpose of client-side content
    negotiation. More information about content negotiation is available from
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Content_negotiation.

    :param request: the HTTP request (required). If an Accepts header is provided, MIME types that do not support
    links will be ignored.
    :param result: a HEA desktop object dict or list of desktop object dicts.
    :param caching_strategy: the caching strategy to use. If None, then response headers are sent to request no caching.
    :return: aiohttp.web.Response object with status code 300, and a body containing the HEA desktop object and links
    representing possible choices for opening the HEA desktop object; status code 404 if no HEA desktop object dict
    was provided; or status code 406 if content negotiation failed to determine an acceptable content type.
    """
    _logger = logging.getLogger(__name__)
    if result is not None:
        wstl_builder: RuntimeWeSTLDocumentBuilder = request[requestproperty.HEA_WSTL_BUILDER]
        wstl_builder.data = result if isinstance(result, list) else [result]
        wstl_builder.href = str(request.url)
        run_time_doc = wstl_builder()
        _logger.debug('Run-time WeSTL document is %s', run_time_doc)

        representor = representor_factory.from_accept_header(request.headers[hdrs.ACCEPT])
        _logger.debug('Using %s output format', representor)
        if representor is None:
            return status_not_acceptable()

        default_url: Optional[Union[URL, str]] = None

        def link_callback(action_index: int, link: Link):
            nonlocal default_url
            if default_url is None or 'default' in link.rel:
                default_url = link.href
        body = await representor.formats(request, run_time_doc, link_callback=link_callback)
        _logger.debug('Response body is %s', body)
        etag = _compute_etag(body)
        if request.if_none_match and etag in request.if_none_match:
            return web.HTTPNotModified()
        response = status_multiple_choices(default_url=default_url if default_url else '#',
                                       body=body,
                                       content_type=representor.MIME_TYPE)
        if caching_strategy:
            response.etag = etag
        else:
            response.headers.update(NO_CACHE_HEADERS)
        return response
    else:
        return web.HTTPNotFound(headers={} if caching_strategy else NO_CACHE_HEADERS)


async def get_from_wstl(request: web.Request, run_time_doc: Dict[str, Any]) -> web.Response:
    """
    Handle a get request that returns a run-time WeSTL document. Any actions in the document are added to the
    request's run-time WeSTL documents, and the href of the action is prepended by the service's base URL. The actions
    in the provided run-time document are expected to have a relative href.

    :param request: the HTTP request (required).
    :param run_time_doc: a run-time WeSTL document containing data.
    :return: aiohttp.web.Response object with a body containing the object in a JSON array of objects.
    """
    return await _handle_get_result_from_wstl(request, run_time_doc)


async def get_all_from_wstl(request: web.Request, run_time_docs: List[Dict[str, Any]]) -> web.Response:
    """
    Handle a get all request that returns one or more run-time WeSTL documents. Any actions in the documents are added
    to the request's run-time WeSTL documents, and the href of the action is prepended by the service's base URL. The
    actions in the provided run-time document are expected to have a relative href.

    :param request: the HTTP request (required).
    :param run_time_docs: a list of run-time WeSTL documents containing data.
    :return: aiohttp.web.Response object with a body containing the object in a JSON array of objects.
    """
    return await _handle_get_result_from_wstl(request, run_time_docs)


async def get_all(request: web.Request, data: List[DesktopObjectDict]) -> web.Response:
    """
    Create and return a Response object in response to a GET request for all HEA desktop object resources in a
    collection.

    :param request: the HTTP request (required).
    :param data: a list of HEA desktop object dicts.
    :return: aiohttp.web.Response object with a body containing the object in a JSON array of objects.
    """
    return await _handle_get_result(request, data)


async def get_options(request: web.Request, methods: List[str]) -> web.Response:
    """
    Create and return a Response object in response to an OPTIONS request.

    :param request: the HTTP request (required).
    :param methods: the allowed HTTP methods.
    :return: an aiohttp.web.Response object with a 200 status code and an Allow header.
    """
    methods_ = ', '.join(methods)
    etag = _compute_etag(methods_)
    if request.if_none_match and etag in request.if_none_match:
        return web.HTTPNotModified()
    resp = web.HTTPOk()
    resp.headers[hdrs.ALLOW] = methods_
    return resp


async def get_streaming(request: web.Request, out: SupportsAsyncRead, content_type: str = 'application/json',
                        caching_strategy: CachingStrategy = None) -> web.StreamResponse:
    """
    Create and return a StreamResponse object in response to a GET request for the content associated with a HEA desktop
    object.

    :param request: the HTTP request (required).
    :param out: a file-like object with an asynchronous read() method (required).
    :param content_type: optional content type.
    :param caching_strategy: the caching strategy to employ. If unspecified, response headers are sent to request no
    caching.
    :return: aiohttp.web.StreamResponse object with status code 200.
    """
    logger = logging.getLogger(__name__)
    logger.debug('Getting content with content type %s', content_type)
    if content_type is not None:
        response_ = web.StreamResponse(status=200, reason='OK', headers={hdrs.CONTENT_TYPE: content_type})
    else:
        response_ = web.StreamResponse(status=200, reason='OK')
    await response_.prepare(request)
    flag = True
    try:
        while chunk := await out.read(1024):
            await response_.write(chunk)
        out.close()
        flag = False
    finally:
        if flag:
            try:
                out.close()
            except OSError:
                pass

    await response_.write_eof()
    if not caching_strategy:
        response_.headers.update(NO_CACHE_HEADERS)
    return response_


async def post(request: web.Request, result: Optional[str], resource_base: str) -> web.Response:
    """
    Create and return a Response object in response to a POST request to create a new HEA desktop object resource.

    :param request: the HTTP request (required).
    :param result: the id of the POST'ed HEA object, or None if the POST failed due to a bad request.
    :param resource_base: the common base path fragment for all resources of this type (required).
    :return: aiohttp.web.Response with Created status code and the URL of the created object, or a Response with a Bad
    Request status code if the result is None.
    """
    logger = logging.getLogger(__name__)
    if result is not None:
        return await _handle_post_result(request, resource_base, result)
    else:
        logger.debug('No result for request %s', request.url)
        return web.HTTPBadRequest()


async def put(result: bool) -> web.Response:
    """
    Handle the result from a put request.

    :param result: whether any objects were updated.
    :return: aiohttp.web.Response object with status code 203 (No Content) or 404 (Not Found).
    """
    if result:
        return web.HTTPNoContent()
    else:
        return web.HTTPNotFound()


async def delete(result: bool) -> web.Response:
    """
    Handle the result from a delete request.

    :param result: whether any objects were deleted.
    :return: aiohttp.web.Response object with status code 203 (No Content) or 404 (Not Found).
    """
    if result:
        return web.HTTPNoContent()
    else:
        return web.HTTPNotFound()


async def _handle_get_result(request: web.Request, data: Union[DesktopObjectDict, List[DesktopObjectDict]]) -> web.Response:
    """
    Handle the result from a get request. Returns a Response object, the body of which will always contain a list of
    JSON objects.

    :param request: the HTTP request object. Cannot be None.
    :param data: the retrieved HEA desktop objects as a dict or a list of dicts, with each dict representing a
    desktop object with its attributes as name-value pairs.
    :return: aiohttp.web.Response object, either a 200 status code and the requested JSON object in the body, or status
    code 404 (Not Found).
    """
    if data is not None:
        wstl_builder = request[requestproperty.HEA_WSTL_BUILDER]
        wstl_builder.data = data if isinstance(data, list) else [data]
        wstl_builder.href = str(request.url)
        return await _handle_get_result_from_wstl(request, wstl_builder())
    else:
        return web.HTTPNotFound()


async def _handle_get_result_from_wstl(request: web.Request,
                                       run_time_docs: Union[Dict[str, Any], List[Dict[str, Any]]],
                                       caching_strategy: CachingStrategy = None) -> web.Response:
    """
    Handle a get or get all request that returns one or more run-time WeSTL documents. Any actions in the documents are
    added to the request's run-time WeSTL documents, and the href of the action is prepended by the service's base URL.
    The actions in the provided run-time documents are expected to have a relative href.

    :param request: the HTTP request object. Cannot be None.
    :param run_time_docs: a list of run-time WeSTL documents containing data
    :param caching_strategy: what caching headers to send. By default, headers are generated to prevent caching.
    :return: aiohttp.web.Response object, with a 200 status code and the requested JSON objects in the body,
    status code 406 (Not Acceptable) if content negotiation failed to determine an acceptable content type, or status
    code 404 (Not Found).
    """
    _logger = logging.getLogger(__name__)
    _logger.debug('Run-time WeSTL document is %s', run_time_docs)
    if run_time_docs is not None:
        representor = representor_factory.from_accept_header(request.headers.get(hdrs.ACCEPT, None))
        _logger.debug('Using %s output format', representor)
        if representor is None:
            return status_not_acceptable()
        body = await representor.formats(request, run_time_docs)
        _logger.debug('Response body is %s', body)
        if caching_strategy:
            etag = _compute_etag(body)
            if request.if_none_match and etag in request.if_none_match:
                return web.HTTPNotModified()
        response = status_ok(body=body, content_type=representor.MIME_TYPE, headers=NO_CACHE_HEADERS if not caching_strategy else None)
        if caching_strategy:
            response.etag = etag
        return response
    else:
        return status_not_found()


async def _handle_post_result(request: web.Request, resource_base: str, inserted_id: str) -> web.Response:
    """
    Handle the result from a post request.

    :param request: the HTTP request object (required).
    :param resource_base: the common base path fragment for all resources of this type (required).
    :param inserted_id: the id of the newly created object (required).
    :return: aiohttp.web.Response object with status code 201 (Created).
    """
    return status_created(request.app[appproperty.HEA_COMPONENT], resource_base, inserted_id)


async def _get_options(methods: List[str]) -> web.Response:
    """
    Create and return a Response object in response to an OPTIONS request.

    :param methods: the allowed HTTP methods.
    :return: an aiohttp.web.Response object with a 200 status code and an Allow header.
    """
    resp = web.HTTPOk()
    resp.headers[hdrs.ALLOW] = ', '.join(methods)
    return resp


def _compute_etag(body: bytes | str, encoding='utf-8') -> ETag:
    """
    Computes an ETag from a bytes or str object.

    @param body: a bytes or str object.
    @param encoding: for bytes bodies, an optional encoding.
    @return: an ETag object.
    """
    if isinstance(body, str):
        body_ = body.encode(encoding)
    else:
        body_ = bytes(body)
    return ETag(md5(body_).hexdigest())
