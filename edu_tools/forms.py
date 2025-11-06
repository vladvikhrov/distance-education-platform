from django import forms
from edu.models import Lessons, Subjects, Classes

class LessonsForm(forms.ModelForm):
    class Meta:
        model = Lessons
        fields = ['topic', 'data', 'additionals', 'home_work', 'email', 'document']
        widgets = {
            'topic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите тему урока'
            }),
            'data': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'additionals': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительная информация (необязательно)'
            }),
            'home_work': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание домашнего задания'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'document': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'topic': 'Тема урока',
            'data': 'Дата урока',
            'additionals': 'Описание',
            'home_work': 'Домашнее задание',
            'email': 'Email',
            'document': 'Файл урока'
        }

    class_field = forms.ModelChoiceField(
        label='Класс',
        queryset=Classes.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_class_field'}),
        empty_label='Выберите класс'
    )
    
    subject = forms.ModelChoiceField(
        label='Предмет',
        queryset=Subjects.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_subject'}),
        empty_label='Сначала выберите класс'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Для учителей - только их предметы
        if user and user.role == 'T':
            teacher_subjects = user.subjects_id.all()
            self.fields['subject'].queryset = teacher_subjects
            
            # Получаем классы, в которых есть предметы учителя
            class_ids = Classes.objects.filter(sub_id__in=teacher_subjects).distinct()
            self.fields['class_field'].queryset = class_ids
        else:
            # Для админов - все классы и предметы
            self.fields['class_field'].queryset = Classes.objects.all()
            self.fields['subject'].queryset = Subjects.objects.all()
        
        # Если в POST передан класс, фильтруем предметы
        if 'class_field' in self.data:
            try:
                class_id = int(self.data.get('class_field'))
                class_obj = Classes.objects.get(id=class_id)
                
                if user and user.role == 'T':
                    # Пересечение: предметы учителя И предметы класса
                    self.fields['subject'].queryset = user.subjects_id.filter(
                        id__in=class_obj.sub_id.all()
                    )
                else:
                    self.fields['subject'].queryset = class_obj.sub_id.all()
            except (ValueError, TypeError, Classes.DoesNotExist):
                pass
        
        self.order_fields(['class_field', 'subject', 'topic', 'data', 'additionals', 'home_work', 'email', 'document'])