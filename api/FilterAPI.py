from flask import Blueprint, request, send_file, Response
from services.DBConn import db
import api.AuthorizationAPI
from bson.json_util import dumps
import json


filter_api = Blueprint('filter_api', __name__)
userDB = db.users
listingDB = db.listings


@filter_api.route("/<currentpage>/<int:offset>", methods=['GET'])
@api.AuthorizationAPI.requires_auth
def filterListings(currentpage, offset):
    condition = request.args.get('condition')  # /filter?condition=
    category = request.args.get('category')  # /filter?condition=
    username = request.userNameFromToken
    user_favorites = userDB.find({'username': username})

    try:
        if(currentpage == "Items" or currentpage == "WishList"):
            if not condition and not category:
                listings = dumps(listingDB.find().skip((offset-1)*10).limit(10))
            elif (condition is not None) and not category :
                listings = dumps(listingDB.find({'condition' : condition}).skip((offset-1)*10).limit(10))
            elif (category is not None) and not condition :
                listings = dumps(listingDB.find({'category':category }).skip((offset-1)*10).limit(10))
            elif(condition is not None) and (category is not None):
                listings = dumps(listingDB.find({'condition' : condition, 'category':category }).skip((offset-1)*10).limit(10))
        
        elif(currentpage == "List"):
            if not condition and not category:
                listings = dumps(listingDB.find({'username': username}).skip((offset-1)*10).limit(10))
            elif (condition is not None) and not category :
                listings = dumps(listingDB.find({'username': username, 'condition' : condition}).skip((offset-1)*10).limit(10))
            elif (category is not None) and not condition :
                listings = dumps(listingDB.find({'username': username, 'category':category }).skip((offset-1)*10).limit(10))
            elif(condition is not None) and (category is not None):
                listings = dumps(listingDB.find({'username': username, 'condition' : condition, 'category':category }).skip((offset-1)*10).limit(10))

        # elif(currentpage == "WishList"):
        #     for document in user_favorites:
        #         return json.dumps(document['favorites'])




        if listings is None:
            return json.dumps({'error': "Filterd item not found: "})
        else:
            return listings
    except Exception as e:
        print(e)
        return json.dumps({'error': "Server error filtering the database.", 'code': 123})
