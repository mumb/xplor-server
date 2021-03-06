# Generated by Django 2.0.2 on 2018-03-17 08:48

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Museum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('coordinates', django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=255)),
                ('rating', models.FloatField()),
                ('description', models.TextField()),
                ('thumbnail', models.ImageField(upload_to='photos')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MuseumImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(upload_to='photos')),
                ('museum', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='images', to='core.Museum')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Just an identifier', max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='QuizCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QuizItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.FileField(upload_to='')),
                ('question', models.CharField(max_length=255)),
                ('options', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), size=4)),
                ('hint', models.TextField(blank=True, null=True)),
                ('trivia', models.TextField(help_text='Shown to the user after answering the question')),
                ('answer', models.CharField(max_length=64)),
                ('points', models.PositiveSmallIntegerField(default=50)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Quiz')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UpcomingEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('image', models.ImageField(upload_to='photos')),
                ('status', models.CharField(choices=[('A', 'ACTIVE'), ('IN', 'INACTIVE')], default='IN', max_length=2)),
                ('museum', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='upcoming_events', to='core.Museum')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('correct', models.BooleanField()),
                ('quiz_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.QuizItem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='quizitem',
            name='user_answers',
            field=models.ManyToManyField(editable=False, through='core.UserAnswer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='quiz',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.QuizCategory'),
        ),
        migrations.AddField(
            model_name='quiz',
            name='museum',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Museum'),
        ),
        migrations.AlterUniqueTogether(
            name='useranswer',
            unique_together={('user', 'quiz_item')},
        ),
        migrations.AlterUniqueTogether(
            name='quiz',
            unique_together={('category', 'museum')},
        ),
    ]
