from flask import jsonify

HTTP_OK = {'message': "success", 'code': 200}
HTTP_CREATED = {'message': "success", 'code': 201}
HTTP_BAD_REQUEST = {'message': "Invalid request body", 'code': 400}
HTTP_UNAUTHORIZED = {'message': "Unauthorized", 'code': 401}
HTTP_NOT_FOUND = {'message': "Not found", 'code': 404}
HTTP_INTERNAL_ERROR = {'message': "Internal server error", 'code': 500}

def success_response_with_data(respone=HTTP_OK, data = None):
    return jsonify({
        "status": "success",
        "message": respone['message'],
        "data": data
    }), respone['code']

def success_response(respone=HTTP_OK):
    return jsonify({
        "status": "success",
        "message": respone['message'],
    }), respone['code']

def error_response(respone=HTTP_OK):
    return jsonify({
        "status": "error",
        "error": {
            "code": respone['code'],
            "message": respone['message']
        }
    }), respone['code']