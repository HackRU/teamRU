# Forum API (all uuids are universal)
# 	-> need to get all forum posts by a given user
# 		-> payload is just their email in the query string e.g. ‘${api-route}/${email}’
# 		-> return {poster : string, title : string, uuid : string}[]
# 
# 	-> need to POST a forum post
# 		-> payload {poster : string, title : string, content : string} 
#     and will be sent in the body of the request. The token 
#     will be in the header
# 		-> return the uuid generated for that post
# 
# 	-> need to POST a comment
# 		-> payload {poster : string, content : string, parent_uuid : string}
# 		    and will be sent in the request body. The token will be in the header
# 		-> return {poster : string, content : string, uuid : string}
# 
#   -> need to get the forum post itself
# 		-> payload is the post uuid e.g. ‘${api-route}/${uuid}’
# 		-> return {poster : string, title : string, content : string
# 	-> need to get all comments of a post
# 		-> payload is the post uuid e.g. ‘${api-route}/${uuid}’
# 		-> return {poster : string, content : string, uuid : string, 
#     subcomments : comment[]}[] //an array of comments where 
#     each comment itself has a field ‘subcomments’ that is an array 
#     of comments that have that former comment as its parent

from src.flaskapp.db import coll
from pymongo import ObjectId

# need to get all forum posts posted (maybe only for current year)
#   return {poster : string, title : string, uuid : string}[]
def get_all_posts(limit=100):
    posts = list(coll("posts").find({}).limit(limit))
    return {"posts": posts}, 200


def get_user_posts(poster, limit=100):
    posts = list(coll("posts").find({"poster": poster}).limit(limit))
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

def get_all_sub_comments(parent_id):
    comment = coll("comments").find_one({"_id": parent_id})
    if not comment:
        return {"message": "comment not found"}, 404

    subcomments = []
    subcomments_ids = comment["subcomment"]
    for subcomments_id in subcomments_ids:
        subcomments.append(coll("subcomments").find_one({"_id": subcomments_id}))

    return {"subcomments": subcomments}, 200

# 	need to POST a forum post
# 	    payload {poster : string, title : string, content : string} 
#       and will be sent in the body of the request. The token 
#   will be in the header
# 		-> return the uuid generated for that post
def post_post(**kwargs):
    id = ObjectId()
    coll("posts").insert_one(
        {
            "_id": id,
            "poster": kwargs["poster"],
            "title": kwargs["title"],
            "content": kwargs["content"]
            "comment": []
        }
    )
    return {"post_id": id}, 200

def post_comment(**kwargs):
    id = ObjectId()
    parent = coll("posts").find_one({"_id": email})
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

def post_sub_comment(**kwargs):
    id = ObjectId()

    parent = coll("comment").find_one({"_id": email})
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