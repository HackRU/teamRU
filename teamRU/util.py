#Used for defining helper functions
import hashlib
from teamRU import sql
from teamRU import config


def authenticate(hcode):
    select = "Select * from user where user.hashCode = %s"
    result = SelectQuery(select,(hcode))
    if result == None:
        return False
    else:
        return True

