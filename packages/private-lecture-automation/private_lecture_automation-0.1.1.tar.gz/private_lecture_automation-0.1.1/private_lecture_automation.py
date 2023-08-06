import json
import smtplib
import textwrap
from configparser import ConfigParser
from copy import deepcopy
from datetime import datetime, timedelta
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from icalendar import Calendar, Event


def send_introduction_email(
    recipient_email: str,
    values_to_replace: dict[str, str] | None = None,
) -> None:
    config = _load_config()

    message = MIMEMultipart()
    message["Subject"] = "Különóra információk"
    message["From"] = formataddr(
        (str(Header(f"PythonVilág", "utf-8")), config["email"]["email_address"])
    )
    message["To"] = recipient_email

    with open(
        config["introduction_email"]["email_path"], mode="r", encoding="utf-8"
    ) as message_file:
        message_body = message_file.read()

    if values_to_replace is not None:
        for key, value in values_to_replace.items():
            message_body = message_body.replace(f"[{key}]", value)

    html_part = MIMEText(message_body, "html")
    message.attach(html_part)

    try:
        with open(config["introduction_email"]["logo_path"], mode="rb") as img_file:
            img = MIMEImage(img_file.read())
        img.add_header("Content-ID", "<logo>")
        message.attach(img)
    except KeyError:
        pass

    _send_email(config, message)


def send_calendar_event(student_name: str, **kwargs: str) -> None:
    config = _load_config()

    student_data = _load_student_data(config, student_name)
    if kwargs:
        student_data.update(kwargs)

    ical_part = _create_calendar_event(student_data, config["email"]["email_address"])

    message = MIMEMultipart()
    message[
        "Subject"
    ] = f"Python programozás {student_data['occasion_number']} - {student_data['name']}"
    message["From"] = formataddr(
        (str(Header(f"PythonVilág", "utf-8")), config["email"]["email_address"])
    )
    message["To"] = student_data["email"]
    message.attach(ical_part)

    _send_email(config, message)


def _load_config() -> ConfigParser:
    config = ConfigParser()
    config.read("config.ini")
    return config


def _load_student_data(
    config: ConfigParser, student_name: str, increment_occasion_number: bool = True
) -> dict[str, str]:
    with open(config["calendar_event"]["student_data_path"], "r+", encoding="utf8") as f:
        students = json.load(f)
        student_data = students[student_name]

        if increment_occasion_number:
            students = deepcopy(students)
            incremented_occasion_number = str(int(students[student_name]["occasion_number"]) + 1)
            students[student_name]["occasion_number"] = incremented_occasion_number
            f.seek(0)
            json.dump(students, f, ensure_ascii=False, indent=4)
            f.truncate()

    return student_data


def _create_calendar_event(student_data: dict[str, str], EMAIL_ADDRESS: str) -> MIMEApplication:
    # Event
    event = Event()
    event["organizer"] = f"mailto:{EMAIL_ADDRESS}"

    ##  Event summary
    event.add(
        name="summary",
        value=f"PythonVilág különóra {student_data['occasion_number']} - {student_data['name']}",
    )

    ## Description
    event.add(
        name="description",
        value=textwrap.dedent(
            f"""\
            A korábbi órák tartalmát megtalálod a következő linken:
            {student_data["content_link"]}"""
        ),
    )

    ## Start and end time
    day = int(student_data["day"])
    hour = int(student_data["time"][:2])
    minute = int(student_data["time"][2:])
    duration = int(student_data["duration"])
    today = datetime.now()

    days_ahead = day - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7

    lesson_datetime = today + timedelta(days_ahead)
    lesson_datetime = lesson_datetime.replace(hour=hour, minute=minute, second=0)

    lesson_start = lesson_datetime
    lesson_end = lesson_datetime + timedelta(minutes=duration)

    event.add("dtstart", lesson_start)
    event.add("dtend", lesson_end)

    # Calendar
    calendar = Calendar()

    calendar.add_component(event)
    ical_data = calendar.to_ical()

    ical_part = MIMEApplication(ical_data, "octet-stream", Name="event.ics")
    ical_part["Content-Disposition"] = 'attachment; filename="event.ics"'

    return ical_part


def _send_email(config: ConfigParser, message: MIMEMultipart) -> None:
    with smtplib.SMTP_SSL(config["email"]["host"], int(config["email"]["port"])) as smtp:
        smtp.login(config["email"]["email_address"], config["email"]["email_password"])
        smtp.send_message(message)
