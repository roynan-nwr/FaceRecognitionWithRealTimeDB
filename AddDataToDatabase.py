import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# project/faceattendencerealtime-a551e/settings/serviceaccounts/adminsdk
# creating a new private key from firebase

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    # for realtime database which is in JSON format
    'databaseURL':"https://faceattendencerealtime-a551e-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students') # reference path of database

data = {
    "772348":
        {
            # "key": "value",
            "name": "Prashesh Prasad Karmacharya",
            "major": "BCA",
            "starting_year": 2020,
            "total_attendance": 17,
            "standing": "10",
            "year": 4,
            "last_attendance_time": "2024-9-21 00:54:34"
        },
    "852741":
        {
            # "key": "value",
            "name": "Emly Blunt",
            "major": "BBA",
            "starting_year": 2020,
            "total_attendance": 13,
            "standing": "11",
            "year": 1,
            "last_attendance_time": "2024-9-21 00:54:34"
        },
    "963852":
        {
            # "key": "value",
            "name": "Elon Musk",
            "major": "BCA",
            "starting_year": 2020,
            "total_attendance": 17,
            "standing": "4",
            "year": 2,
            "last_attendance_time": "2024-9-21 00:54:34"
        }

}

for key,value in data.items():
    # if you have to send specific data in a specific directory then you have to use child
    ref.child(key).set(value)