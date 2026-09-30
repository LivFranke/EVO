from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:57084/?directConnection=true")
db = client["eventverwaltung"]

eventsCollection = db['events']
usersCollection = db['users']
bookingsCollection = db['bookings']