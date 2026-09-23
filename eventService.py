from bson import ObjectId
from database import eventsCollection

def createEvent(title, description, date, location, maxParticipants):
    event = {
        "title": title,
        "description": description,
        "date": date,
        "location": location,
        "maxParticipants": maxParticipants
    }

    result = eventsCollection.insert_one(event)

    return result.inserted_id

def getEvents():
    return list(eventsCollection.find())

def getEvent(eventId):
    return eventsCollection.find_one({
        "_id": ObjectId(eventId)
    })

def searchEvents(searchText):
    return list(eventsCollection.find({
        "title": {
            "$regex": searchText,
            "$options": "i"
        }
    }))

def updateEvent(eventId, newData):
    result = eventsCollection.update_one(
        {"_id": ObjectId(eventId)},
        {"$set": newData}
    )

    return result.modified_count

def deleteEvent(eventId):
    result = eventsCollection.delete_one({
        "_id": ObjectId(eventId)
    })

    return result.deleted_count