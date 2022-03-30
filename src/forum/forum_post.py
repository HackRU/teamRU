from src.flaskapp.db import coll
from bson.objectid import ObjectId


def post_post(**kwargs):
    id = str(ObjectId())
    coll("posts").insert_one(
        {
            "_id": id,
            "uuid": id,
            "poster": kwargs["poster"],
            "title": kwargs["title"],
            "content": kwargs["content"]
        }
    )
    return {"post_id": id}


def post_comment(**kwargs):
    parent = coll("posts").find_one({"_id": kwargs["parent_oid"]})
    if not parent:
        parent = coll("comments").find_one({"_id": kwargs["parent_oid"]})
        if not parent:
            return {"message": "post not found"}, 404
    
    id = str(ObjectId())
    coll("comments").insert_one(
        {
            "_id": id,
            "uuid": id,
            "parent_oid": kwargs["parent_oid"],
            "poster": kwargs["poster"],
            "content": kwargs["content"]
        }
    )
    return {"comment_id": id}
