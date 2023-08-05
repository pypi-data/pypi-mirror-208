# coding=utf-8
import os
from flask_restful import reqparse
from flask_restful import Resource
from flask_restful import marshal_with
from rest_server.resource.models.helper import resource_fields
from test_framework.state import State


PARSER = reqparse.RequestParser()
PARSER.add_argument('operate_name')
PARSER.add_argument('fw')
PARSER.add_argument('slot')
PARSER.add_argument('device_index')


class OperationResource(Resource):

    def __init__(self):
        pass

    @marshal_with(resource_fields, envelope='resource')
    def post(self):
        result = {"msg": "Operation: is not support upgrade", "state": State.ERROR_NOT_FOUND}
        return result
