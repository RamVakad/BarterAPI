from flask import Blueprint, request, send_file, Response
from services.DBConn import db
import api.AuthorizationAPI
import json
from bson import Binary
from bson.json_util import dumps
from bson.objectid import ObjectId
import time
import datetime

favorite_api = Blueprint('favorite_api', __name__)
userDB = db.users
listingDB = db.listings


@favorite_api.route("", methods=['GET'])
@api.AuthorizationAPI.requires_auth
def getFavorite():      # returns list of object_ids under user
    username = request.userNameFromToken

    try:
        user_favorites = userDB.find({'username': username})

        if user_favorites is None:
            return json.dumps({'error': username + " does not exist in database", 'code': 1})
        else:

            for document in user_favorites:
                return json.dumps(document['favorites'])

    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error grabbing all favorites under current user.", 'code': 2})


@favorite_api.route("/set/<object_id>", methods=['POST'])
@api.AuthorizationAPI.requires_auth
def setFavorite(object_id):
    username = request.userNameFromToken

    try:
        user = userDB.find({'username': username})

        if user is None:
            return json.dumps({'error': username + " does not exist in database", 'code': 3})
        else:
            userDB.update_one(    # update the user document field with favorite list to store user favorites
                {'username': username},
                {
                    "$addToSet": {
                        "favorites": object_id

                    }
                }
            )

            return json.dumps({'success': True})

    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error saving current user's favorites.", 'code': 4})


@favorite_api.route("/delete/<object_id>")
@api.AuthorizationAPI.requires_auth
def unFavorite(object_id):
    username = request.userNameFromToken

    try:
        user = userDB.find({'username': username})

        if user is None:
            return json.dumps({'error': username + " does not exist in database", 'code': 5})
        else:
            userDB.update_one(
                {'username': username},
                {
                    "$pull": {
                        "favorites": object_id

                    }
                }
            )

            return json.dumps({'success': True})

    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error deleting current user's favorites.", 'code': 6})
