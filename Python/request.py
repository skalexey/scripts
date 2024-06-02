import os
import sys

import requests


def send_request( url, type, headers = None, data=None ):
    req = getattr( requests, type )
    response = req( url, headers=headers, json=data )
    print( "Status Code", response.status_code )
    return response

def post( url, data = None, headers=None ):
    return send_request( url, "post", headers, data )

def get( url, headers=None ):
    return send_request( url, "get", headers )
