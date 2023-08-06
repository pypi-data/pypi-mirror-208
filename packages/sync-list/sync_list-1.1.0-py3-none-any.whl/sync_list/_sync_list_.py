import json
import os


class SyncList:
    _data = {}

    def __init__(self, data=None, filename='data.json', bucket_name: str = "default"):
        self.filename = filename
        self.bucket = bucket_name
        self._load_data()
        if data is None:
            if bucket_name in self._data:
                ...
            else:
                self._data[self.bucket] = []
        else:
            self._data[self.bucket] = data

    def __getitem__(self, index):
        return self._data[self.bucket][index]

    def __setitem__(self, index, item):
        self._data[self.bucket][index] = item
        self._save_data()

    def destroy(self):
        os.remove(self.filename)
        del self

    def __delitem__(self, index):
        del self._data[self.bucket][index]
        self._save_data()

    def __len__(self):
        return len(self._data[self.bucket])

    def __iter__(self):
        return iter(self._data[self.bucket])

    def __reversed__(self):
        return reversed(self._data[self.bucket])

    def __repr__(self):
        return repr(self._data[self.bucket])

    def index(self, item):
        return self._data[self.bucket].index(item)

    def count(self, item):
        return self._data[self.bucket].count(item)

    def __add__(self, other):
        if isinstance(other, list):
            self._data[self.bucket] += other
            self._save_data()
            return self
        else:
            raise TypeError("Unsupported operand type for +: SyncList and {}".format(type(other).__name__))

    def copy(self):
        new_obj = SyncList(
            data=self._data[self.bucket].copy(),
            filename=self.filename,
            bucket_name=self.bucket
        )
        return new_obj

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
        self._data[self.bucket].append(item)
        self._save_data()

    def extend(self, iterable):
        self._data[self.bucket].extend(iterable)
        self._save_data()

    def insert(self, index, item):
        self._data[self.bucket].insert(index, item)
        self._save_data()

    def remove(self, item):
        self._data[self.bucket].remove(item)
        self._save_data()

    def pop(self, index=-1):
        item = self._data[self.bucket].pop(index)
        self._save_data()
        return item

    def clear(self):
        self._data[self.bucket].clear()
        self._save_data()

    def sort(self, *args, **kwargs):
        self._data[self.bucket].sort(*args, **kwargs)
        self._save_data()

    def reverse(self):
        self._data[self.bucket].reverse()
        self._save_data()
