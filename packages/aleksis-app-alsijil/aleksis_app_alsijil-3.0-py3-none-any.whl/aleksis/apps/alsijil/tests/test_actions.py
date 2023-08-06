from datetime import date, time

import pytest

from aleksis.apps.alsijil.actions import (
    delete_personal_note,
    mark_as_excuse_type_generator,
    mark_as_excused,
    mark_as_unexcused,
)
from aleksis.apps.alsijil.models import ExcuseType, PersonalNote
from aleksis.apps.chronos.models import Event, TimePeriod
from aleksis.core.models import Person

pytestmark = pytest.mark.django_db


def _generate_event(day: date):
    period_from = TimePeriod.objects.create(
        weekday=0, period=1, time_start=time(10, 00), time_end=time(11, 00)
    )
    period_to = TimePeriod.objects.create(
        weekday=0, period=2, time_start=time(11, 00), time_end=time(12, 00)
    )

    event = Event.objects.create(
        date_start=day, date_end=day, period_from=period_from, period_to=period_to
    )
    return event


def _prepare_notes():
    """Create some minimal personal notes."""
    person, __ = Person.objects.get_or_create(first_name="Jane", last_name="Doe")

    excuse_type, __ = ExcuseType.objects.get_or_create(short_name="Foo", name="Fooooooooooooo")
    notes = [
        PersonalNote(
            person=person,
            event=_generate_event(date(2021, 10, 1)),
            absent=True,
            remarks="This is baz.",
        ),
        PersonalNote(person=person, event=_generate_event(date(2021, 11, 1)), absent=True),
        PersonalNote(
            person=person, event=_generate_event(date(2022, 10, 1)), absent=True, excused=True
        ),
        PersonalNote(
            person=person,
            event=_generate_event(date(2021, 3, 1)),
            absent=True,
            excused=True,
            excuse_type=excuse_type,
        ),
        PersonalNote(person=person, event=_generate_event(date(2021, 10, 4)), tardiness=10),
        PersonalNote(
            person=person, event=_generate_event(date(2032, 10, 11)), remarks="Good work!"
        ),
        PersonalNote(person=person, event=_generate_event(date(2032, 10, 11))),
    ]
    PersonalNote.objects.bulk_create(notes)
    return notes


def test_mark_as_excused_action():
    notes = _prepare_notes()
    assert PersonalNote.objects.filter(excused=True).count() == 2
    mark_as_excused(None, None, PersonalNote.objects.all())
    assert PersonalNote.objects.filter(excused=True).count() == 4
    assert PersonalNote.objects.filter(excuse_type=None, excused=True).count() == 4


def test_mark_as_unexcused_action():
    notes = _prepare_notes()
    assert PersonalNote.objects.filter(excused=True).count() == 2
    mark_as_unexcused(None, None, PersonalNote.objects.all())
    assert PersonalNote.objects.filter(excused=True).count() == 0
    assert PersonalNote.objects.filter(excuse_type=None, excused=True).count() == 0


def test_mark_as_excuse_type_generator_action():
    excuse_type, __ = ExcuseType.objects.get_or_create(short_name="Foo", name="Fooooooooooooo")
    notes = _prepare_notes()
    assert PersonalNote.objects.filter(excused=True).count() == 2
    assert PersonalNote.objects.filter(excused=True, excuse_type=excuse_type).count() == 1
    mark_as_foo = mark_as_excuse_type_generator(excuse_type=excuse_type)
    mark_as_foo(None, None, PersonalNote.objects.all())
    assert PersonalNote.objects.filter(excused=True).count() == 4
    assert PersonalNote.objects.filter(excuse_type=excuse_type, excused=True).count() == 4


def test_delete_personal_note_action():
    notes = _prepare_notes()
    assert PersonalNote.objects.not_empty().count() == 6
    delete_personal_note(None, None, PersonalNote.objects.all())
    assert PersonalNote.objects.not_empty().count() == 0
