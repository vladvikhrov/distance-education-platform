import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Загружаем настройки из Django settings с префиксом CELERY_
# Например: CELERY_BROKER_URL = 'redis://localhost:6379/0'
# надо добваить строки в settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Тестовая задача для проверки работы Celery"""
    print(f'Request: {self.request!r}')