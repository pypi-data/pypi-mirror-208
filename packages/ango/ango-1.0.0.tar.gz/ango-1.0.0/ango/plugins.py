import datetime
import logging
from io import BytesIO
from typing import Callable, Tuple

import requests
import socketio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ango.plugin_logger import PluginLogger
from ango.sdk import SDK

try:
    import asyncio
except ImportError:
    import trollius as asyncio


class Plugin(socketio.ClientNamespace):

    def __init__(self, id: str, secret: str, callback: Callable):
        super().__init__('/plugin')
        self.id = id
        self.secret = secret
        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.heartbeat, 'interval', seconds=60)
        scheduler.start()
        self.logger = logging.getLogger()
        self.callback = callback

    def on_connect(self):
        self.logger.warning("Connected")
        self.heartbeat()

    def on_disconnect(self):
        self.logger.warning("Disconnected")

    def heartbeat(self):
        self.emit('heartbeat', {"id": self.id, "secret": self.secret})

    def on_plugin(self, data):
        data["logger"] = self._get_logger(data)
        data["batches"] = data.get('tags', [])
        response = {
            "response": self.callback(**data),
            "session": data.get("session", "")
        }
        self.emit('response', response)

    def _get_logger(self, data):
        org_id = data.get("orgId", "")
        run_by = data.get("runBy", "")
        session = data.get("session", "")
        logger = PluginLogger("logger", self.id, org_id, run_by, session, self)
        return logger


class ExportPlugin(Plugin):

    def __init__(self, id: str, secret: str, callback: Callable[[str, dict], Tuple[str, BytesIO]],
                 host="https://api.ango.ai"):
        super().__init__(id, secret, callback)
        self.host = host

    def on_plugin(self, data):
        """
        :param data: {project_id: str, assignees: List[str] = None, completed_at: List[datetime.datetime] = None,
               updated_at: List[datetime.datetime = None, tags: List[str] = None}
        :return:
        """
        completed_at = None
        updated_at = None
        project_id = data.get('projectId')
        logger = super()._get_logger(data)
        api_key = data.get('apiKey')
        sdk = SDK(api_key=api_key, host=self.host)

        if data.get("completed_at", None):
            completed_at = [datetime.datetime.fromisoformat(data.completed_at[0]),
                            datetime.datetime.fromisoformat(data.completed_at[1])]
        if data.get("updated_at", None):
            updated_at = [datetime.datetime.fromisoformat(data.updated_at[0]),
                          datetime.datetime.fromisoformat(data.updated_at[1])]
        json_export = sdk.export(project_id, data.get('assignees', None), completed_at=completed_at,
                                 updated_at=updated_at, batches=data.get('tags', None))
        data["jsonExport"] = json_export
        data["logger"] = logger
        file_name, export_bytes = self.callback(**data)
        upload_url = sdk._get_upload_url(file_name)
        upload_resp = requests.put(upload_url, data=export_bytes.getvalue())
        if upload_resp.status_code != 200:
            logging.getLogger().error("Unable to upload exports!")
        response = {
            "export": True,
            "response": upload_url.split("?")[0],
            "session": data.get("session", "")
        }
        self.emit('response', response)


class ModelPlugin(Plugin):
    def __init__(self, id: str, secret: str, callback: Callable, host="https://api.ango.ai"):
        super().__init__(id, secret, callback)
        self.host = host

    def on_plugin(self, data):
        workflow = data.get('workflow')
        if not workflow:
            return super().on_plugin(data)
        api_key = data.get('apiKey')
        task_id = data.get('labeltask').get('_id')
        sdk = SDK(api_key=api_key, host=self.host)
        answer = self.callback(**data)
        annotation = {
            "tools": answer.get("answer").get("objects") + data.get('labeltask').get("answer").get("tools"),
            "classifications": answer.get("answer").get("classifications") + data.get('labeltask').get("answer").get("classifications"),
            "relations": answer.get("answer").get("relations") + data.get('labeltask').get("answer").get("relations")
        }
        return sdk._annotate(task_id, annotation);

class FileExplorerPlugin(Plugin):
    def __init__(self, id: str, secret: str, callback: Callable):
        super().__init__(id, secret, callback)


class BatchModelPlugin(Plugin):
    def __init__(self, id: str, secret: str, callback: Callable):
        super().__init__(id, secret, callback)


class InputPlugin(Plugin):
    def __init__(self, id: str, secret: str, callback: Callable):
        super().__init__(id, secret, callback)


class MarkdownPlugin(Plugin):
    def __init__(self, id: str, secret: str, callback: Callable):
        super().__init__(id, secret, callback)


def run(plugin, host="https://api.ango.ai"):
    sio = socketio.Client()
    sio.register_namespace(plugin)
    sio.connect(host, namespaces=["/plugin"], wait_timeout=100)
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logging.getLogger().warning("Plugin Stopped")
