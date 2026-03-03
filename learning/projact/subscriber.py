class Subscriber:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
    
    def to_dict(self):
        return {
            "name": self.name,
            "ip": self.ip
        }
