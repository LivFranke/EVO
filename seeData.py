from database import events_collection, users_collection, bookings_collection

users = [
    {
        "username": "admin",
        "name": "Max Mustermann",
        "email": "max@eventverwaltung.de",
        "role": "admin"
    },
    {
        "username": "admin2",
        "name": "Anna Schmidt",
        "email": "anna@eventverwaltung.de",
        "role": "admin"
    },
    {
        "username": "lukas",
        "name": "Lukas Weber",
        "email": "lukas@example.de",
        "role": "user"
    },
    {
        "username": "sophie",
        "name": "Sophie Müller",
        "email": "sophie@example.de",
        "role": "user"
    },
    {
        "username": "jonas",
        "name": "Jonas Becker",
        "email": "jonas@example.de",
        "role": "user"
    },
    {
        "username": "lea",
        "name": "Lea Wagner",
        "email": "lea@example.de",
        "role": "user"
    }
]

events = [
    {
        "title": "Sommerfest",
        "description": "Gemeinsames Sommerfest mit Essen, Musik und Spielen.",
        "date": "2026-10-15",
        "location": {
            "name": "Veranstaltungshalle",
            "city": "Detmold",
            "room": "Saal 1"
        },
        "maxParticipants": 30
    },
    {
        "title": "Workshop Python",
        "description": "Einführung in die Python-Programmierung.",
        "date": "2026-10-20",
        "location": {
            "name": "Schulungsraum A",
            "city": "Lage",
            "room": "Raum 101"
        },
        "maxParticipants": 15
    },
    {
        "title": "Teambuilding",
        "description": "Gemeinsamer Teambuilding-Tag mit verschiedenen Aktivitäten.",
        "date": "2026-10-25",
        "location": {
            "name": "Freizeitpark",
            "city": "Bielefeld",
            "room": "Haupteingang"
        },
        "maxParticipants": 20
    },
    {
        "title": "Weihnachtsfeier",
        "description": "Gemeinsame Weihnachtsfeier mit Essen und Getränken.",
        "date": "2026-12-10",
        "location": {
            "name": "Restaurant Zur Linde",
            "city": "Detmold",
            "room": "Großer Saal"
        },
        "maxParticipants": 50
    },
    {
        "title": "Fußballturnier",
        "description": "Internes Fußballturnier für Mitarbeiter.",
        "date": "2026-11-05",
        "location": {
            "name": "Sportzentrum West",
            "city": "Lage",
            "room": "Sportplatz 2"
        },
        "maxParticipants": 10
    },
    {
        "title": "Projektpräsentation",
        "description": "Präsentation der aktuellen Projekte und Ergebnisse.",
        "date": "2026-11-20",
        "location": {
            "name": "Konferenzzentrum",
            "city": "Detmold",
            "room": "Konferenzraum 3"
        },
        "maxParticipants": 25
    }
]

users_collection.insert_many(users)
events_collection.insert_many(events)

lukas = users_collection.find_one({"username": "lukas"})
sophie = users_collection.find_one({"username": "sophie"})
jonas = users_collection.find_one({"username": "jonas"})
lea = users_collection.find_one({"username": "lea"})

sommerfest = events_collection.find_one({"title": "Sommerfest"})
python_workshop = events_collection.find_one({"title": "Workshop Python"})
teambuilding = events_collection.find_one({"title": "Teambuilding"})
weihnachtsfeier = events_collection.find_one({"title": "Weihnachtsfeier"})
fussball = events_collection.find_one({"title": "Fußballturnier"})

bookings = [
    {
        "userId": lukas["_id"],
        "eventId": sommerfest["_id"],
        "bookingDate": "2026-09-20"
    },
    {
        "userId": sophie["_id"],
        "eventId": sommerfest["_id"],
        "bookingDate": "2026-09-21"
    },
    {
        "userId": jonas["_id"],
        "eventId": sommerfest["_id"],
        "bookingDate": "2026-09-22"
    },
    {
        "userId": lea["_id"],
        "eventId": python_workshop["_id"],
        "bookingDate": "2026-09-20"
    },
    {
        "userId": lukas["_id"],
        "eventId": python_workshop["_id"],
        "bookingDate": "2026-09-21"
    },
    {
        "userId": sophie["_id"],
        "eventId": teambuilding["_id"],
        "bookingDate": "2026-09-22"
    },
    {
        "userId": jonas["_id"],
        "eventId": weihnachtsfeier["_id"],
        "bookingDate": "2026-09-22"
    },
    {
        "userId": lea["_id"],
        "eventId": fussball["_id"],
        "bookingDate": "2026-09-22"
    }
]

bookings_collection.insert_many(bookings)

print("Benutzer wurden eingefügt.")
print("Events wurden eingefügt.")
print("Buchungen wurden eingefügt.")
print("Datenbank wurde erfolgreich erstellt.")