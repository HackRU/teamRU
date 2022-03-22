from src.flaskapp.db import coll
from bson.objectid import ObjectId


def post_post(**kwargs):
    id = ObjectId()
    coll("posts").insert_one(
        {
            "_id": id,
            "poster": kwargs["poster"],
            "title": kwargs["title"],
            "content": kwargs["content"],
            "comment": []
        }
    )
    
    return {"post_id": id}, 200


def post_comment(**kwargs):
    id = ObjectId()
    parent = coll("posts").find_one({"_id": kwargs["parent_uuid"]})
    if not parent:
        return {"message": "post not found"}, 404
    coll("posts").update_one({'_id': kwargs["parent_uuid"]},{'$push': {"comment": id}})
    coll("comments").insert_one(
        {
            "_id": id,
            "poster": kwargs["poster"],
            "content": kwargs["content"],
            "subcomment": []
        }
    )
    return {"comment_id": id}, 200


def post_subcomment(**kwargs):
    id = ObjectId()
    
    parent = coll("comment").find_one({"_id": kwargs["parent_uuid"]})
    if not parent:
        return {"message": "comment not found"}, 404
    
    coll("comment").update_one({'_id': kwargs["parent_uuid"]},{'$push': {"subcomment": id}})
    coll("subcomments").insert_one(
        {
            "_id": id,
            "poster": kwargs["poster"],
            "content": kwargs["content"]
        }
    )
    return {"sub_comment_id": id}, 200