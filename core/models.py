from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from base.models import BaseModel


class Museum(BaseModel):
    name = models.CharField(max_length=255)
    coordinates = gis_models.PointField(
        geography=True,
        srid=4326,
        spatial_index=True,
    )
    address = models.TextField()
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    rating = models.FloatField()
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='photos')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Museum")
        verbose_name_plural = _("Museums")


class QuizCategory(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Quiz Category")
        verbose_name_plural = _("Quiz Categories")


class Quiz(BaseModel):
    name = models.CharField(
        max_length=128,
        help_text=_("Just an identifier"),
    )
    category = models.ForeignKey(QuizCategory, on_delete=models.PROTECT)
    museum = models.ForeignKey(Museum, on_delete=models.PROTECT)

    def __str__(self):
        return '%s (%s)' % (self.name, self.category)

    class Meta:
        unique_together = (('category', 'museum'),)
        verbose_name = _("Quiz")
        verbose_name_plural = _("Quizzes")


class Question(BaseModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    image = models.FileField()
    question = models.CharField(max_length=255)
    options = ArrayField(models.CharField(max_length=64), size=4)
    hint = models.TextField(blank=True, null=True)
    trivia = models.TextField(
        help_text=_("Shown to the user after answering the question"),
    )
    answer = models.CharField(max_length=64)
    user_answers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='UserAnswer',
        editable=False,
    )
    points = models.PositiveSmallIntegerField(default=50)

    def clean(self):
        if self.answer not in self.options:
            raise ValidationError({'answer': _("Must be one of the options!")})

    def __str__(self):
        return self.question


class UserAnswer(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    answer = models.CharField(max_length=64)
    correct = models.BooleanField()

    class Meta:
        unique_together = (('user', 'question'),)


class MuseumImage(BaseModel):
    museum = models.ForeignKey(
        Museum,
        related_name='images',
        on_delete=models.SET_NULL,
        null=True,
    )
    image = models.ImageField(upload_to='photos')


class UpcomingEvent(BaseModel):

    ACTIVE = 'A'
    INACTIVE = 'IN'
    STATUS_CHOICES = (('A', 'ACTIVE'), (INACTIVE, 'INACTIVE'))

    name = models.CharField(max_length=255)
    date = models.DateField()
    image = models.ImageField(upload_to='photos')
    museum = models.ForeignKey(
        Museum,
        related_name='upcoming_events',
        on_delete=models.SET_NULL,
        null=True,
    )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=INACTIVE)

    def __str__(self):
        return self.name
