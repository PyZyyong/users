import os
import pickle

from wechatpy.session import SessionStorage


class FileSessionStorage(SessionStorage):
    def __init__(self):
        self._data = {}

    def _save(self):
        pickle.dump(self._data, open('/data/b2c_runtime/wx_session.p', 'wb'))

    def _load(self):
        if os.path.getsize('/data/b2c_runtime/wx_session.p') > 0:
            self._data = pickle.load(open('/data/b2c_runtime/wx_session.p', 'rb'))

    def get(self, key, default=None):
        self._load()
        return self._data.get(key, default)

    def set(self, key, value, ttl=None):
        if value is None:
            return
        self._data[key] = value
        self._save()

    def delete(self, key):
        self._data.pop(key, None)
        self._save()