from celery import shared_task
from .models import Task
import time

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5)
def process_task(self, task_id):
    print("[Celery] : Recevied task : ", task_id)
    channel_layer = get_channel_layer()

    task = Task.objects.get(id=task_id)

    # PROCESSING
    task.status = "PROCESSING"
    task.save()

    async_to_sync(channel_layer.group_send)(
        f"task_{task.id}",
        {
            "type": "task_update",
            "status": task.status,
        }
    )

    time.sleep(5)

    # COMPLETED
    task.status = "COMPLETED"
    task.save()

    async_to_sync(channel_layer.group_send)(
        f"task_{task.id}",
        {
            "type": "task_update",
            "status": task.status,
        }
    )
