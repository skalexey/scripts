import json
import os
import sys

import requests

gcloud_api_key = None
gcloud_api_p2_key = None
gcloud_use_account = False

def gcloud_init():
	global gcloud_api_key
	global gcloud_api_p2_key
	this_dir=os.path.dirname( os.path.realpath( __file__ ) )
	sys.path.insert( 1, os.path.expanduser('~') + "/Scripts/Python" )
	with open(this_dir + "/tmp/api_key", 'r') as file:
		gcloud_api_key = file.read().rstrip()
	with open(this_dir + "/tmp/p2_api_key", 'r') as file:
		gcloud_api_p2_key = file.read().rstrip()

gcloud_init()

from command_line_utils import *
from request import *


def get_token( setting = "" ):
	return os.popen( "gcloud auth " + setting + " print-access-token" ).read().strip()

def user_auth_headers( setting = "" ):
	return {
		"Authorization": "Bearer " + get_token( setting ),
		"Content-Type": "application/json; charset=utf-8"
	}

def project_user_auth_headers( project_id, setting = "" ):
	return {
		"Authorization": "Bearer " + get_token( setting ),
		"x-goog-user-project": project_id,
		"Content-Type": "application/json; charset=utf-8"
	}

def project_api_key_auth_headers( project_id, key ):
	return {
		"X-goog-api-key": key,
		"x-goog-user-project": project_id,
		"Content-Type": "application/json; charset=utf-8"
	}

def auth( setting = "" ):
	return get( "https://translation.googleapis.com/language/translate/v2", user_auth_headers( setting ) );

def translate( req, api_key = None ):
	key = api_key if api_key else gcloud_api_key if not gcloud_use_account else None
	if key:
		headers = {
			"Content-Type": "application/json; charset=utf-8",
			"X-goog-api-key": key
		}
	else:
		if gcloud_use_account:
			headers = user_auth_headers( "application-default" )
		else:
			headers = None
	print("Request: ", req )
	print("Headers: ", headers )
	return post( "https://translation.googleapis.com/language/translate/v2", req, headers );

def translate_word( word, language = "en" ):
	r = translate( { "q": word, "target": language } )
	print( "Translate result: ", json.dumps( r.json(), indent=2 ) )

def ocr( input_uri, output_uri, api_key = None ):
	# input_uri format: gs://bucket/file
	# output_uri format: gs://bucket/file, but it will be actually a lot of JSON files postfixed with + <some google info>.json
	req = {
		"requests":[
			{
				"inputConfig": {
					"gcsSource": {
					"uri": input_uri
					},
					"mimeType": "application/pdf"
				},
				"features": [
					{
					"type": "DOCUMENT_TEXT_DETECTION"
					}
				],
				"outputConfig": {
					"gcsDestination": {
						"uri": output_uri
					},
					"batchSize": 1
				}
			}
		]
	}
	headers = project_user_auth_headers("self-service-411913")
	print("Headers: ", headers)
	print("Request: ", req)
	return post( "https://vision.googleapis.com/v1/files:asyncBatchAnnotate", req, headers )

def vision_operation( operation_id ):
	headers = project_user_auth_headers("self-service-411913")
	print("Headers: ", headers)
	result = get( "https://vision.googleapis.com/v1/" + operation_id, headers )
	print( "Vision operation result: ", json.dumps( result.json(), indent=2 ) )
	return result

call_locals_with_args( locals() )
