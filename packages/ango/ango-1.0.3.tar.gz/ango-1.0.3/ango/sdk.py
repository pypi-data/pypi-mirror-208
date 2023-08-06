import datetime
import logging
import mimetypes
import urllib.request
import uuid
import zipfile
from enum import Enum
from typing import List

import requests
import json

from tqdm import tqdm

from ango.models.enums import TaskStatus
from ango.models.label_category import ToolCategory, ClassificationCategory, RelationCategory


class SDK:

    def __init__(self, api_key, host="https://imeritapi.ango.ai"):
        self.api_key = api_key
        self.host = host
        self.session = requests.Session()
        if host == 'https://api.ango.ai' or host == 'https://apibeta.ango.ai':
            logging.getLogger().error("Please downgrade your version to < 1.0.0")
        logging.getLogger().warning("Your host is %s" % host)

    def list_projects(self, page=1, limit=10):
        url = "%s/v2/listProjects?page=%s&limit=%s" % (self.host, page, limit)

        payload = {}
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
        response = self.session.get(url, headers=headers, data=payload)
        return response.json()

    def get_project(self, project_id):
        url = "%s/v2/project/%s" % (self.host, project_id)

        payload = {}
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }

        response = self.session.get(url, headers=headers, data=payload)
        return response.json()

    def get_tasks(self, project_id: str, page: int = 1, limit: int = 10, status: str = None, stage: str = None,
                  batches: List[str] = None):
        url = "%s/v2/project/%s/tasks?page=%s&limit=%s" % (self.host, project_id, page, limit)
        if status:
            url += "&status[eq]=%s" % status
        if batches:
            tags = self.__get_batches(project_id, batches)
            url += "&batches=%s" % json.dumps(tags)
        if stage:
            url += "&stage=%s" % stage

        payload = {}
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
        response = self.session.get(url, headers=headers, data=payload)
        return response.json()

    def get_task(self, task_id):
        url = "%s/v2/task/%s" % (self.host, task_id)

        payload = {}
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
        response = self.session.get(url, headers=headers, data=payload)
        return response.json()

    def assign_task(self, task, userid=None, email=None):
        url = "%s/v2/task/assign" % self.host

        payload = {"task": task}
        if userid:
            payload["user"] = userid
        elif email:
            payload["username"] = email
        else:
            return Exception("userid or email required!")

        payload = json.dumps(payload)
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
        response = self.session.post(url, headers=headers, data=payload)
        return response.json()

    def _get_upload_url(self, fname: str):
        url = "%s/v2/getUploadUrl?name=%s" % (self.host, fname)
        headers = {
            'apikey': self.api_key
        }
        r = self.session.get(url, headers=headers).json()
        url = r["data"]["uploadUrl"]
        return url

    def __get_batches(self, project_id, batches):
        ptags = self.get_batches(project_id)
        resp = []
        for t1 in batches:
            batch_exist = False
            for t2 in ptags:
                if t1 == t2["_id"] or t1 == t2["name"]:
                    resp.append(t2["_id"])
                    batch_exist = True
            if not batch_exist:
                raise Exception("Tag %s not found" % t1)
        return resp

    def __check_storages(self, project_id, storage_id):
        resp = self.get_storages(project_id)
        storages_list = resp['data']['storages']
        storage_exists = False
        for t1 in storages_list:
            if '_id' in t1 and t1['_id'] == storage_id:
                storage_exists = True
        return storage_exists

    def upload_files(self, project_id: str, file_paths: List, storage_id: str = None, batches: List[str] = None):
        if storage_id and not self.__check_storages(project_id, storage_id):
            raise "Storage ID is Invalid!"
        assets = []
        for path in tqdm(file_paths):
            uid = uuid.uuid4().hex
            data = ""
            external_id = ""
            if isinstance(path, str):
                data = path
                external_id = uid
            else:
                data = path.get("data")
                external_id = path.get("externalId", uid)
            file = open(data, 'rb')
            fname = uid + '.' + file.name.split('.')[-1]
            url = self._get_upload_url(fname)
            requests.put(url, data=file.read())
            asset = {'data': url.split('?')[0], 'externalId': external_id}
            if storage_id:
                asset['storage'] = storage_id
            assets.append(asset)

        url = "%s/v2/project/%s/cloud" % (self.host, project_id)
        if batches:
            tags = self.__get_batches(project_id, batches)
            url += "?batches=%s" % json.dumps(tags)

        payload = json.dumps({"assets": assets})
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }

        response = self.session.post(url, headers=headers, data=payload)
        return response.json()

    def upload_files_cloud(self, project_id: str, assets, storage_id: str = None, batches: List[str] = None):
        if storage_id and not self.__check_storages(project_id, storage_id):
            raise "Storage ID is Invalid!"
        url = "%s/v2/project/%s/cloud" % (self.host, project_id)

        tagMap = {}
        ptags = self.get_batches(project_id)
        for tag in ptags:
            tagMap[tag['name']] = tag['_id']

        def switch_tags_names_with_ids(tags):
            resp = []
            for t1 in tags:
                tag_exist = False
                for t2 in ptags:
                    if t1 == t2["_id"] or t1 == t2["name"]:
                        resp.append(t2["_id"])
                        tag_exist = True
                if not tag_exist:
                    raise Exception("Tag %s not found" % t1)
            return resp

        for a in assets:
            if storage_id:
                a['storage'] = storage_id
            if "batches" in a:
                a['batches'] = switch_tags_names_with_ids(a['batches'])

        if batches:
            tags = switch_tags_names_with_ids(batches)
            url += "?batches=%s" % json.dumps(tags)

        payload = json.dumps({"assets": assets})
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }

        response = self.session.post(url, headers=headers, data=payload)
        return response.json()

    def create_issue(self, task_id, content, position):
        url = "%s/v2/issues" % self.host

        payload = {
            "content": content,
            "labelTask": str(task_id),
            "position": str(position)
        }
        headers = {
            'apikey': self.api_key
        }

        response = self.session.post(url, headers=headers, json=payload)
        return response.json()

    def get_assets(self, project_id, asset_id=None, external_id=None, page=1, limit=10):
        url = "%s/v2/project/%s/assets?page=%s&limit=%s" % (self.host, project_id, page, limit)
        if asset_id:
            url += "?_id=" % asset_id
        if external_id:
            url += "?externalId=" % external_id

        headers = {
            'apikey': self.api_key
        }
        response = self.session.get(url, headers=headers)
        return response.json()

    def create_attachment(self, project_id, attachments):

        url = "%s/v2/attachments" % self.host

        payload = {
            "project": project_id,
            "attachments": attachments
        }
        headers = {
            'apikey': self.api_key
        }

        response = self.session.post(url, headers=headers, json=payload)
        return response.json()

    def export(self, project_id: str, assignees: List[str] = None, completed_at: List[datetime.datetime] = None,
               updated_at: List[datetime.datetime] = None, batches: List[str] = None):

        url = "%s/v2/export?project=%s&sendEmail=false&format=json&stage=[\"Complete\"]&" \
              "includeMetadata=true&includeHistory=true&includeSegmentationPoints=true&doNotNotify=true"\
              % (self.host, project_id)
        if type(assignees) == list and len(assignees) > 0:
            url += "&assignee=" + json.dumps(assignees)
        if type(batches) == list and len(batches) > 0:
            url += "&batches=" + json.dumps(batches)
        if type(completed_at) == list and len(completed_at) == 2:
            if completed_at[0] is not None:
                url += "&completedAt[gt]=" + completed_at[0].isoformat()
            if completed_at[1] is not None:
                url += "&completedAt[lt]=" + completed_at[1].isoformat()
        if type(updated_at) == list and len(updated_at) == 2:
            if updated_at[0] is not None:
                url += "&updatedAt[gt]=" + updated_at[0].isoformat()
            if completed_at[1] is not None:
                url += "&updatedAt[lt]=" + updated_at[1].isoformat()

        headers = {
            'apikey': self.api_key
        }
        response = self.session.get(url, headers=headers)
        link = response.json()['data']['exportPath']
        filehandle, _ = urllib.request.urlretrieve(link)
        zip_file_object = zipfile.ZipFile(filehandle, 'r')
        first_file = zip_file_object.namelist()[0]
        file = zip_file_object.open(first_file)
        content = file.read()
        json_response = json.loads(content)
        return json_response

    def create_label_set(self, project_id: str, tools: List[ToolCategory] = [],
                         classifications: List[ClassificationCategory] = [],
                         relations: List[RelationCategory] = []):

        url = "%s/v2/project/%s" % (self.host, project_id)
        headers = {
            'apikey': self.api_key
        }
        payload = {
            "categorySchema": {
                "tools": list(map(lambda t: t.toDict(), tools)),
                "classifications": list(map(lambda t: t.toDict(), classifications)),
                "relations": list(map(lambda t: t.toDict(), relations))
            }
        }

        response = self.session.post(url, headers=headers, json=payload)
        return response.json()

    def import_labels(self, project_id: str, labels: List[dict]):

        url = "%s/v2/import/labels" % self.host
        headers = {
            'apikey': self.api_key
        }
        payload = {
            "project": project_id,
            "jsonContent": labels
        }

        response = self.session.post(url, headers=headers, json=payload)
        return response.json()

    def get_storages(self, id: str = None):
        url = "%s/v2/storages" % self.host
        headers = {
            'apikey': self.api_key
        }
        response = self.session.get(url, headers=headers)
        if id:
            for i in response.json().get('data', {}).get("storages", []):
                if i["_id"] == id:
                    return i
        return response.json()

    def get_batches(self, project_id: str):
        p = self.get_project(project_id)
        if 'data' in p:
            return p.get("data", {}).get("project", {}).get("batches", [])
        else:
            raise Exception('Invalid Project Id!')

    def create_batch(self, project_id: str, batch_name: str):
        url = "%s/v2/batches/%s" % (self.host, project_id)
        bacthes = self.get_batches(project_id)
        headers = {
            'apikey': self.api_key
        }
        bacthes.append({
            'name': batch_name
        })
        payload = {
            "batches": bacthes,
        }
        response = self.session.post(url, headers=headers, json=payload)
        return response.json().get("data", []).get("project", []).get("batches", [])

    def assign_batches(self, project_id: str, asset_ids: List[str], batches: List[str]):
        url = "%s/v2/assignBatches" % self.host
        batches = self.__get_batches(project_id, batches)
        headers = {
            'apikey': self.api_key
        }
        payload = {
            "assets": asset_ids,
            "batches": batches,
        }
        response = self.session.post(url, headers=headers, json=payload)
        return response.json()

    def create_project(self, name, description=""):
        url = "%s/v2/project" % self.host
        headers = {
            'apikey': self.api_key
        }
        payload = {
            "name": name,
            "description": description,
        }
        response = self.session.post(url, headers=headers, json=payload)
        return response.json()

    def _annotate(self, task_id: str, answer: dict):
        url = "%s/v2/annotate/%s?nextStage=true" % (self.host, task_id)
        headers = {
            'apikey': self.api_key
        }
        payload = {
            "answer": answer,
            "duration": 0
        }
        response = self.session.post(url, headers=headers, json=payload)
        return response.status_code == 200

    def update_workflow_stages(self, project_id: str, stages: List[dict] = []):

        url = "%s/v2/project/%s" % (self.host, project_id)
        headers = {
            'apikey': self.api_key
        }
        payload = {
            "stages": stages
        }

        response = self.session.post(url, headers=headers, json=payload)
        return response.json()

    def get_task_history(self, id: str = None, task_id: str = None):

        url = None
        if id:
            url = "%s/v2/taskHistory/%s" % (self.host, id)
        elif task_id:
            url = "%s/v2/task/%s/history" % (self.host, task_id)
        else:
            raise Exception("id or task_id should be specified!")

        headers = {
            'apikey': self.api_key
        }
        response = self.session.get(url, headers=headers)
        return response.json()