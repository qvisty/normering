from django.db import models
from datetime import datetime
from django.utils.timesince import timesince

class School(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.department.name} - {self.name}"

class EmploymentCategory(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    price_pr_lesson = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Staff(models.Model):
    name = models.CharField(max_length=100)
    employment_category = models.ForeignKey(EmploymentCategory, on_delete=models.CASCADE)
    employment_grade = models.IntegerField(default=37)

    def __str__(self):
        return self.name

class SchoolClass(models.Model):
    IND = 'Indskoling'
    MEL = 'Mellemtrin'
    UDS = 'Udskoling'
    AGE_GROUP_CHOICES = [
        (IND, 'Indskoling'),
        (MEL, 'Mellemtrin'),
        (UDS, 'Udskoling'),
    ]
    DEFAULT_AGE_GROUP = IND  # Sæt standardværdi til 'Indskoling'

    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    class_teachers = models.ManyToManyField(Staff, related_name='class_teachers', blank=True)
    class_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES, default=DEFAULT_AGE_GROUP)
    age_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

class StudentInSchoolManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(school_class__team__department__school__isnull=False)

    def __str__(self):
        return self.name

class StudentInSchoolClassManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(school_class__isnull=False)

class Lesson(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100) # fag
    classroom = models.CharField(max_length=100) #lokale
    teachers = models.ManyToManyField(Staff)

    def __str__(self):
        teachers_names = ', '.join([teacher.name for teacher in self.teachers.all()])
        return f"{self.school_class.name} har {self.subject} i {self.classroom}-lokalet med {teachers_names}"


class SchoolFee(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    level = models.IntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.level} - {self.name}: {self.amount} DKK"


class Student(models.Model):
    name = models.CharField(max_length=100)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    age_number = models.IntegerField(blank=True, null=True) # klassetrin
    date_of_birth = models.DateField(blank=True, null=True)
    DEFAULT_FEE_LEVEL = 1
    school_fee = models.ForeignKey(SchoolFee, on_delete=models.SET_NULL, blank=True, null=True)  # Tilføj denne linje

    objects = models.Manager() # Den standard manager
    in_school = StudentInSchoolManager()
    in_school_class = StudentInSchoolClassManager()

    def __str__(self):
        return self.name
    
    @property
    def age(self):
        if self.date_of_birth:
            return timesince(self.date_of_birth, datetime.now()).split(",")[0]
        return "N/A"