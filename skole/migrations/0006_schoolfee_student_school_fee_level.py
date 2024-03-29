# Generated by Django 5.0.3 on 2024-03-27 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skole', '0005_remove_schoolclass_class_teacher_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(choices=[(1, 'Trin 1'), (2, 'Trin 2'), (3, 'Trin 3')])),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='school_fee_level',
            field=models.IntegerField(blank=True, choices=[(1, 'Trin 1'), (2, 'Trin 2'), (3, 'Trin 3')], null=True),
        ),
    ]
