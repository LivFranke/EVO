from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:63592/?directConnection=true")
db = client["eventverwaltung"]

events_collection = db['events']
users_collection = db['users']
bookings_collection = db['bookings']