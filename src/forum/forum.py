# Forum API (all uuids are universal)
# 	-> need to get all forum posts by a given user
# 		-> payload is just their email in the query string e.g. ‘${api-route}/${email}’
# 		-> return {poster : string, title : string, uuid : string}[]
# 	-> need to get all forum posts posted (maybe only for current year)
# 		-> return {poster : string, title : string, uuid : string}[]
# 	-> need to POST a forum post
# 		-> payload {poster : string, title : string, content : string} 
#     and will be sent in the body of the request. The token 
#     will be in the header
# 		-> return the uuid generated for that post
# 	-> need to get the forum post itself
# 		-> payload is the post uuid e.g. ‘${api-route}/${uuid}’
# 		-> return {poster : string, title : string, content : string
# 	-> need to get all comments of a post
# 		-> payload is the post uuid e.g. ‘${api-route}/${uuid}’
# 		-> return {poster : string, content : string, uuid : string, 
#     subcomments : comment[]}[] //an array of comments where 
#     each comment itself has a field ‘subcomments’ that is an array 
#     of comments that have that former comment as its parent
# 	-> need to POST a comment
# 		-> payload {poster : string, content : string, parent_uuid : string}
# 		    and will be sent in the request body. The token will be in the header
# 		-> return {poster : string, content : string, uuid : string}
from src.flaskapp.db import coll

def get_all_user():
    return none

def get_all_posts(size=25):
    return none

def get_all_comments():
    return none

def post_post(payload):
    return none

def post_comment():
    return none

