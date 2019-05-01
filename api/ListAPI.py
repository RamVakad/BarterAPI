from flask import Blueprint, request, send_file, Response
from services.DBConn import db
import api.AuthorizationAPI
import json
from bson import Binary
from bson.json_util import dumps
from bson.objectid import ObjectId
import time
import datetime
import boto3
from boto3.s3.transfer import S3Transfer


list_api = Blueprint('list_api', __name__)
userDB = db.users
listingDB = db.listings


@list_api.route("/<int:offset>", methods=['GET'])
@api.AuthorizationAPI.requires_auth
def allListing(offset):
    try:

        # paginate, 10 listings per call
        listings = dumps(listingDB.find().skip((offset-1)*10).limit(10))
        if listings is None:
            return json.dumps({'error': "No listings found.", 'code': 1})
        else:
            return listings
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error grabbing all listings.", 'code': 2})


@list_api.route("/user/<int:offset>", methods=['GET'])
@api.AuthorizationAPI.requires_auth
def userListing(offset):
    username = request.userNameFromToken

    try:
        listings = dumps(listingDB.find({'username': username}).skip((offset-1)*10).limit(10))
        if listings is None:
            return json.dumps({'error': "No listings found for current user: " + username, 'code': 3})
        else:
            return listings
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error grabbing all listings under current user.", 'code': 4})


@list_api.route("/add", methods=['POST'])
@api.AuthorizationAPI.requires_auth
def addListing():
    username = request.userNameFromToken
    item = request.args.get('item')
    category = request.args.get('category')
    condition = request.args.get('condition')
    description = request.args.get('description')
    timeNow = str(round(time.time() * 1000))
    dateAdded = datetime.datetime.now()
    file = request.files['picture']

    if not file:
        return json.dumps({'error': "No file uploaded with identifier 'pic'", 'code': 20})

    if not file.content_type.startswith("image/"):
        return json.dumps({'error': "File is not an image.", 'code': 842})

    try:
        record = listingDB.find_one({'item': item, 'description': description})
        if record:
            return json.dumps({'error': "You are trying to add a duplicate listing.", 'code': 6})
        else:
            s3client = boto3.client('s3')

            key = username + "/" + timeNow + "/" + file.filename
            s3client.upload_fileobj(file, 'barterplace', key,
                                    ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type})

            listing = {'username': username, 'item': item, 'category': category, 'condition': condition,
                       'description': description, 'timeAdded': timeNow, 'dateAdded': dateAdded,
                       'picture': key}

            listingDB.insert_one(listing)

        return json.dumps({'success': True})
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error while checking if listing exists.", 'code': 7})


@list_api.route("/remove/<object_id>")
@api.AuthorizationAPI.requires_auth
def removeListing(object_id):

    try:
        record = listingDB.find_one({'_id': ObjectId(object_id)})
        if record is None:
            return json.dumps({'error': "The listing you want to delete does not exist.", 'code': 8})
        else:
            # delete listing with specific object id
            listingDB.delete_one({'_id': ObjectId(object_id)})
            return json.dumps({'success': True})
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error while checking if listing exists.", 'code': 9})


@list_api.route("/update/<object_id>", methods=['POST'])
@api.AuthorizationAPI.requires_auth
def updateListing(object_id):
    condition = request.args.get('condition')
    description = request.args.get('description')

    try:
        record = listingDB.find_one({'_id': ObjectId(object_id)})
        if record is None:
            return json.dumps({'error': "The listing you want to update does not exist.", 'code': 10})
        else:
            # update condition, and description
            listingDB.update_one(
                {'_id': ObjectId(object_id)},
                {
                    "$set": {
                        "condition": condition,
                        "description": description
                    }
                }
            )

            return json.dumps({'success': True})
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error while checking if listing exists.", 'code': 11})


