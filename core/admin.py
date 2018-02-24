from .models import (
    Museum,
    Quiz,
    Question,
    QuizCategory,
    UpcomingEvent,
    MuseumImage,
)
from django.forms import Textarea
from django.contrib.gis import admin
from django.db import models


class MuseumAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'city', 'country', 'rating')
    list_filter = ('city', 'country')


class QuestionInlineAdmin(admin.StackedInline):
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={
                'rows': 2,
                'cols': 20,
            })
        },
    }
    fieldsets = ((
        None, {
            'fields': (('question', 'image'), ('options', 'answer'), (
                'hint',
                'trivia',
            ))
        }
    ),)
    model = Question
    extra = 0


class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInlineAdmin]


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question')
    list_filter = ('quiz', 'quiz__museum', 'created_at')


admin.site.register(Museum, MuseumAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizCategory)
admin.site.register(UpcomingEvent)
admin.site.register(MuseumImage)
