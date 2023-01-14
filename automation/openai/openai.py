import requests
import json
import sys
import os
import re
this_dir=os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, this_dir + '/../tmp')
from openai_config import *

logs_dir = this_dir + '/tmp/logs'

def store_to_file( fname, data ):
    os.makedirs( logs_dir, exist_ok = True)
    with open( logs_dir + '/' + fname, 'w' ) as f:
        f.write( data )

def log_fname( postfix = '' ):
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + postfix + '.log'

def store( data, prefix = '' ):
    store_to_file( prefix + log_fname(), data )

def send_request( cmd, type, data = None ):
    url = "https://api.openai.com/v1/" + cmd
    headers = { "Content-Type": "application/json; charset=utf-8",
                "Authorization": "Bearer " + openai_token
    }
    req = getattr( requests, type )
    response = req( url, headers=headers, json=data )
    print( "Status Code", response.status_code )
    j = response.json()
    store( json.dumps( j, indent=2 ) )
    if 'choices' in j:
        store( j['choices'][0]['text'], 'text_' )
    return j

def post( cmd, data = None ):
    return send_request(cmd, "post", data)

def get( cmd ):
    return send_request(cmd, "get")

def models( full=False ):
    r = get( "models" )
    if full:
        print( "JSON Response ", json.dumps( r, indent=2 ) )
    else:
        for e in r['data']:
            print( e['id'] )

def ask( query ):
    r = json.dumps( post("completions", {
        "model": "text-davinci-003",
        "prompt": query,
        "temperature": 0,
        "max_tokens": 4096 - len( re.findall( r'[^\s:]', query ) ),
    }), indent=2 )
    if 'choices' in r:
        print( r['choices'][0]['text'] )
    else:
        print( r )
    

def ask_file( fpath ):
    with open( fpath, 'r') as f:
        query = f.read()
        ask( query )

def words_test( query ):
    print( len( re.findall( r'[^\s:]+', query ) ) )

if len(sys.argv) > 2:
    locals()[sys.argv[1]](sys.argv[2])
elif len(sys.argv) == 2:
    locals()[sys.argv[1]]()
else:
    print('No arguments provided. Specify a command with needed arguments')
    sys.exit(1)
