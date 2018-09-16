#Used for defining helper functions
import hashlib
from teamRU2 import sql
from teamRU2 import config.example.py


def authenticate(hcode):
    select = "Select * from user where user.hashCode = %s"
    result = SelectQuery(select,(hcode))
    if result == None:
        return False
    else:
        return True

