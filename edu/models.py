import os
from django.db import models


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    ext = filename.split('.')[-1]
    filename = "%s_%s.%s" % (instance.topic, os.path.splitext(filename)[0], ext)
    return os.path.join('files', filename)


class Lessons(models.Model):
    data = models.DateField(verbose_name='Дата')
    topic = models.TextField(verbose_name='Тема урока')
    additionals = models.TextField(verbose_name='Дополнительные материалы', blank=True, null=True, help_text='Это не обязательное поле')
    home_work = models.TextField(verbose_name='Домашняя работа')
    email = models.EmailField(blank=True, verbose_name='Почта учителя', help_text='Это не обязательное поле')
    document = models.FileField(blank=True, null=True, upload_to=user_directory_path, verbose_name='Файлы урока', help_text='Это не обязательное поле')
    
    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ["-data"]
        
    def __str__(self):
        return self.topic
    
    # def save(self, *args, **kwargs):
    #     self.email = self.request.user.email
    #     super(Lessons, self).save(*args, **kwargs)


class Subjects(models.Model):
    name = models.CharField(max_length=20, verbose_name='Название')
    lesson_id = models.ManyToManyField(Lessons, verbose_name='Уроки')
    
    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'
        
    def __str__(self):
        return self.name
    
    
class Classes(models.Model):
    number = models.CharField(max_length=2, verbose_name='Номер класса')
    letter = models.CharField(max_length=1, verbose_name='Параллель')
    sub_id = models.ManyToManyField(Subjects, verbose_name='Предметы', blank=True)
    
    class Meta:
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'
        ordering = ["id"]
        
    def get_class(self):
        return self.number + self.letter
        
    def __str__(self):
        return self.number + self.letter