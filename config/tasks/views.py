from rest_framework.viewsets import ModelViewSet
from .models import Task
from .serializers import TaskSerializer
from .tasks import process_task

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        task = serializer.save(status="PENDING")
        process_task.delay(task.id)
