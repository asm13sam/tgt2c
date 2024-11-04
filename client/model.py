from repository import Data


class Item:
    model: dict
    repo: Data

    def __init__(self, name: str):
        self.name = name
        self.value = {}
        self.values = []

    def get(self, id:int):
        res = self.repo.get(model_name=self.name, id=id)
        if res['error']:
            self.value = {}
            return res['error']
        self.value = res['value']
        return ''
    
    def get_all(self):
        res = self.repo.get_all(model_name=self.name)
        if res['error']:
            self.values = []
            return res['error']
        self.values = res['value']
        return ''
    
    def create(self):
        print('>>>>>>', self.value)
        res = self.repo.create(model_name=self.name, data=self.value)
        if res['error']:
            return res['error']
        self.value = res['value']
        return ''
    
    def update(self):
        print('>>>>>>', self.value)
        res = self.repo.update(model_name=self.name, data=self.value)
        if res['error']:
            return res['error']
        self.value = res['value']
        return ''
    
    def delete(self, id: int):
        res = self.repo.delete(model_name=self.name, id=id)
        if res['error']:
            return res['error']
        self.value = {}
        return ''
    
    def deactivate(self, id:int):
        res = self.repo.deactivate(model_name=self.name, id=id)
        if res['error']:
            return res['error']
        self.value = res['value']
        return ''