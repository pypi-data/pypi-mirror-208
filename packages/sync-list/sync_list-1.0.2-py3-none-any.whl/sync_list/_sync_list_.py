import json


class SyncList:
    def __init__(self, data=None, filename='data.json'):
        self.filename = filename
        if data is None:
            self._data = []
        else:
            self._data = data
        self._load_data()

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, item):
        self._data[index] = item
        self._save_data()

    def __delitem__(self, index):
        del self._data[index]
        self._save_data()

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __reversed__(self):
        return reversed(self._data)

    def __repr__(self):
        return repr(self._data)

    def index(self, item):
        return self._data.index(item)

    def count(self, item):
        return self._data.count(item)

    def _load_data(self):
        try:
            with open(self.filename) as f:
                self._data = json.load(f)
        except FileNotFoundError:
            self._save_data()

    def _save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self._data, f)

    def append(self, item):
        self._data.append(item)
        self._save_data()

    def extend(self, iterable):
        self._data.extend(iterable)
        self._save_data()

    def insert(self, index, item):
        self._data.insert(index, item)
        self._save_data()

    def remove(self, item):
        self._data.remove(item)
        self._save_data()

    def pop(self, index=-1):
        item = self._data.pop(index)
        self._save_data()
        return item

    def clear(self):
        self._data.clear()
        self._save_data()

    def sort(self, *args, **kwargs):
        self._data.sort(*args, **kwargs)
        self._save_data()

    def reverse(self):
        self._data.reverse()
        self._save_data()
