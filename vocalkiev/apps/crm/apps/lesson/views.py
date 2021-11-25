import datetime

from django.shortcuts import render, get_object_or_404, redirect

from vocalkiev.apps.crm.apps.lesson.forms import PlaceDateForm, TimeForm, ClassroomForm, PassLessonForm, \
    LessonReportsForm
from vocalkiev.apps.crm.models import ClientSubscription, Lesson, Classroom, LessonComment


def index(request):
    return redirect('crm-subscriptions')


def show_subscriptions(request):
    client_subscriptions = ClientSubscription.objects.filter(teacher_id=request.user.id)
    return render(request, 'lesson/subscriptions.html', {'client_subscriptions': client_subscriptions})


def show_lessons(request, client_subscription_id):
    client_subscription = ClientSubscription.objects.get(pk=client_subscription_id)
    lessons = Lesson.objects.filter(client_subscription__id=client_subscription.id)
    return render(request, 'lesson/lessons.html', {'client_subscription': client_subscription, 'lessons': lessons})


def create_lesson(request, client_subscription_id):
    client_subscription = get_object_or_404(ClientSubscription, pk=client_subscription_id)

    if not client_subscription.can_create_lesson():
        return redirect('crm-subscription-lessons', client_subscription_id=client_subscription.id)

    place = None
    date = None
    date_hour = None
    time_form = None
    classroom_form = None

    if request.method == 'POST':
        place_date_form = PlaceDateForm(request.POST)
        if place_date_form.is_valid():
            place = place_date_form.cleaned_data['place']
            date = place_date_form.cleaned_data['date']

            time_form = TimeForm(request.POST)
            if time_form.is_valid():
                date_hour = time_form.cleaned_data['date_hour']

                if date_hour:
                    classroom_form = ClassroomForm(request.POST)

                    if classroom_form.is_valid():
                        date_hour = classroom_form.cleaned_data['date_hour']
                        classroom_id = classroom_form.cleaned_data['classroom']

                        if classroom_id:
                            classroom = get_object_or_404(Classroom, pk=classroom_id)

                            dt = datetime.datetime(date.year, date.month, date.day, date_hour)

                            new_lesson = Lesson.objects.create(
                                creator=request.user,
                                client_subscription=client_subscription,
                                classroom=classroom,
                                teacher=request.user,
                                datetime=dt,
                            )
                            new_lesson.save()

                            return redirect('crm-schedule-day',
                                            year=date.year,
                                            month=date.month,
                                            day=date.day,
                                            place_id=classroom.place.id
                                            )
    else:
        place_date_form = PlaceDateForm()

    return render(
        request,
        'lesson/create-lesson.html',
        {
            'client_subscription': client_subscription,
            'place': place,
            'date': date,
            'date_hour': date_hour,
            'place_date_form': place_date_form,
            'time_form': time_form,
            'classroom_form': classroom_form,
        }
    )


def pass_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)

    if lesson.is_passed:
        return redirect('crm-subscription-lessons', client_subscription_id=lesson.client_subscription.id)

    if request.method == 'POST':
        pass_lesson_form = PassLessonForm(request.POST)
        if pass_lesson_form.is_valid():
            lesson.is_passed = True
            lesson.save()

            new_comment = LessonComment.objects.create(
                creator=request.user,
                lesson=lesson,
                comment=pass_lesson_form.cleaned_data['comment']
            )
            new_comment.save()

            return redirect('crm-subscription-lessons', client_subscription_id=lesson.client_subscription.id)
    else:
        pass_lesson_form = PassLessonForm()

    return render(
        request,
        'lesson/pass-lesson.html',
        {
            'lesson': lesson,
            'form': pass_lesson_form
        }
    )


def reports(request):
    lessons = None
    year = None
    month = None
    total = 0

    if request.method == 'POST':
        lesson_reports_form = LessonReportsForm(request.POST)

        if lesson_reports_form.is_valid():
            year = int(lesson_reports_form.cleaned_data['year'])
            month = int(lesson_reports_form.cleaned_data['month'])

            lessons = Lesson.objects.filter(
                teacher_id=request.user.id,
                is_passed=True,
                datetime__year=year,
                datetime__month=month
            )

            for lesson in lessons:
                total += lesson.teacher_amount()
    else:
        lesson_reports_form = LessonReportsForm()

    return render(
        request,
        'lesson/reports.html',
        {
            'lessons': lessons,
            'form': lesson_reports_form,
            'year': year,
            'month': month,
            'total': total,
        }
    )
