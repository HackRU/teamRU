#Used for defining helper functions
import hashlib



def authenticate(uid,slack):
    hcode = hashlib.sha256(str(uid)+str(slack))
    select = "Select * from user where user.hashCode = %s"
    result = SelectQuery(select,(hcode))
    if result == None:
        return False
    else:
        return True

