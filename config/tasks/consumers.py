from channels.generic.websocket import AsyncWebsocketConsumer
import json

class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope["url_route"]["kwargs"]["task_id"]
        print("[TaskConsumer] : task_id -> ", self.task_id)
        self.group_name = f"task_{self.task_id}"
        print("[TaskConsumer] : group_name -> ", self.group_name)

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        print("[Disconnected] : ", close_code)
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def task_update(self, event):
        print("[TaskConsumer] : task_update -> ", event)
        await self.send(json.dumps({
            "status": event["status"]
        }))
