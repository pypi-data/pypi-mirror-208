class IDGenerator:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__instance.id = 0
        return cls.__instance

    def generate_id(self):
        id_value = self.id
        self.id += 1
        return id_value
