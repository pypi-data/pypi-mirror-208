#!/usr/bin/env python
# coding: utf-8
import os
import zipfile
import json
import datetime
from io import StringIO
from typing import List, Dict, Any
from pathlib import Path


class Message:
    def __init__(self, role: str, contents: List[str]):
        self.role = role
        self.contents = contents

    def __str__(self) -> str:
        return f"{self.role}: {self.text()}"

    def text(self) -> str:
        return '\n'.join(self.contents)

    def markdown(self) -> str:
        sio = StringIO()
        sio.write(f"_{self.role}_: ")
        sio.write('\n\n'.join(self.contents))
        result = sio.getvalue()
        sio.close()
        return result

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def from_json_dict(cls, json_dict: Dict[str, Any]) -> 'Message':
        author = json_dict['author']
        role = author['role']
        parts = json_dict['content']['parts']
        return cls(role=role, contents=parts)


class Conversation:
    def __init__(self, title: str, update_time: float, messages: List[Message]):
        self.title = title
        self.update_time = update_time
        self.messages = messages

    def updated(self) -> str:
        # convert epoch to ISO timestamp
        return datetime.datetime.fromtimestamp(self.update_time).isoformat()


def conversation(item: dict) -> Conversation:
    title = item['title']
    update_time = item['update_time']
    mapping = item['mapping']
    raw_messages = [d['message'] for d in mapping.values() if d['message'] is not None]
    messages = [Message.from_json_dict(raw) for raw in raw_messages if 'author' in raw]
    convo = Conversation(title, update_time, messages)
    return convo


def convert(zip_file_name: Path) -> Dict[str, Conversation]:
    file_to_extract = "conversations.json"
    with zipfile.ZipFile(zip_file_name, 'r') as zip_file:
        with zip_file.open(file_to_extract) as file:
            data = json.load(file)
    result = {}
    for item in data:
        convo= conversation(item)
        result[convo.title] = convo
    return result

def convert_all(directory: str, prefix: str) -> Dict[str, Conversation]:
    result = {}
    for name in os.listdir(directory):
        if name.startswith(prefix) and name.endswith('.zip'):
            pathname = os.path.join(directory, name)
            result |= convert(pathname)
    return result


