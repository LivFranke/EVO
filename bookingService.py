from datetime import datetime
from bson import ObjectId

from database import bookingsCollection, eventsCollection, usersCollection

def getBookingCount(eventId):
    return bookingsCollection.count_documents({
        "eventId": ObjectId(eventId)
    })

def getFreePlaces(eventId):
    event = eventsCollection.find_one({
        "_id": ObjectId(eventId)
    })

    if event is None:
        return None

    bookingCount = getBookingCount(eventId)

    return event["maxParticipants"] - bookingCount

def isEventFull(eventId):
    freePlaces = getFreePlaces(eventId)

    if freePlaces is None:
        return False

    return freePlaces <= 0

def isUserBooked(userId, eventId):
    booking = bookingsCollection.find_one({
        "userId": ObjectId(userId),
        "eventId": ObjectId(eventId)
    })

    return booking is not None

def bookEvent(userId, eventId):

    event = eventsCollection.find_one({
        "_id": ObjectId(eventId)
    })

    # Event existiert nicht
    if event is None:
        return False

    # User ist bereits angemeldet
    if isUserBooked(userId, eventId):
        return False

    # Event ist ausgebucht
    if isEventFull(eventId):
        return False

    booking = {
        "userId": ObjectId(userId),
        "eventId": ObjectId(eventId),
        "bookingDate": datetime.now()
    }

    bookingsCollection.insert_one(booking)

    return True

def cancelBooking(userId, eventId):
    result = bookingsCollection.delete_one({
        "userId": ObjectId(userId),
        "eventId": ObjectId(eventId)
    })

    return result.deleted_count

def getUserBookings(userId):
    return list(bookingsCollection.find({
        "userId": ObjectId(userId)
    }))

def getEventParticipants(eventId):
    bookings = bookingsCollection.find({
        "eventId": ObjectId(eventId)
    })

    participants = []

    for booking in bookings:
        user = usersCollection.find_one({
            "_id": booking["userId"]
        })

        if user is not None:
            participants.append(user)

    return participants