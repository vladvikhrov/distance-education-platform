from django import forms
from .models import Lessons

class LessonForm(forms.ModelForm):
    remove_file = forms.BooleanField(required=False, label='Удалить файл')
    
    class Meta:
        model = Lessons
        fields = ['data', 'topic', 'additionals', 'home_work', 'email', 'document']
        widgets = {
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'topic': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'additionals': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'home_work': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'document': forms.FileInput(attrs={'class': 'form-control'})
        }
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('remove_file'):
            instance.file = None  
        if commit:
            instance.save()
            self.save_m2m()
        return instance