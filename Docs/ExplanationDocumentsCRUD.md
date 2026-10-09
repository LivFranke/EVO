# MongoDB und CRUD – Eventverwaltung

## 1. Aufbau eines MongoDB-Dokuments

Die Daten liegen in diesem Projekt in 'seeData.py'.

Beispiel zum Aufbau eines Aufbau eines MongoDB Dokuments unserer DB:
```python
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
}
```

Dieses Dokument stellt ein Event dar. Es speichert den Titel, die Beschreibung, das Datum, den Veranstaltungsort und die maximale Teilnehmerzahl. Der Ort ist verschachtelt und fasst mehrere Angaben zusammen: zum Beispiel Name, Stadt und Raum.

## 3. Umsetzung von CRUD

Hier sind einmal Beispiele für die Umsetzung von CRUD in unserer Eventverwaltung. Die Datenbanklogik ist vor allem in den Service-Dateien gekapselt, zum Beispiel in 'eventService.py', welche die CRUD-Funktionen enthalten.

### Create

```python
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
```

Die Funktion erstellt ein neues Event-Dokument. Mit `insert_one(event)` wird dieses Dokument in der Collection `events` gespeichert.

### Read

```python
def getEvents():
    return list(eventsCollection.find())
```

Diese Funktion liest alle Event-Dokumente aus der Collection `events`. Das Ergebnis von `find()` wird in eine Liste umgewandelt und an die App zurückgegeben.

### Update

```python
def updateEvent(eventId, newData):
    result = eventsCollection.update_one(
        {"_id": ObjectId(eventId)},
        {"$set": newData}
    )

    return result.modified_count
```

Die Funktion sucht ein Event über seine `_id`. Mit `$set` werden die neuen Daten in das vorhandene Dokument geschrieben.

### Delete

```python
def deleteEvent(eventId):
    result = eventsCollection.delete_one({
        "_id": ObjectId(eventId)
    })

    return result.deleted_count
```

Diese Funktion löscht genau ein Event-Dokument anhand seiner `_id`. Über `deleted_count` wird zurückgegeben, ob ein Dokument gelöscht wurde.
