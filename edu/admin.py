from django.contrib import admin

from edu.forms import LessonForm

from .models import Classes, Subjects, Lessons

@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    filter_horizontal = ('sub_id',)

@admin.register(Subjects)
class Subjectsdmin(admin.ModelAdmin):
    filter_horizontal = ('lesson_id',)

@admin.register(Lessons)
class LessonsAdmin(admin.ModelAdmin):
    list_display = ('topic', 'email', 'data')
    list_filter = ('data', 'email')
    form = LessonForm

