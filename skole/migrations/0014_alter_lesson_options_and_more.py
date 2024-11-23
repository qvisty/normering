# Generated by Django 5.0.6 on 2024-11-23 18:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("skole", "0013_alter_department_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="lesson",
            options={
                "ordering": ["schoolclass__name", "subject", "classroom"],
                "verbose_name": "Lektion",
                "verbose_name_plural": "Lektioner",
            },
        ),
        migrations.RenameField(
            model_name="lesson",
            old_name="schoolclass",
            new_name="schoolclass",
        ),
        migrations.RenameField(
            model_name="student",
            old_name="schoolclass",
            new_name="schoolclass",
        ),
        migrations.AlterField(
            model_name="schoolclass",
            name="team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="schoolclasses",
                to="skole.team",
            ),
        ),
    ]
