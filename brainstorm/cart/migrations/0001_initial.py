# Generated by Django 4.2.6 on 2023-11-04 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('rule_id', models.AutoField(primary_key=True, serialize=False)),
                ('lhs', models.CharField(max_length=255)),
                ('rhs', models.CharField(max_length=255)),
                ('confidence', models.IntegerField()),
            ],
        ),
    ]
