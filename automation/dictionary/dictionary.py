import json
import os
import sys


def dictionary_init():
    global gcloud_api_key
    this_dir=os.path.dirname( os.path.realpath( __file__ ) )
    sys.path.insert( 1, os.path.expanduser('~') + "/Scripts/Python" );

dictionary_init()

from command_line_utils import *
from request import *


def meaning( word ):
    r = get( "https://api.dictionaryapi.dev/api/v2/entries/en/" + word );
    print(r)
    print( "Meaning result: ", json.dumps( r.json(), indent=2 ) )

call_locals_with_args( locals() )
