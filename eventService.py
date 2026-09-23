from bson import ObjectId
from database import events_collection

def create_event(title, description, date, location, maxParticipants):
    event = {
        "title": title,
        "description": description,
        "date": date,
        "location": location,
        "maxParticipants": maxParticipants
    }

    result = events_collection.insert_one(event)

    return result.inserted_id


def get_events():
    return list(events_collection.find())


def get_event(event_id):
    return events_collection.find_one({
        "_id": ObjectId(event_id)
    })


def search_events(search_text):
    return list(events_collection.find({
        "title": {
            "$regex": search_text,
            "$options": "i"
        }
    }))


def update_event(event_id, new_data):
    result = events_collection.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": new_data}
    )

    return result.modified_count


def delete_event(event_id):
    result = events_collection.delete_one({
        "_id": ObjectId(event_id)
    })

    return result.deleted_count