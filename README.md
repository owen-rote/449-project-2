# How to run (Nothing to run yet)

**1.** `python -m venv venv` \
**2.** `.\venv\Scripts\activate` \
**3.** `pip install -r req.txt` \
**4.** `uvicorn main:app --reload`

http://localhost:8000/docs#/


# Dataflow:

CREATE/UPDATE/DELETE operations create identical entries, one on MySQL and one on Mongo

READ operations will allow you to choose, read from mongo or mysql

Registering users and logging in will only use mysql.

## Admin Privilages
Full CRUD on all entities \
Add/Remove normal users \

## User Privilages
Mostly read only \
Perhaps updating only some fields such as inventory count \
No deletes


slides?
user/admin stuff. does each user own their own entries?
