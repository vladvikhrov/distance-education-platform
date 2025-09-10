from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'), # главная страница
    path('edu/detail-lesson/<int:lesson_id>', views.lesson_detail, name='detail_lesson'),
    path('students/homework-list', views.list_homework_view, name='homework-list'),
    path('teachers/redaction', views.redaction, name='redaction_teachers'),
]
