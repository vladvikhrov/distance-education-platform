from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
import pandas as pd
from edu.models import Classes, Lessons, Subjects
from users.models import User
from .forms import LessonsForm
from django.contrib import messages

# код для добавление учеников или учителей
def add_schoolers(request):
    if request.user.role == 'A':
        if request.method == 'POST':
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)
            role = request.POST.get('Role')
            
            
            for index, row in df.iterrows():
                username = row.get('Логин')
                name = row.get('Имя')
                surname = row.get('Фамилия')
                password = row.get('Пароль')
                patronymic = row.get('Отчество')

                if not isinstance(patronymic, str):
                    patronymic = ''

                if None in [username, name, surname, password, patronymic]:
                    messages.error(request, 'Файл имеет не верный формат.')
                    return redirect('add_schoolers')
                
                if username and password and name and surname:  
                    User.objects.create_user(login=username, password=password, first_name=name, last_name=surname, patronymic=patronymic, role=role)
            
            return redirect('home')
            
        return render(request, "tools/add_schoolers.html")  
    else:
        return HttpResponseForbidden() # нет доступа

# Добавление уроков
def edu_program(request):
    if request.user.role != 'S':
        if request.method == 'POST':
            form = LessonsForm(request.POST, request.FILES, user = request.user)
            if form.is_valid():

                lesson = Lessons.objects.create(
                    topic = request.POST.get('topic'),
                    additionals = request.POST.get('additionals'),
                    home_work = request.POST.get('home_work'),
                    data = request.POST.get('data'),
                    email = request.POST.get('email'),
                    document = request.FILES['document'],
                )
                
                subject = Subjects.objects.get(id=request.POST.get('class_field'))
                subject.lesson_id.add(lesson)
                subject.save()
                messages.success(request, 'Запись успешно создана')
            
            return redirect('redaction_teachers')
        else:
            form = LessonsForm(user = request.user)
        return render(request, 'tools/edu_program.html', {'form': form})
    else:
        return HttpResponseForbidden()


def class_change(request):
    if request.user.role == 'A':
        students = User.objects.filter(role='S')
        classes = Classes.objects.all()
        if request.method == 'POST':
            selected_students = request.POST.getlist('selected_students')
            class_name= int(request.POST.get('class_filter'))
            print(class_name)
            for selection in selected_students: 
                    User.objects.filter(pk=int(selection)).update(classes_id=class_name)
        return render(request, 'tools/class_change.html', {'students': students, 'classes': classes})
    else:
        return HttpResponseForbidden()

