import json
import logging
import requests
from requests import Response, request
import cattr

def post(resource, data=None) -> Response:
    url = get_url(resource)
    response = request(
        method="POST",
        url=url,
        json=data,
    )
    return response


def post_file(resource, data=None) -> Response:
    files = {'file': ('files', data, 'application/vnd.ms-excel', {'Expires': '0'})}
    url = get_url(resource)
    response = request(
        method="POST",
        url=url,
        files=files,
    )
    return response


def get(resource, url_param=None, param=None) -> Response:
    url = get_url(resource, url_param, param)
    response = request(
        method="GET",
        url=url,

    )
    return response


def delete(resource, url_param=None, param=None) -> Response:
    url = get_url(resource, url_param, param)
    response = request(
        method="DELETE",
        url=url,

    )
    return response


def put(resource, data=None, url_param=None) -> Response:
    url = get_url(resource, url_param)
    response = request(
        method="PUT",
        url=url,
        json=data,
    )
    return response

def get_url(resource, url_params=None, query=None):
    url = str(resource.path_name)
    if url_params:
        url = '/'.join((url, str(url_params)))

    if query is not None:
        url += '?' + query

    return url


def structure(response: Response, type_response) -> Response:
    """
        Try to structure response
        :param response: response
        :param type_response: type response
        :return: modify response with "data" field
        """
    if type_response:
        try:
            response.data = cattr.structure(response.json(), type_response)
        except Exception as e:
            raise e
    logging.info(f"Response{response}")
    return response


def request(method: str, url: str, **kwargs) -> Response:
    kwargs.setdefault('verify', False)
    """
    Request method
    method: method for the new Request object: GET, OPTIONS, HEAD, POST, PUT, PATCH, or DELETE.
    url – URL for the new Request object.
    **kwargs:
        params – (optional) Dictionary, list of tuples or bytes to send in the query string for the Request. # noqa
        json – (optional) A JSON serializable Python object to send in the body of the Request. # noqa
        headers – (optional) Dictionary of HTTP Headers to send with the Request.
    """
    return requests.request(method, url, **kwargs)


def create_payload(*kwargs):
    return json.loads(json.dumps(*kwargs, default=lambda o: o.__dict__))