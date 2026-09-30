# Eventverwaltung

Dies ist ein einfaches Python-Projekt zur Verwaltung von Events, Teilnehmern und Buchungen.
Die Benutzeroberfläche wurde mit Streamlit umgesetzt, die Daten werden in MongoDB gespeichert.

## Projektdateien

- `app.py`: Hauptdatei mit der Streamlit-Oberfläche
- `database.py`: Verbindung zur MongoDB-Datenbank
- `eventService.py`: Funktionen zum Erstellen, Anzeigen, Suchen, Bearbeiten und Löschen von Events
- `bookingService.py`: Funktionen für Buchungen, freie Plätze und Teilnehmer
- `seeData.py`: Beispieldaten für Benutzer, Events und Buchungen

## Voraussetzungen

Damit das Projekt gestartet werden kann, müssen folgende Dinge vorhanden sein:

- Python 3
- MongoDB
- die Python-Pakete `streamlit`, `pymongo` und `bson`

Die MongoDB-Verbindung ist aktuell in `database.py` so eingestellt:

```python
MongoClient("mongodb://127.0.0.1:57084/?directConnection=true")
```

MongoDB muss also unter dieser Adresse und diesem Port erreichbar sein.

## Installation

Im Projektordner können die benötigten Pakete installiert werden:

```bash
pip install streamlit pymongo bson
```

Falls `pip` nicht funktioniert, kann je nach System auch dieser Befehl genutzt werden:

```bash
python3 -m pip install streamlit pymongo bson
```

## Beispieldaten einfügen

Vor dem ersten Start sollten Beispieldaten in die Datenbank eingefügt werden:

```bash
python3 seeData.py
```

Die Datei legt Beispiel-Benutzer, Events und Buchungen an.

Wichtig: Wenn `seeData.py` mehrfach ausgeführt wird, werden die Beispieldaten erneut eingefügt.
Dadurch können doppelte Benutzer oder Events entstehen.

## Anwendung starten

Die Streamlit-App wird mit folgendem Befehl gestartet:

```bash
streamlit run app.py
```

Danach öffnet sich die Anwendung normalerweise automatisch im Browser.
Falls nicht, zeigt Streamlit im Terminal eine lokale URL an, zum Beispiel:

```text
http://localhost:8501
```

## Bedienungsanleitung

Oben in der Anwendung befindet sich eine horizontale Navigation.
Dort kann zwischen den Bereichen wie `Dashboard`, `Events`, `Event erstellen` oder `Meine Buchungen` gewechselt werden.
Der aktuell ausgewählte Bereich ist dunkel hervorgehoben.

Unter der Navigation kann zuerst die Rolle ausgewählt werden:

- `ADMIN`
- `USER`

Danach wird ein Benutzer passend zur Rolle ausgewählt.
Es gibt keine echte Anmeldung mit Passwort, da es sich um ein einfaches Schulprojekt handelt.

## Bedienung als Admin

Admins können Events verwalten und Teilnehmer sehen.

Mögliche Funktionen:

- Events anzeigen
- Events suchen
- Events nach Stadt filtern
- neue Events erstellen
- bestehende Events bearbeiten
- Events löschen
- Teilnehmer eines Events anzeigen
- Benutzer zu einem Event anmelden
- Anmeldungen stornieren
- Teilnehmerzahl und freie Plätze anzeigen

### Neues Event erstellen

Im Bereich `Event erstellen` können Titel, Beschreibung, Datum, Ort, Stadt, Raum und maximale Teilnehmerzahl eingegeben werden.
Mit `Event erstellen` wird das Event gespeichert.

### Event bearbeiten

Im Bereich `Events` kann ein Event aufgeklappt werden.
Danach können die Daten im Formular geändert und mit `Änderungen speichern` gespeichert werden.

Die maximale Teilnehmerzahl kann nicht kleiner als die bereits vorhandene Anzahl an Buchungen sein.

### Event löschen

Ein Event kann im Admin-Bereich gelöscht werden.
Dabei werden auch die Buchungen zu diesem Event entfernt.
Vorher muss eine Bestätigung per Checkbox gesetzt werden.

## Bedienung als User

User können Events ansehen und eigene Buchungen verwalten.
Andere Teilnehmer sind für User nicht sichtbar.

Mögliche Funktionen:

- Events anzeigen
- Events suchen
- Events nach Stadt filtern
- freie Plätze sehen
- Event buchen
- eigene Buchungen anzeigen
- eigene Buchungen stornieren
- bei vollen Events den Hinweis `Ausgebucht` sehen

### Event buchen

Im Bereich `Events` kann ein freies Event über den Button `Event buchen` gebucht werden.
Wenn keine freien Plätze mehr vorhanden sind, wird das Event als `Ausgebucht` angezeigt.

### Eigene Buchungen anzeigen

Im Bereich `Meine Buchungen` sieht der ausgewählte User nur seine eigenen Buchungen.
Dort können Buchungen auch wieder storniert werden.

## Kurze technische Dokumentation

Die Anwendung ist bewusst einfach aufgebaut.
Die Oberfläche befindet sich in `app.py`.
Die Datenbanklogik bleibt in den Service-Dateien:

- Event-Funktionen werden über `eventService.py` aufgerufen.
- Buchungs- und Teilnehmerfunktionen werden über `bookingService.py` aufgerufen.
- Die MongoDB-Verbindung wird zentral in `database.py` erstellt.

Dadurch ist die GUI von der Datenbanklogik getrennt.
`app.py` ruft nur die vorhandenen Funktionen auf und führt keine direkten MongoDB-Abfragen aus.

## Datenmodell

### Event

Ein Event enthält unter anderem:

- Titel
- Beschreibung
- Datum
- Ort mit Name, Stadt und Raum
- maximale Teilnehmerzahl

### Benutzer

Ein Benutzer enthält unter anderem:

- Benutzername
- Name
- E-Mail-Adresse
- Rolle (`admin` oder `user`)

### Buchung

Eine Buchung verbindet einen Benutzer mit einem Event.
Zusätzlich wird ein Buchungsdatum gespeichert.

## Hinweise

- Die Anwendung ist für lokale Nutzung und Lernzwecke gedacht.
- Es gibt keine Passwort-Anmeldung.
- Die Daten werden in MongoDB gespeichert.
- Wenn MongoDB nicht läuft oder der Port nicht passt, kann die App keine Daten laden.
