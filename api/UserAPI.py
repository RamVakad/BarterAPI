import io
import boto3
import re
import time
from flask import Blueprint, request, send_file, Response
import api.AuthorizationAPI
from services.DBConn import db
from bson import Binary
import json
from boto3.s3.transfer import S3Transfer

user_api = Blueprint('user_api', __name__)
userDB = db.users


@user_api.route("", methods=['PUT'])
def createUser():
    username = request.args.get('username')
    password = request.args.get('password')
    phone = request.args.get('phone')

    if not username:
        return json.dumps({'error': "Username parameter was not provided.", 'code': 1})
    if not password:
        return json.dumps({'error': "Password parameter was not provided.", 'code': 2})
    if not phone:
        return json.dumps({'error': "Phone parameter was not provided.", 'code': 9214})

    username = username.lower()
    if "@" not in username:
        return json.dumps({'error': "Username is not a valid email.", 'code': 3})
    if username[-18:] != "@myhunter.cuny.edu":
        return json.dumps({'error': "Email is not a valid @myhunter.cuny.edu email.", 'code': 4})
    if username[:-18] == "":
        return json.dumps({'error': "@myhunter.cuny.edu email is invalid.", 'code': 5})

    if len(password) < 6 or len(password) > 52:
        return json.dumps({'error': "Password must be at least 6 characters and less than 52 characters long.", 'code': 6})

    try:
        record = userDB.find_one({'username': username}, {'_id': 1})
        if record is None:
            user = {'username': username, 'password': password, 'name': username, 'phone': phone, 'profilePicture': None}
            result = userDB.insert_one(user)
            if result.inserted_id:
                print("created new user: " + username)
                authtoken = api.AuthorizationAPI.encode_auth_token(username).decode("utf-8")
                return json.dumps({'success': True, 'token': authtoken})
            else:
                return json.dumps({'error': "Server error while creating new user.", 'code': 7})
        else:
            return json.dumps({'error': "User already exists.", 'code': 8})
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error while checking if username already exists.", 'code': 9})


@user_api.route("/", methods=['GET'], defaults={'username': None})
@user_api.route("/<username>", methods=['GET'])
@api.AuthorizationAPI.requires_auth
def getUserDetails(username):
    if not username:
        username = request.userNameFromToken
    else:
        username = username.lower()

    try:
        record = userDB.find_one({'username': username}, {'username': 1, 'name': 1, 'phone': 1})
        if record is None:
            return json.dumps({'error': "No user details found for username: " + username})
        else:
            del record['_id']  # don't send document id
            # del record['password'] #don't send the password
            print("returned user details: " + username)
            return json.dumps(record)
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error while checking if username already exists."})


@user_api.route("/update", methods=['POST'])
@api.AuthorizationAPI.requires_auth
def updateUserDetails():
    name = request.args.get('name')
    phone = request.args.get('phone')

    try:
        record = userDB.find_one({'username': request.userNameFromToken})
        if record is None:
            return json.dumps({'error': "The listing you want to update does not exist.", 'code': 10})
        else:
            userDB.update_one(
                {'username': request.userNameFromToken},
                {
                    "$set": {
                        "name": name,
                        "phone": phone
                    }
                }
            )

            return json.dumps({'success': True})
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error while checking if listing exists.", 'code': 11})


@user_api.route("/profilePicture", methods=['GET'])
@api.AuthorizationAPI.requires_auth
def getUserPicture():
    username = request.args.get('username')
    if not username:
        username = request.userNameFromToken
    else:
        username = username.lower()

    try:
        record = userDB.find_one({'username': username}, {'profilePicture': 1})
        if record is None:
            return Response(status=404)
        else:
            if 'profilePicture' in record and record['profilePicture'] is not None:
                return "dkdno63yk5s4u.cloudfront.net/" + record['profilePicture']
                #return send_file(io.BytesIO(record['profilePicture']), attachment_filename='ppic_' + username, mimetype='image/png')
            else:
                return ""
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error while fetching profile picture", 'code': 1})


@user_api.route("/profilePicture", methods=['POST'])
@api.AuthorizationAPI.requires_auth
def updateUserPicture():
    username = request.userNameFromToken
    file = request.files['pic']

    if not file:
        return json.dumps({'error': "No file uploaded with identifier 'pic'", 'code': 1})

    if not file.content_type.startswith("image/"):
        return json.dumps({'error': "File is not an image.", 'code': 842})

    length = 0
    if length > (1000000 * 5):
        return json.dumps({'error': "File too large.", 'code': 3})

    try:
        record = userDB.find_one({'username': username}, {'profilePicture': 1, '_id': 1})
        if record is None:
            return json.dumps({'error': "No user found for username: " + username})
        else:
            s3client = boto3.client('s3')
            timeNow = str(round(time.time() * 1000))

            key = username + "/" + timeNow + "/" + file.filename
            s3client.upload_fileobj(file, 'barterplace', key, ExtraArgs={'ACL':'public-read', 'ContentType': file.content_type})

            result = userDB.update_one(
                {"username": username},
                {
                    "$set": {
                        "profilePicture": key
                    }
                }
            )
            if result.matched_count > 0:
                return json.dumps({'success': True})
            else:
                return json.dumps({'error': 'Updating user profile picture failed for some reason', 'code': 998})
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error while updating profile picture", 'code': 2})
