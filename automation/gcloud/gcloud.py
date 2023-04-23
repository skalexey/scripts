import requests
import json
import sys
import os

gcloud_api_key = None
gcloud_use_account = False

def gcloud_init():
    global gcloud_api_key
    this_dir=os.path.dirname( os.path.realpath( __file__ ) )
    sys.path.insert( 1, os.path.expanduser('~') + "/Scripts/Python" );
    with open(this_dir + "/tmp/api_key", 'r') as file:
        gcloud_api_key = file.read().rstrip()

gcloud_init()

from request import *
from log_utils import *
from command_line_utils import *

def get_token( setting = "" ):
    return os.popen( "gcloud auth " + setting + " print-access-token" ).read().strip()

def auth_headers( setting = "" ):
    return {
        "Authorization": "Bearer " + get_token( setting ),
        "Content-Type": "application/json; charset=utf-8"
    }

def auth( setting = "" ):
    return get( "https://translation.googleapis.com/language/translate/v2", auth_headers( setting ) );

def translate( req, api_key = None ):
    key = api_key if api_key else gcloud_api_key if not gcloud_use_account else None
    if key:
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-goog-api-key": key
        }
    else:
        if gcloud_use_account:
            headers = auth_headers( "application-default" )
        else:
            headers = None
    print("Request: ", req )
    print("Headers: ", headers )
    return post( "https://translation.googleapis.com/language/translate/v2", req, headers );

def translate_word( word, language = "en" ):
    r = translate( { "q": word, "target": language } )
    print( "Translate result: ", json.dumps( r.json(), indent=2 ) )

call_locals_with_args( locals() )
