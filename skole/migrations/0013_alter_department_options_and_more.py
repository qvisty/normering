# Generated by Django 5.0.6 on 2024-07-07 10:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("skole", "0012_alter_student_options_alter_student_age_number_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="department",
            options={
                "ordering": ["name"],
                "verbose_name": "Afdeling",
                "verbose_name_plural": "Afdelinger",
            },
        ),
        migrations.AlterModelOptions(
            name="employmentcategory",
            options={
                "ordering": ["name"],
                "verbose_name": "Personalekategori",
                "verbose_name_plural": "Personalekategorier",
            },
        ),
        migrations.AlterModelOptions(
            name="lesson",
            options={
                "ordering": ["schoolclass__name", "subject", "classroom"],
                "verbose_name": "Lektion",
                "verbose_name_plural": "Lektioner",
            },
        ),
        migrations.AlterModelOptions(
            name="school",
            options={
                "ordering": ["name"],
                "verbose_name": "Skole",
                "verbose_name_plural": "Skoler",
            },
        ),
        migrations.AlterModelOptions(
            name="schoolclass",
            options={
                "ordering": ["team__department__name", "name"],
                "verbose_name": "Skoleklasse",
                "verbose_name_plural": "Skoleklasser",
            },
        ),
        migrations.AlterModelOptions(
            name="schoolfee",
            options={
                "ordering": ["level", "name"],
                "verbose_name": "Takst",
                "verbose_name_plural": "Takster",
            },
        ),
        migrations.AlterModelOptions(
            name="staff",
            options={
                "ordering": ["name"],
                "verbose_name": "Ansat",
                "verbose_name_plural": "Ansatte",
            },
        ),
        migrations.AlterModelOptions(
            name="team",
            options={
                "ordering": ["department__name", "name"],
                "verbose_name": "Team",
                "verbose_name_plural": "Teams",
            },
        ),
    ]
