import json

from requests import Response

from orkg.out import OrkgResponse


def mock_pageable_func(*args, params=None):
    base_response = mock_pageable_response(**params)
    return OrkgResponse(response=base_response, status_code=None, content=None, url='test_url', paged=True)


def mock_unpageable_func(*args, params=None):
    base_response = mock_unpageable_response(**params)
    return OrkgResponse(response=base_response, status_code=None, content=None, url='test_url', paged=True)


def mock_unpageable_func_different_signature(id):
    raise TypeError


def mock_pageable_response(status_code=200, content_size=2, total_pages=10, page=0):
    _content = {
        'content': [
            {
                'id': '0'
            }
        ] * content_size,
        'pageable': {
        },
        "totalPages": total_pages,
    }

    response = Response()
    response.__setattr__('status_code', status_code)
    response.__setattr__('_content', json.dumps(_content).encode('utf-8'))

    return response


def mock_unpageable_response(status_code=200):
    _content = {
        'content': [
             {
                'id': '0'
             }
        ],
    }

    response = Response()
    response.__setattr__('status_code', status_code)
    response.__setattr__('_content', json.dumps(_content).encode('utf-8'))

    return response


