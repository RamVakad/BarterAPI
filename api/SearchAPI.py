from flask import Blueprint, request, send_file, Response
from services.DBConn import db
import api.AuthorizationAPI
import json

search_api = Blueprint('search_api', __name__)
userDB = db.users
listingDB = db.listings


@search_api.route("", methods=['GET'])
@api.AuthorizationAPI.requires_auth
def searchListings():
    username = request.userNameFromToken
    query = request.args.get('query')  # /search?query=

    try:
        listings = listingDB.find({'item': {'$regex': 'query'}})
        if listings is None:
            return json.dumps({'error': "Searched item not found: "})
        else:
            return json.dumps(listings)
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error regex searching the database.", 'code': 123})
