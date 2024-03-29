from django.shortcuts import render
from django.db.models import Sum, CharField, Count, Value, F
from django.db.models.functions import Concat
from .models import SchoolClass, Lesson
from collections import defaultdict


def school_class_detail(request, class_id):
    school_class = SchoolClass.objects.annotate(total_school_fee=Sum('students__school_fee__amount')).get(pk=class_id)
    lessons = Lesson.objects.filter(school_class=school_class).annotate(
        teacher_name=Concat('teachers__name', Value(' - '), output_field=CharField()),
        total_lessons=Count('id'),
        employment_category=F('teachers__employment_category__name')  # Brug kategorinavnet her
    ).values('teacher_name', 'employment_category', 'subject', 'classroom').annotate(
        total_lessons_per_teacher=Count('id')
    ).order_by('teacher_name', 'subject')
    

    # Calculate total hours per employment category
    total_hours = defaultdict(int)
    for lesson in lessons:
        total_hours[lesson['employment_category']] += lesson['total_lessons_per_teacher']

    # Convert total_hours to a list of tuples
    total_hours_list = [(category, hours) for category, hours in total_hours.items()]


    # Calculate total sum
    total_sum = sum(total_hours.values())

    # Calculate total number of lessons in the class
    total_lessons_in_class = Lesson.objects.filter(school_class=school_class).count()


    return render(request, 'skole/schoolclass_detail.html', {'school_class': school_class, 'lessons': lessons, 'total_hours': total_hours_list, 'total_sum': total_sum, 'total_lessons_in_class': total_lessons_in_class})





def homepage(request):
    school_classes = SchoolClass.objects.all()

    return render(request, 'skole/homepage.html', {'school_classes': school_classes})
