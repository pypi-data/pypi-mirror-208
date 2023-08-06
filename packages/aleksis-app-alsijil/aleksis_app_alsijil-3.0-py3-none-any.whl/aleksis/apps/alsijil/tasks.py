from copy import deepcopy
from datetime import date, timedelta

from django.db.models import Q
from django.utils.translation import gettext as _

from calendarweek import CalendarWeek
from celery.result import allow_join_result
from celery.states import SUCCESS

from aleksis.apps.chronos.models import Event, ExtraLesson, LessonPeriod
from aleksis.core.models import Group, PDFFile
from aleksis.core.util.celery_progress import ProgressRecorder, recorded_task
from aleksis.core.util.pdf import generate_pdf_from_template

from .models import ExcuseType, ExtraMark, LessonDocumentation, PersonalNote


@recorded_task
def generate_full_register_printout(group: int, file_object: int, recorder: ProgressRecorder):
    """Generate a full register printout as PDF for a group."""
    context = {}

    _number_of_steps = 8

    recorder.set_progress(1, _number_of_steps, _("Load data ..."))

    group = Group.objects.get(pk=group)
    file_object = PDFFile.objects.get(pk=file_object)

    groups_q = (
        Q(lesson_period__lesson__groups=group)
        | Q(lesson_period__lesson__groups__parent_groups=group)
        | Q(extra_lesson__groups=group)
        | Q(extra_lesson__groups__parent_groups=group)
        | Q(event__groups=group)
        | Q(event__groups__parent_groups=group)
    )
    personal_notes = (
        PersonalNote.objects.prefetch_related(
            "lesson_period__substitutions", "lesson_period__lesson__teachers"
        )
        .not_empty()
        .filter(groups_q)
        .filter(groups_of_person=group)
    )
    documentations = LessonDocumentation.objects.not_empty().filter(groups_q)

    recorder.set_progress(2, _number_of_steps, _("Sort data ..."))

    sorted_documentations = {"extra_lesson": {}, "event": {}, "lesson_period": {}}
    sorted_personal_notes = {"extra_lesson": {}, "event": {}, "lesson_period": {}, "person": {}}
    for documentation in documentations:
        key = documentation.register_object.label_
        sorted_documentations[key][documentation.register_object_key] = documentation

    for note in personal_notes:
        key = note.register_object.label_
        sorted_personal_notes[key].setdefault(note.register_object_key, [])
        sorted_personal_notes[key][note.register_object_key].append(note)
        sorted_personal_notes["person"].setdefault(note.person.pk, [])
        sorted_personal_notes["person"][note.person.pk].append(note)

    recorder.set_progress(3, _number_of_steps, _("Load lesson data ..."))

    # Get all lesson periods for the selected group
    lesson_periods = LessonPeriod.objects.filter_group(group).distinct()
    events = Event.objects.filter_group(group).distinct()
    extra_lessons = ExtraLesson.objects.filter_group(group).distinct()
    weeks = CalendarWeek.weeks_within(group.school_term.date_start, group.school_term.date_end)

    register_objects_by_day = {}
    for extra_lesson in extra_lessons:
        day = extra_lesson.date
        register_objects_by_day.setdefault(day, []).append(
            (
                extra_lesson,
                sorted_documentations["extra_lesson"].get(extra_lesson.pk),
                sorted_personal_notes["extra_lesson"].get(extra_lesson.pk, []),
                None,
            )
        )

    for event in events:
        day_number = (event.date_end - event.date_start).days + 1
        for i in range(day_number):
            day = event.date_start + timedelta(days=i)
            event_copy = deepcopy(event)
            event_copy.annotate_day(day)

            # Skip event days if it isn't inside the timetable schema
            if not (event_copy.raw_period_from_on_day and event_copy.raw_period_to_on_day):
                continue

            register_objects_by_day.setdefault(day, []).append(
                (
                    event_copy,
                    sorted_documentations["event"].get(event.pk),
                    sorted_personal_notes["event"].get(event.pk, []),
                    None,
                )
            )

    recorder.set_progress(4, _number_of_steps, _("Sort lesson data ..."))

    weeks = CalendarWeek.weeks_within(
        group.school_term.date_start,
        group.school_term.date_end,
    )

    for lesson_period in lesson_periods:
        for week in weeks:
            day = week[lesson_period.period.weekday]

            if (
                lesson_period.lesson.validity.date_start
                <= day
                <= lesson_period.lesson.validity.date_end
            ):
                filtered_documentation = sorted_documentations["lesson_period"].get(
                    f"{lesson_period.pk}_{week.week}_{week.year}"
                )
                filtered_personal_notes = sorted_personal_notes["lesson_period"].get(
                    f"{lesson_period.pk}_{week.week}_{week.year}", []
                )

                substitution = lesson_period.get_substitution(week)

                register_objects_by_day.setdefault(day, []).append(
                    (lesson_period, filtered_documentation, filtered_personal_notes, substitution)
                )

    recorder.set_progress(5, _number_of_steps, _("Load statistics ..."))

    persons = group.members.prefetch_related(None).select_related(None)
    persons = group.generate_person_list_with_class_register_statistics(persons)

    prefetched_persons = []
    for person in persons:
        person.filtered_notes = sorted_personal_notes["person"].get(person.pk, [])
        prefetched_persons.append(person)

    context["school_term"] = group.school_term
    context["persons"] = prefetched_persons
    context["excuse_types"] = ExcuseType.objects.filter(count_as_absent=True)
    context["excuse_types_not_absent"] = ExcuseType.objects.filter(count_as_absent=False)
    context["extra_marks"] = ExtraMark.objects.all()
    context["group"] = group
    context["weeks"] = weeks
    context["register_objects_by_day"] = register_objects_by_day
    context["register_objects"] = list(lesson_periods) + list(events) + list(extra_lessons)
    context["today"] = date.today()
    context["lessons"] = (
        group.lessons.all()
        .select_related(None)
        .prefetch_related(None)
        .select_related("validity", "subject")
        .prefetch_related("teachers", "lesson_periods")
    )
    context["child_groups"] = (
        group.child_groups.all()
        .select_related(None)
        .prefetch_related(None)
        .prefetch_related(
            "lessons",
            "lessons__validity",
            "lessons__subject",
            "lessons__teachers",
            "lessons__lesson_periods",
        )
    )

    recorder.set_progress(6, _number_of_steps, _("Generate template ..."))

    file_object, result = generate_pdf_from_template(
        "alsijil/print/full_register.html", context, file_object=file_object
    )

    recorder.set_progress(7, _number_of_steps, _("Generate PDF ..."))

    with allow_join_result():
        result.wait()
        file_object.refresh_from_db()
        if not result.status == SUCCESS and file_object.file:
            raise Exception(_("PDF generation failed"))

    recorder.set_progress(8, _number_of_steps)
