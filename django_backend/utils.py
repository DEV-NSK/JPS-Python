from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """Return errors in { message: '...' } format to match Node.js API."""
    response = exception_handler(exc, context)
    if response is not None:
        detail = response.data
        if isinstance(detail, dict) and 'detail' in detail:
            response.data = {'message': str(detail['detail'])}
        elif isinstance(detail, list):
            response.data = {'message': str(detail[0])}
    return response
