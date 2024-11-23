import re
from collections import defaultdict
from datetime import datetime

from django.db import models
from django.utils.timesince import timesince

from .managers import SchoolClassManager


class School(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Skole"
        verbose_name_plural = "Skoler"
        ordering = ["name"]


class Department(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="departments"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Afdeling"
        verbose_name_plural = "Afdelinger"
        ordering = ["name"]


class Team(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="teams"
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        ordering = ["department__name", "name"]


class EmploymentCategory(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    price_pr_lesson = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Personalekategori"
        verbose_name_plural = "Personalekategorier"
        ordering = ["name"]


class Staff(models.Model):
    name = models.CharField(max_length=100)
    employment_category = models.ForeignKey(
        EmploymentCategory, on_delete=models.CASCADE, related_name="staff_members"
    )
    employment_grade = models.IntegerField(default=37)

    def __str__(self):
        return self.name

    @classmethod
    def total_lessons_taught_in_class(cls, schoolclass):
        """
        Beregn det samlede antal lektioner, alle medarbejdere i denne kategori har undervist i en bestemt klasse.
        """
        return cls.objects.filter(taught_lessons__schoolclass=schoolclass).count()

    class Meta:
        verbose_name = "Ansat"
        verbose_name_plural = "Ansatte"
        ordering = ["name"]


from collections import Counter


class SchoolClass(models.Model):
    IND = "Indskoling"
    MEL = "Mellemtrin"
    UDS = "Udskoling"
    AGE_GROUP_CHOICES = [
        (IND, "Indskoling"),
        (MEL, "Mellemtrin"),
        (UDS, "Udskoling"),
    ]
    DEFAULT_AGE_GROUP = IND

    name = models.CharField(max_length=100)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="schoolclasses"
    )
    class_teachers = models.ManyToManyField(
        Staff, related_name="class_teachers", blank=True
    )
    class_group = models.CharField(
        max_length=20, choices=AGE_GROUP_CHOICES, default=DEFAULT_AGE_GROUP
    )
    age_number = models.IntegerField(blank=True, null=True)

    objects = SchoolClassManager()  # Brug den brugerdefinerede manager

    def get_class_number(self):
        match = re.match(r"(\d+)", self.name)
        return int(match.group(0)) if match else 0

    def total_lessons_per_category(self):
        total_lessons_by_category = Counter()
        for lesson in self.lessons.all():
            for teacher in lesson.teachers.all():
                category = teacher.employment_category.name
                total_lessons_by_category[category] += 1
        return total_lessons_by_category

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Skoleklasse"
        verbose_name_plural = "Skoleklasser"
        ordering = ["team__department__name", "name"]


class StudentInSchoolManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(schoolclass__team__department__school__isnull=False)
        )

    def __str__(self):
        return self.name


class StudentInSchoolClassManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(schoolclass__isnull=False)


class Lesson(models.Model):
    schoolclass = models.ForeignKey(
        SchoolClass, on_delete=models.CASCADE, related_name="lessons"
    )
    subject = models.CharField(max_length=100)  # fag
    classroom = models.CharField(max_length=100)  # lokale
    teachers = models.ManyToManyField(Staff, related_name="taught_lessons")

    def __str__(self):
        teachers_names = ", ".join([teacher.name for teacher in self.teachers.all()])
        return f"{self.schoolclass.name} har {self.subject} i {self.classroom}-lokalet med {teachers_names}"

    class Meta:
        verbose_name = "Lektion"
        verbose_name_plural = "Lektioner"
        ordering = ["schoolclass__name", "subject", "classroom"]


class SchoolFee(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    level = models.IntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.level} - {self.name}: {self.amount} DKK"

    class Meta:
        verbose_name = "Takst"
        verbose_name_plural = "Takster"
        ordering = ["level", "name"]


class Student(models.Model):
    name = models.CharField(max_length=100, help_text="Elevens fulde navn")
    schoolclass = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="students",
        help_text="Vælg den klasse, som eleven tilhører",
    )
    age_number = models.IntegerField(
        blank=True, null=True, help_text="Indtast klassetrin"
    )
    date_of_birth = models.DateField(
        blank=True, null=True, help_text="Indtast fødselsdato i formatet YYYY-MM-DD"
    )
    DEFAULT_FEE_LEVEL = 1
    school_fee = models.ForeignKey(
        SchoolFee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Vælg takst (kriterie) i tildelingsmodellen",
    )

    objects = models.Manager()  # Standard manager
    in_school = StudentInSchoolManager()
    in_schoolclass = StudentInSchoolClassManager()

    def save(self, *args, **kwargs):
        if self.school_fee is None:
            default_fee = SchoolFee.objects.filter(level=self.DEFAULT_FEE_LEVEL).first()
            if default_fee:
                self.school_fee = default_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def age(self):
        if self.date_of_birth:
            return timesince(self.date_of_birth, datetime.now()).split(",")[0]
        return "N/A"

    class Meta:
        verbose_name = "Elev"
        verbose_name_plural = "Elever"
        ordering = ["name"]
