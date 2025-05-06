# 449 Project 2, Group 2
# How to run (Currently Working)

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

## User Privilages
Full CRUD on ONLY entities that THEY create. \
Each entity will also store the user ID of the creator.

# Authors
Caleb Cassin, Owen Rotenberg, Devin Ngo, Ashton Yoshino, Jake Souza
