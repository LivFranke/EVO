from datetime import date, datetime

import streamlit as st

from bookingService import (
    bookEvent,
    cancelBooking,
    cancelEventBookings,
    getBookingCount,
    getEventParticipants,
    getFreePlaces,
    getUserBookings,
    getUsers,
    getUsersByRole,
    isEventFull,
    isUserBooked,
)
from eventService import (
    createEvent,
    deleteEvent,
    getEvent,
    getEvents,
    searchEvents,
    updateEvent,
)


st.set_page_config(page_title="Eventverwaltung", layout="wide")


def event_id(event):
    return str(event["_id"])


def user_id(user):
    return str(user["_id"])


def format_location(location):
    if isinstance(location, dict):
        parts = [
            location.get("name", ""),
            location.get("city", ""),
            location.get("room", ""),
        ]
        return ", ".join([part for part in parts if part])

    return str(location)


def parse_event_date(value):
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return date.today()


def format_event_date(value):
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")

    if isinstance(value, date):
        return value.isoformat()

    return str(value)


def event_label(event):
    return f'{event.get("title", "Ohne Titel")} ({format_event_date(event.get("date", ""))})'


def user_label(user):
    return f'{user.get("name", "Ohne Name")} ({user.get("username", "")})'


def filter_events(events, search_text, city_filter):
    filtered_events = events

    if search_text:
        filtered_events = searchEvents(search_text)

    if city_filter != "Alle":
        filtered_events = [
            event
            for event in filtered_events
            if isinstance(event.get("location"), dict)
            and event["location"].get("city") == city_filter
        ]

    return filtered_events


def get_cities(events):
    cities = []

    for event in events:
        location = event.get("location")
        if isinstance(location, dict) and location.get("city") not in cities:
            cities.append(location.get("city"))

    return sorted(cities)


def show_event_info(event, show_status=True):
    current_event_id = event_id(event)
    booking_count = getBookingCount(current_event_id)
    free_places = getFreePlaces(current_event_id)

    st.subheader(event.get("title", "Ohne Titel"))
    st.write(event.get("description", ""))
    st.write(f"**Datum:** {format_event_date(event.get('date', ''))}")
    st.write(f"**Ort:** {format_location(event.get('location', ''))}")
    st.write(f"**Teilnehmer:** {booking_count} / {event.get('maxParticipants', 0)}")
    st.write(f"**Freie Plätze:** {free_places}")

    if show_status and isEventFull(current_event_id):
        st.error("Ausgebucht")


def build_event_data(title, description, event_date, location_name, city, room, max_participants):
    return {
        "title": title,
        "description": description,
        "date": event_date.isoformat(),
        "location": {
            "name": location_name,
            "city": city,
            "room": room,
        },
        "maxParticipants": max_participants,
    }


def show_create_event_form():
    st.header("Neues Event erstellen")

    with st.form("create_event_form"):
        title = st.text_input("Titel")
        description = st.text_area("Beschreibung")
        event_date = st.date_input("Datum", value=date.today())
        location_name = st.text_input("Ort / Gebäude")
        city = st.text_input("Stadt")
        room = st.text_input("Raum")
        max_participants = st.number_input(
            "Maximale Teilnehmerzahl",
            min_value=1,
            step=1,
            value=10,
        )

        submitted = st.form_submit_button("Event erstellen")

    if submitted:
        if not title.strip():
            st.warning("Bitte gib einen Titel ein.")
            return

        createEvent(
            title.strip(),
            description.strip(),
            event_date.isoformat(),
            {
                "name": location_name.strip(),
                "city": city.strip(),
                "room": room.strip(),
            },
            int(max_participants),
        )
        st.success("Event wurde erstellt.")
        st.rerun()


def show_admin_events(filtered_events):
    st.header("Events verwalten")

    if not filtered_events:
        st.info("Keine Events gefunden.")
        return

    selected_event = st.selectbox(
        "Event auswählen",
        filtered_events,
        format_func=event_label,
    )
    selected_event_id = event_id(selected_event)

    left_column, right_column = st.columns([1, 1])

    with left_column:
        show_event_info(selected_event, show_status=False)

    with right_column:
        st.subheader("Teilnehmer")
        participants = getEventParticipants(selected_event_id)

        if participants:
            for participant in participants:
                st.write(
                    f"- {participant.get('name', 'Ohne Name')} "
                    f"({participant.get('email', 'Keine E-Mail')})"
                )
        else:
            st.info("Noch keine Teilnehmer.")

        users = getUsersByRole("user")
        free_places = getFreePlaces(selected_event_id)
        users_not_booked = [
            user
            for user in users
            if not isUserBooked(user_id(user), selected_event_id)
        ]

        # Admins können Teilnehmer hinzufügen, solange noch Plätze frei sind.
        if free_places is not None and free_places > 0 and users_not_booked:
            user_to_add = st.selectbox(
                "Teilnehmer hinzufügen",
                users_not_booked,
                format_func=user_label,
            )

            if st.button("Teilnehmer anmelden"):
                if bookEvent(user_id(user_to_add), selected_event_id):
                    st.success("Teilnehmer wurde angemeldet.")
                    st.rerun()
                else:
                    st.error("Teilnehmer konnte nicht angemeldet werden.")
        elif free_places is not None and free_places <= 0:
            st.warning("Dieses Event ist ausgebucht.")
        else:
            st.info("Alle Benutzer sind bereits angemeldet.")

        if participants:
            participant_to_cancel = st.selectbox(
                "Anmeldung stornieren",
                participants,
                format_func=user_label,
            )

            if st.button("Anmeldung stornieren"):
                deleted_count = cancelBooking(
                    user_id(participant_to_cancel),
                    selected_event_id,
                )

                if deleted_count > 0:
                    st.success("Anmeldung wurde storniert.")
                    st.rerun()
                else:
                    st.error("Anmeldung wurde nicht gefunden.")

    st.divider()
    st.subheader("Event bearbeiten")

    with st.form(f"edit_event_form_{selected_event_id}"):
        location = selected_event.get("location", {})
        if not isinstance(location, dict):
            location = {}

        title = st.text_input("Titel", value=selected_event.get("title", ""))
        description = st.text_area(
            "Beschreibung",
            value=selected_event.get("description", ""),
        )
        event_date = st.date_input(
            "Datum",
            value=parse_event_date(selected_event.get("date", date.today())),
        )
        location_name = st.text_input("Ort / Gebäude", value=location.get("name", ""))
        city = st.text_input("Stadt", value=location.get("city", ""))
        room = st.text_input("Raum", value=location.get("room", ""))
        max_participants = st.number_input(
            "Maximale Teilnehmerzahl",
            min_value=max(1, getBookingCount(selected_event_id)),
            step=1,
            value=max(
                int(selected_event.get("maxParticipants", 1)),
                getBookingCount(selected_event_id),
            ),
        )

        saved = st.form_submit_button("Änderungen speichern")

    if saved:
        new_data = build_event_data(
            title.strip(),
            description.strip(),
            event_date,
            location_name.strip(),
            city.strip(),
            room.strip(),
            int(max_participants),
        )
        updateEvent(selected_event_id, new_data)
        st.success("Event wurde aktualisiert.")
        st.rerun()

    st.subheader("Event löschen")
    st.warning("Beim Löschen werden auch die Buchungen dieses Events entfernt.")

    confirm_delete = st.checkbox("Ich möchte dieses Event wirklich löschen.")

    if st.button("Event löschen", disabled=not confirm_delete):
        cancelEventBookings(selected_event_id)
        deleteEvent(selected_event_id)
        st.success("Event wurde gelöscht.")
        st.rerun()


def show_user_events(filtered_events, current_user):
    st.header("Events")

    if not filtered_events:
        st.info("Keine Events gefunden.")
        return

    for event in filtered_events:
        current_event_id = event_id(event)

        with st.container():
            left_column, right_column = st.columns([3, 1])

            with left_column:
                show_event_info(event)

            with right_column:
                st.write("")
                st.write("")

                if isUserBooked(user_id(current_user), current_event_id):
                    st.success("Gebucht")
                    if st.button("Buchung stornieren", key=f"cancel_{current_event_id}"):
                        cancelBooking(user_id(current_user), current_event_id)
                        st.success("Buchung wurde storniert.")
                        st.rerun()
                elif isEventFull(current_event_id):
                    st.button("Ausgebucht", disabled=True, key=f"full_{current_event_id}")
                else:
                    if st.button("Event buchen", key=f"book_{current_event_id}"):
                        if bookEvent(user_id(current_user), current_event_id):
                            st.success("Event wurde gebucht.")
                            st.rerun()
                        else:
                            st.error("Buchung war nicht möglich.")


def show_user_bookings(current_user):
    st.header("Meine Buchungen")
    bookings = getUserBookings(user_id(current_user))

    if not bookings:
        st.info("Du hast aktuell keine Buchungen.")
        return

    for booking in bookings:
        event = getEvent(str(booking["eventId"]))

        if event is None:
            continue

        with st.container():
            left_column, right_column = st.columns([3, 1])

            with left_column:
                show_event_info(event, show_status=False)

            with right_column:
                st.write("")
                st.write("")
                if st.button("Stornieren", key=f"my_cancel_{event_id(event)}"):
                    cancelBooking(user_id(current_user), event_id(event))
                    st.success("Buchung wurde storniert.")
                    st.rerun()


def main():
    st.title("Eventverwaltung")

    all_events = getEvents()

    with st.sidebar:
        st.header("Navigation")

        role = st.radio("Rolle", ["ADMIN", "USER"])

        all_users = getUsers()
        admin_users = [user for user in all_users if user.get("role") == "admin"]
        normal_users = [user for user in all_users if user.get("role") == "user"]

        if role == "ADMIN":
            selected_user_list = admin_users or all_users
        else:
            selected_user_list = normal_users or all_users

        current_user = None
        if selected_user_list:
            current_user = st.selectbox(
                "Benutzer",
                selected_user_list,
                format_func=user_label,
            )
        else:
            st.warning("Es wurden noch keine Benutzer gefunden.")

        search_text = st.text_input("Events suchen")
        city_filter = st.selectbox("Stadt filtern", ["Alle"] + get_cities(all_events))

    if current_user is None:
        st.info("Bitte lege zuerst Benutzer in der Datenbank an.")
        return

    filtered_events = filter_events(all_events, search_text, city_filter)

    if role == "ADMIN":
        tab_events, tab_create = st.tabs(["Events", "Neues Event"])

        with tab_events:
            show_admin_events(filtered_events)

        with tab_create:
            show_create_event_form()
    else:
        tab_events, tab_bookings = st.tabs(["Events", "Meine Buchungen"])

        with tab_events:
            show_user_events(filtered_events, current_user)

        with tab_bookings:
            show_user_bookings(current_user)


if __name__ == "__main__":
    main()
