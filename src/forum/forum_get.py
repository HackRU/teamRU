from src.flaskapp.db import coll
from bson.objectid import ObjectId
import json

def get_all_posts(limit):
    posts = coll("posts").find({}).limit(limit)
    return {"posts": posts}, 200


def get_all_comments(parent_id):
    post = coll("posts").find_one({"_id": parent_id})
    if not post:
        return {"message": "post not found"}, 404
    comments = []
    comment_ids = post["comment"]
    for comment_id in comment_ids:
        comments.append(coll("comments").find_one({"_id": comment_id}))

    return {"comments": comments}, 200


def get_all_subcomments(parent_id):
    comment = coll("comments").find_one({"_id": parent_id})
    if not comment:
        return {"message": "comment not found"}, 404

    subcomments = []
    subcomments_ids = comment["subcomment"]
    for subcomments_id in subcomments_ids:
        subcomments.append(coll("subcomments").find_one({"_id": subcomments_id}))

    return {"subcomments": subcomments}, 200


def get_user_posts(poster, limit):
    posts = list(coll("posts").find({"poster": poster}).limit(limit))
    return {"posts": posts}, 200
