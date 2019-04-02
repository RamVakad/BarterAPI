from flask import Blueprint, request, send_file, Response
from services.DBConn import db
import api.AuthorizationAPI
import json
from bson import Binary

list_api = Blueprint('list_api', __name__)
userDB = db.users
listingDB = db.listings


@list_api.route("", methods=['GET'])
@api.AuthorizationAPI.requires_auth
def showListing():
    username = request.userNameFromToken

    try:
        listings = listingDB.find({'username': username})
        if listings is None:
            return json.dumps({'error': "No listings found for current user: " + username})
        else:
            return json.dumps(listings)
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error grabbing all listings under current user."})


@list_api.route("/add", methods=['POST'])
@api.AuthorizationAPI.requires_auth
def addListing():
    username = request.userNameFromToken
    item = request.args.get('item')
    description = request.args.get('description')
    picture = request.files['picture'].read()

    if len(picture) > (1000000 * 5):
        return json.dumps({'error': "File too large.", 'code': 3})

    listing = {'username': username, 'item': item, 'description': description, 'picture': Binary(picture)}

    try:
        record = listingDB.find_one({'username': username, 'item': item})
        if record:
            return json.dumps({'error': "You are trying to add a duplicate listing. Please add a unique listing."})
        else:
            listingDB.insert_one(listing)
            return json.dumps({'success': True})
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error while checking if listing exists."})


@list_api.route("/remove/<item>", methods=['POST'])
@api.AuthorizationAPI.requires_auth
def removeListing(item):
    username = request.userNameFromToken

    try:
        record = listingDB.find_one({'username': username, 'item': item})
        if record is None:
            return json.dumps({'error': "The listing you want to delete does not exist."})
        else:
            # delete listing with username and item match
            listingDB.delete_one({'username': username, 'item': item})
            return json.dumps({'success': True})
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error while checking if listing exists."})





