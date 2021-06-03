from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, DESCENDING
from werkzeug.security import generate_password_hash

from user import User

client = MongoClient("mongodb+srv://test:test@chatapp.yv6vv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

chat_db = client.get_database("ChatDB")
users_collection = chat_db.get_collection("users")
rooms_collection = chat_db.get_collection("rooms")
room_members_collection = chat_db.get_collection("room_members")
messages_collection = chat_db.get_collection("messages")
event_collection = chat_db.get_collection("event")
gevent_collection = chat_db.get_collection("gevent")
video_collection = chat_db.get_collection("video")
nevent_collection = chat_db.get_collection("nevent")
napproval_collection = chat_db.get_collection("napproval")

def get_user(username):
    user_data = users_collection.find_one({'_id': username})
    return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None


def save_room(room_name, created_by):
    room_id = rooms_collection.insert_one(
        {'name': room_name, 'created_by': created_by, 'created_at': datetime.now()}).inserted_id
    add_room_member(room_id, room_name, created_by, created_by, is_room_admin=True)
    return room_id


def save_user(username, email, password):
    password_hash = generate_password_hash(password)
    users_collection.insert_one({'_id': username, 'email': email, 'password': password_hash})


def update_user(username, email, password):
    password_hash = generate_password_hash(password)
    myquery = { "_id": username }
    newvalues = { "$set": { "password": password_hash } }
    users_collection.update_one(myquery, newvalues)


def update_room(room_id, room_name):
    rooms_collection.update_one({'_id': ObjectId(room_id)}, {'$set': {'name': room_name}})
    room_members_collection.update_many({'_id.room_id': ObjectId(room_id)}, {'$set': {'room_name': room_name}})


def get_room(room_id):
    return rooms_collection.find_one({'_id': ObjectId(room_id)})


def get_video():
    return list(video_collection.find({'added_by': "server"}))


def get_rooms_for_user(username):
    return list(room_members_collection.find({'_id.username': username}))


def add_event(date, timestart, event, added_by, members):
    event_collection.insert_one({'date': date, 'timestart':timestart, 'event':event, 'added_by':added_by, 'members': members})


def add_nevent(date, timestart, event, added_by, members):
    nevent_collection.insert_one({'date': date, 'timestart':timestart, 'event':event, 'added_by':added_by, 'members': members})


def delete_event(date, timestart, timeend, event, added_by, members):
    event_collection.delete_one({'date': date, 'timestart':timestart,  'event':event, 'added_by':added_by, 'members': members})


def get_events_for_user(username):
    x = list(event_collection.find({'members': username}))
    y = list(event_collection.find({'added_by': username}))
    z = x+y
    return z


def get_events_for_user_date(username, date):
    return list(event_collection.find({'members': username, 'date':date}))


def get_nevents_for_user(username):
    return list(nevent_collection.find({'members': username}))


def get_neventsid():
    ne = list(nevent_collection.find())
    ids = []
    for e in ne:
        idd = e.get('_id')
        idd = str(idd)
        iddd = ""
        iddd += idd
        ids.append(iddd)
    return ids

def add_napproval_for_user(info, username):
    napproval_collection.insert_one({'info': info, 'username' : username})


def get_napproval_for_user(username):
    return list(napproval_collection.find({'username': username}))


def get_nevents_by_id(id):
    objInstance = ObjectId(id)
    return list(nevent_collection.find({'_id': objInstance}))


def delete_nevents_by_id(id):
    objInstance = ObjectId(id)
    nevent_collection.delete_one({'_id': objInstance})


def add_gevent(date, timestart, timeend, event, link):
    gevent_collection.insert_one({'date': date, 'timestart':timestart, 'timeend':timeend, 'event':event, 'added_by':'SERVER', 'link':link})


def delete_gevent(date, timestart, timeend, event):
    gevent_collection.delete_one({'date': date, 'timestart':timestart, 'timeend':timeend, 'event':event, 'added_by':'SERVER'})


def get_gevents():
    return list(gevent_collection.find({'added_by': 'SERVER'}))


def add_room_member(room_id, room_name, username, added_by, is_room_admin=False):
    room_members_collection.insert_one(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by,
         'added_at': datetime.now(), 'is_room_admin': is_room_admin})


def add_room_members(room_id, room_name, usernames, added_by):
    room_members_collection.insert_many(
        [{'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by,
          'added_at': datetime.now(), 'is_room_admin': False} for username in usernames])


def remove_room_members(room_id, usernames):
    room_members_collection.delete_many(
        {'_id': {'$in': [{'room_id': ObjectId(room_id), 'username': username} for username in usernames]}})


def get_room_members(room_id):
    return list(room_members_collection.find({'_id.room_id': ObjectId(room_id)}))


def get_rooms_for_user(username):
    return list(room_members_collection.find({'_id.username': username}))


def is_room_member(room_id, username):
    return room_members_collection.count_documents({'_id': {'room_id': ObjectId(room_id), 'username': username}})


def is_room_admin(room_id, username):
    return room_members_collection.count_documents(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'is_room_admin': True})


def save_message(room_id, text, sender):
    messages_collection.insert_one({'room_id': room_id, 'text': text, 'sender': sender, 'created_at': datetime.now()})


MESSAGE_FETCH_LIMIT = 3


def get_messages(room_id, page=0):
    offset = page * MESSAGE_FETCH_LIMIT
    messages = list(
        messages_collection.find({'room_id': room_id}).sort('_id', DESCENDING).skip(offset))
    for message in messages:
        message['created_at'] = message['created_at'].strftime("%d %b, %H:%M")
    return messages[::-1]
