from src.flaskapp.db import coll
from bson.objectid import ObjectId
import json

def get_one_post(uuid):
    post = coll("posts").find_one({"_id": uuid})
    if not post:
        return {"message": "post not found"}, 404
    return post

def get_all_posts(limit):
    posts = coll("posts").find({}).limit(limit)
    return {"posts": posts}


def get_all_comments(post_id):
    comments = coll("comments").find({"parent_oid": post_id})
    if not comments:
        return {"message": "post not found"}, 404
    comments = list(comments)
    for comment in comments:
        # all subcomments
        subcomments = list(coll("comments").find( {"parent_oid": comment["uuid"]} ))
        comment["sub_comments"] = subcomments
    
    return {"comments": comments}



def get_user_posts(poster, limit):
    posts = list(coll("posts").find({"poster": poster}).limit(limit))
    return {"posts": posts}
