"""
Prepare JSON Response Data
"""
from flask import jsonify


def prepare_json_response(sms, success=True, data=None, code=200):
    """
    Prepare Json response
    """
    json_object = {'data': data} if data is not None else {}
    return jsonify({
        'message': sms,
        'success': success,
        **json_object
    }), code
