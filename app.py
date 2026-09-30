from datetime import date, datetime
from html import escape

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


NAVIGATION = {
    "ADMIN": [
        ("dashboard", "📊 Dashboard"),
        ("events", "📅 Events"),
        ("create", "➕ Event erstellen"),
    ],
    "USER": [
        ("dashboard", "📊 Dashboard"),
        ("events", "📅 Events"),
        ("bookings", "🎟 Meine Buchungen"),
    ],
}


def apply_styles():
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }

            .block-container {
                max-width: 1120px;
                padding-top: 1rem;
            }

            .app-navbar {
                position: sticky;
                top: 0;
                z-index: 999;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                padding: 0.7rem 1rem;
                margin-bottom: 1rem;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                background: #ffffff;
            }

            .app-brand {
                font-weight: 700;
                color: #222222;
                white-space: nowrap;
            }

            .nav-links {
                display: flex;
                gap: 0.4rem;
                flex-wrap: wrap;
                justify-content: flex-end;
            }

            .nav-link {
                display: inline-block;
                padding: 0.45rem 0.75rem;
                border: 1px solid #c9c9c9;
                border-radius: 6px;
                color: #222222 !important;
                text-decoration: none !important;
                background: #f8f8f8;
                font-size: 0.95rem;
            }

            .nav-link.active {
                color: #ffffff !important;
                border-color: #222222;
                background: #222222;
            }

            .page-title {
                margin-top: 0.4rem;
                margin-bottom: 1rem;
            }

            .table-head {
                padding: 0.6rem 0.8rem;
                border: 1px solid #c9c9c9;
                border-radius: 6px;
                background: #f8f8f8;
                font-weight: 700;
            }

            .confirm-box {
                padding: 1rem;
                margin: 1rem 0;
                border: 1px solid #d89b00;
                border-radius: 8px;
                background: #fff8e6;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


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


def rerun_app():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def get_query_value(name, default):
    try:
        if hasattr(st, "query_params"):
            value = st.query_params.get(name, default)
        else:
            value = st.experimental_get_query_params().get(name, [default])

        if isinstance(value, list):
            return value[0] if value else default

        return value
    except Exception:
        return default


def get_current_page(role):
    page = get_query_value("page", "dashboard")
    allowed_pages = [item[0] for item in NAVIGATION[role]]

    if page not in allowed_pages:
        return "dashboard"

    return page


def render_navbar(role, current_page):
    links = []

    for page_key, label in NAVIGATION[role]:
        active_class = " active" if page_key == current_page else ""
        links.append(
            f'<a class="nav-link{active_class}" href="?page={page_key}">{label}</a>'
        )

    st.markdown(
        f"""
        <div class="app-navbar">
            <div class="app-brand">EVO EventOrganizer</div>
            <div class="nav-links">{''.join(links)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def set_feedback(kind, message):
    st.session_state["feedback"] = {
        "kind": kind,
        "message": message,
    }


def show_feedback():
    feedback = st.session_state.pop("feedback", None)

    if feedback is None:
        return

    if feedback["kind"] == "success":
        st.success(feedback["message"])
    elif feedback["kind"] == "error":
        st.error(feedback["message"])
    else:
        st.info(feedback["message"])


def ask_confirmation(action, message, payload):
    st.session_state["pending_confirmation"] = {
        "action": action,
        "message": message,
        "payload": payload,
    }
    rerun_app()


def show_pending_confirmation():
    pending = st.session_state.get("pending_confirmation")

    if pending is None:
        return

    # Zentrale Rückfrage für alle Aktionen, die Daten verändern.
    st.markdown(
        f"""
        <div class="confirm-box">
            <strong>Bestätigung erforderlich</strong><br>
            {escape(pending["message"])}
        </div>
        """,
        unsafe_allow_html=True,
    )

    confirm_column, cancel_column, _ = st.columns([1, 1, 4])

    if confirm_column.button("✓ Bestätigen", key="confirm_action"):
        execute_confirmed_action(pending)
        st.session_state.pop("pending_confirmation", None)
        rerun_app()

    if cancel_column.button("✕ Abbrechen", key="cancel_action"):
        st.session_state.pop("pending_confirmation", None)
        set_feedback("info", "Aktion wurde abgebrochen.")
        rerun_app()


def execute_confirmed_action(pending):
    action = pending["action"]
    payload = pending["payload"]

    try:
        if action == "create_event":
            data = payload["event"]
            createEvent(
                data["title"],
                data["description"],
                data["date"],
                data["location"],
                data["maxParticipants"],
            )
            set_feedback("success", "Event wurde erfolgreich erstellt.")

        elif action == "update_event":
            updateEvent(payload["eventId"], payload["event"])
            set_feedback("success", "Änderungen wurden erfolgreich gespeichert.")

        elif action == "delete_event":
            cancelEventBookings(payload["eventId"])
            deleted_count = deleteEvent(payload["eventId"])

            if deleted_count > 0:
                set_feedback("success", "Event wurde erfolgreich gelöscht.")
            else:
                set_feedback("error", "Event konnte nicht gelöscht werden.")

        elif action == "book_event":
            success = bookEvent(payload["userId"], payload["eventId"])

            if success:
                set_feedback("success", "Buchung wurde erfolgreich durchgeführt.")
            else:
                set_feedback("error", "Buchung war nicht möglich.")

        elif action == "cancel_booking":
            deleted_count = cancelBooking(payload["userId"], payload["eventId"])

            if deleted_count > 0:
                set_feedback("success", "Buchung wurde erfolgreich storniert.")
            else:
                set_feedback("error", "Buchung wurde nicht gefunden.")

        elif action == "add_participant":
            success = bookEvent(payload["userId"], payload["eventId"])

            if success:
                set_feedback("success", "Teilnehmer wurde erfolgreich hinzugefügt.")
            else:
                set_feedback("error", "Teilnehmer konnte nicht hinzugefügt werden.")

        elif action == "remove_participant":
            deleted_count = cancelBooking(payload["userId"], payload["eventId"])

            if deleted_count > 0:
                set_feedback("success", "Teilnehmer wurde erfolgreich entfernt.")
            else:
                set_feedback("error", "Anmeldung wurde nicht gefunden.")

    except Exception as error:
        set_feedback("error", f"Aktion konnte nicht ausgeführt werden: {error}")


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
        "maxParticipants": int(max_participants),
    }


def get_cities(events):
    cities = []

    for event in events:
        location = event.get("location")
        if isinstance(location, dict) and location.get("city") not in cities:
            cities.append(location.get("city"))

    return sorted(cities)


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


def show_filter_bar(events, key_prefix):
    search_column, city_column = st.columns([2, 1])

    with search_column:
        search_text = st.text_input("🔎 Suche", key=f"{key_prefix}_search")

    with city_column:
        city_filter = st.selectbox(
            "🏙 Stadt filtern",
            ["Alle"] + get_cities(events),
            key=f"{key_prefix}_city",
        )

    return filter_events(events, search_text, city_filter)


def get_event_availability(event):
    current_event_id = event_id(event)
    max_participants = int(event.get("maxParticipants", 0))
    free_places = getFreePlaces(current_event_id)

    if free_places is None:
        return "Keine Daten"

    free_places = max(0, free_places)
    return f"{free_places}/{max_participants} Plätze frei"


def show_event_details(event, show_participant_count=True):
    current_event_id = event_id(event)
    booking_count = getBookingCount(current_event_id)
    free_places = getFreePlaces(current_event_id)

    st.write(f"**Beschreibung:** {event.get('description', '')}")
    st.write(f"**Ort:** {format_location(event.get('location', ''))}")
    st.write(f"**Datum:** {format_event_date(event.get('date', ''))}")
    st.write(f"**Freie Plätze:** {free_places}")

    if show_participant_count:
        st.write(f"**Teilnehmer:** {booking_count} / {event.get('maxParticipants', 0)}")

    if isEventFull(current_event_id):
        st.error("Ausgebucht")


def show_table_header():
    st.markdown(
        """
        <div class="table-head">
            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 1rem;">
                <div>Name</div>
                <div>Datum</div>
                <div>Verfügbarkeit</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_dashboard(events):
    st.markdown('<h1 class="page-title">Willkommen zurück!</h1>', unsafe_allow_html=True)

    total_bookings = sum(getBookingCount(event_id(event)) for event in events)
    today_events = [
        event
        for event in events
        if parse_event_date(event.get("date", date.today())) == date.today()
    ]

    metric_left, metric_middle, metric_right = st.columns(3)
    metric_left.metric("👥 Teilnehmer", total_bookings)
    metric_middle.metric("📅 Events", len(events))
    metric_right.metric("🕒 Heute", len(today_events))

    st.subheader("📌 Nächste Veranstaltungen")

    upcoming_events = sorted(
        events,
        key=lambda event: parse_event_date(event.get("date", date.today())),
    )

    if not upcoming_events:
        st.info("Es sind noch keine Events vorhanden.")
        return

    show_table_header()

    for event in upcoming_events[:5]:
        name_column, date_column, places_column = st.columns([2, 1, 1])
        name_column.write(event.get("title", "Ohne Titel"))
        date_column.write(format_event_date(event.get("date", "")))
        places_column.write(get_event_availability(event))


def show_create_event_form():
    st.markdown('<h1 class="page-title">➕ Event erstellen</h1>', unsafe_allow_html=True)

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

        submitted = st.form_submit_button("➕ Event erstellen")

    if submitted:
        if not title.strip():
            st.warning("Bitte gib einen Titel ein.")
            return

        event_data = build_event_data(
            title.strip(),
            description.strip(),
            event_date,
            location_name.strip(),
            city.strip(),
            room.strip(),
            max_participants,
        )

        ask_confirmation(
            "create_event",
            f'Möchtest du das Event "{event_data["title"]}" wirklich erstellen?',
            {"event": event_data},
        )


def show_admin_event_actions(event):
    current_event_id = event_id(event)
    participants = getEventParticipants(current_event_id)
    users = getUsersByRole("user")
    free_places = getFreePlaces(current_event_id)

    st.subheader("👥 Teilnehmer")

    if participants:
        for participant in participants:
            st.write(
                f"- {participant.get('name', 'Ohne Name')} "
                f"({participant.get('email', 'Keine E-Mail')})"
            )
    else:
        st.info("Noch keine Teilnehmer.")

    add_column, remove_column = st.columns(2)

    with add_column:
        users_not_booked = [
            user
            for user in users
            if not isUserBooked(user_id(user), current_event_id)
        ]

        if free_places is not None and free_places > 0 and users_not_booked:
            user_to_add = st.selectbox(
                "👤 Teilnehmer hinzufügen",
                users_not_booked,
                format_func=user_label,
                key=f"add_user_{current_event_id}",
            )

            if st.button("➕ Teilnehmer hinzufügen", key=f"add_button_{current_event_id}"):
                ask_confirmation(
                    "add_participant",
                    f'Möchtest du {user_to_add.get("name", "diesen Benutzer")} wirklich zu diesem Event hinzufügen?',
                    {
                        "userId": user_id(user_to_add),
                        "eventId": current_event_id,
                    },
                )
        elif free_places is not None and free_places <= 0:
            st.warning("Dieses Event ist ausgebucht.")
        else:
            st.info("Alle Benutzer sind bereits angemeldet.")

    with remove_column:
        if participants:
            participant_to_remove = st.selectbox(
                "✕ Anmeldung stornieren",
                participants,
                format_func=user_label,
                key=f"remove_user_{current_event_id}",
            )

            if st.button("✕ Teilnehmer entfernen", key=f"remove_button_{current_event_id}"):
                ask_confirmation(
                    "remove_participant",
                    f'Möchtest du die Anmeldung von {participant_to_remove.get("name", "diesem Teilnehmer")} wirklich stornieren?',
                    {
                        "userId": user_id(participant_to_remove),
                        "eventId": current_event_id,
                    },
                )

    st.subheader("✏ Event bearbeiten")

    location = event.get("location", {})
    if not isinstance(location, dict):
        location = {}

    with st.form(f"edit_event_form_{current_event_id}"):
        title = st.text_input("Titel", value=event.get("title", ""))
        description = st.text_area(
            "Beschreibung",
            value=event.get("description", ""),
        )
        event_date = st.date_input(
            "Datum",
            value=parse_event_date(event.get("date", date.today())),
        )
        location_name = st.text_input("Ort / Gebäude", value=location.get("name", ""))
        city = st.text_input("Stadt", value=location.get("city", ""))
        room = st.text_input("Raum", value=location.get("room", ""))
        booking_count = getBookingCount(current_event_id)
        max_participants = st.number_input(
            "Maximale Teilnehmerzahl",
            min_value=max(1, booking_count),
            step=1,
            value=max(int(event.get("maxParticipants", 1)), booking_count),
        )

        saved = st.form_submit_button("✏ Änderungen speichern")

    if saved:
        if not title.strip():
            st.warning("Bitte gib einen Titel ein.")
            return

        new_data = build_event_data(
            title.strip(),
            description.strip(),
            event_date,
            location_name.strip(),
            city.strip(),
            room.strip(),
            max_participants,
        )

        ask_confirmation(
            "update_event",
            f'Möchtest du die Änderungen am Event "{new_data["title"]}" wirklich speichern?',
            {
                "eventId": current_event_id,
                "event": new_data,
            },
        )

    st.subheader("🗑 Event löschen")
    st.warning("Beim Löschen werden auch die Buchungen dieses Events entfernt.")

    if st.button("🗑 Event löschen", key=f"delete_{current_event_id}"):
        ask_confirmation(
            "delete_event",
            f'Möchtest du das Event "{event.get("title", "Ohne Titel")}" wirklich löschen?',
            {"eventId": current_event_id},
        )


def show_admin_events(events):
    st.markdown('<h1 class="page-title">📅 Events</h1>', unsafe_allow_html=True)
    filtered_events = show_filter_bar(events, "admin_events")

    if not filtered_events:
        st.info("Keine Events gefunden.")
        return

    show_table_header()

    for event in filtered_events:
        title = event.get("title", "Ohne Titel")
        event_date = format_event_date(event.get("date", ""))
        availability = get_event_availability(event)

        with st.expander(f"📅 {title} | {event_date} | {availability}"):
            show_event_details(event)

            action_column_one, action_column_two, action_column_three = st.columns(3)

            with action_column_one:
                st.caption("👥 Teilnehmer verwalten")
            with action_column_two:
                st.caption("✏ Bearbeiten")
            with action_column_three:
                st.caption("🗑 Löschen")

            show_admin_event_actions(event)


def show_user_events(events, current_user):
    st.markdown('<h1 class="page-title">📅 Events</h1>', unsafe_allow_html=True)
    filtered_events = show_filter_bar(events, "user_events")

    if not filtered_events:
        st.info("Keine Events gefunden.")
        return

    show_table_header()

    for event in filtered_events:
        current_event_id = event_id(event)
        title = event.get("title", "Ohne Titel")
        event_date = format_event_date(event.get("date", ""))
        availability = get_event_availability(event)

        with st.expander(f"📅 {title} | {event_date} | {availability}"):
            show_event_details(event, show_participant_count=False)

            if isUserBooked(user_id(current_user), current_event_id):
                st.success("Du hast dieses Event gebucht.")

                if st.button("✕ Buchung stornieren", key=f"cancel_{current_event_id}"):
                    ask_confirmation(
                        "cancel_booking",
                        "Möchtest du diese Buchung wirklich stornieren?",
                        {
                            "userId": user_id(current_user),
                            "eventId": current_event_id,
                        },
                    )
            elif isEventFull(current_event_id):
                st.button("✕ Ausgebucht", disabled=True, key=f"full_{current_event_id}")
            else:
                if st.button("🎟 Event buchen", key=f"book_{current_event_id}"):
                    ask_confirmation(
                        "book_event",
                        f'Möchtest du das Event "{title}" wirklich buchen?',
                        {
                            "userId": user_id(current_user),
                            "eventId": current_event_id,
                        },
                    )


def show_user_bookings(current_user):
    st.markdown(
        '<h1 class="page-title">🎟 Meine Buchungen</h1>',
        unsafe_allow_html=True,
    )
    bookings = getUserBookings(user_id(current_user))

    if not bookings:
        st.info("Du hast aktuell keine Buchungen.")
        return

    show_table_header()

    for booking in bookings:
        event = getEvent(str(booking["eventId"]))

        if event is None:
            continue

        current_event_id = event_id(event)
        title = event.get("title", "Ohne Titel")
        event_date = format_event_date(event.get("date", ""))
        availability = get_event_availability(event)

        with st.expander(f"🎟 {title} | {event_date} | {availability}"):
            show_event_details(event, show_participant_count=False)

            if st.button("✕ Buchung stornieren", key=f"my_cancel_{current_event_id}"):
                ask_confirmation(
                    "cancel_booking",
                    "Möchtest du diese Buchung wirklich stornieren?",
                    {
                        "userId": user_id(current_user),
                        "eventId": current_event_id,
                    },
                )


def show_top_controls(role):
    all_users = getUsers()
    admin_users = [user for user in all_users if user.get("role") == "admin"]
    normal_users = [user for user in all_users if user.get("role") == "user"]

    role_column, user_column = st.columns([1, 2])

    with role_column:
        selected_role = st.selectbox(
            "⚙ Rolle",
            ["ADMIN", "USER"],
            index=0 if role == "ADMIN" else 1,
            key="role_select",
        )

    if selected_role != role:
        rerun_app()

    if selected_role == "ADMIN":
        selected_user_list = admin_users or all_users
    else:
        selected_user_list = normal_users or all_users

    current_user = None

    with user_column:
        if selected_user_list:
            current_user = st.selectbox(
                "👤 Benutzer",
                selected_user_list,
                format_func=user_label,
                key=f"user_select_{selected_role}",
            )
        else:
            st.warning("Es wurden noch keine Benutzer gefunden.")

    return selected_role, current_user


def main():
    apply_styles()

    role = st.session_state.get("role_select", "ADMIN")
    current_page = get_current_page(role)

    render_navbar(role, current_page)
    role, current_user = show_top_controls(role)
    current_page = get_current_page(role)

    show_feedback()
    show_pending_confirmation()

    if current_user is None:
        st.info("Bitte lege zuerst Benutzer in der Datenbank an.")
        return

    events = getEvents()

    if current_page == "dashboard":
        show_dashboard(events)
    elif current_page == "events" and role == "ADMIN":
        show_admin_events(events)
    elif current_page == "events":
        show_user_events(events, current_user)
    elif current_page == "create" and role == "ADMIN":
        show_create_event_form()
    elif current_page == "bookings" and role == "USER":
        show_user_bookings(current_user)
    else:
        st.info("Diese Seite ist für die ausgewählte Rolle nicht verfügbar.")


if __name__ == "__main__":
    main()
