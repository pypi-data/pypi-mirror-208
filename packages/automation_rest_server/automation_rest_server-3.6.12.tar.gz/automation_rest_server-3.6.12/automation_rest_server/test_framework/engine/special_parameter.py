
import os
import sys


class Parameters(object):

    def __init__(self):
        pass

    def pop_parm(self, parameters, key):
        if key in parameters.keys():
            parameters.pop(key)
        return parameters
