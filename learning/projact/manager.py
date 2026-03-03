import json
import os
from subscriber import Subscriber


class SubscriberManager:
    def __init__(self, filename):
        self.filename = filename
        self.subscribers = []

        dirpath = os.path.dirname(self.filename)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)

        if not os.path.exists(self.filename):
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump([], f)

        self.load()

    def load(self):
        self.subscribers = []
        with open(self.filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            s = Subscriber(item["name"], item["ip"])
            self.subscribers.append(s)

    def save(self):
        data = [s.to_dict() for s in self.subscribers]

        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add(self, subscriber):
        self.subscribers.append(subscriber)
        self.save()
        print("Added successfully!")

    def list_all(self):
        if not self.subscribers:
            print("No subscribers yet")
            return
        for i, s in enumerate(self.subscribers, start=1):
            print(f"{i}) {s.name} - {s.ip}")

    def delete(self, name):
        target = name.strip().lower()

        before = len(self.subscribers)

        self.subscribers = [
            s for s in self.subscribers
            if s.name.lower() != target
        ]

        after = len(self.subscribers)

        if after == before:
            print("Subscriber not found")
            return

        self.save()
        print("Subscriber deleted successfully!")

    def search(self, query):
        q = query.strip().lower()

        results = [
            s for s in self.subscribers
            if q in s.name.lower() or q in s.ip
        ]

        return results

    def update(self, number, new_name="", new_ip=""):
        idx = number - 1

        if idx < 0 or idx >= len(self.subscribers):
            print("Invalid number")
            return

        s = self.subscribers[idx]

        if new_name.strip():
            s.name = new_name.strip()

        if new_ip.strip():
            s.ip = new_ip.strip()

        self.save()
        print("Subscriber updated successfully!")

    def update_by_index(self, number, new_name="", new_ip=""):
        self.update(number, new_name=new_name, new_ip=new_ip)
