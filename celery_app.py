import os
from celery import Celery
from config import REDIS_HOST, REDIS_PORT

app = Celery(
    'rpg_bot',
    broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/0',
    backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/0',
    include=['tasks']  # Import tasks modules
)

# Configure Celery
app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
    
    # Concurrency settings
    worker_concurrency=2,
    
    # Task result backend settings
    task_ignore_result=False,
    task_store_errors_even_if_ignored=True,
    
    # Tasks will be removed from the result backend after 1 day
    result_expires=86400,
    
    # Beat settings for periodic tasks
    beat_schedule={
        'check-reminders-every-minute': {
            'task': 'tasks.check_reminders',
            'schedule': 60.0,  # Every minute
        },
    },
)

if __name__ == '__main__':
    app.start() 