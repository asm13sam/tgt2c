import requests

ACTIVE_ONLY = 0
WITH_UNACTIVE = 1
UNACTIVE_ONLY = 2

class Data:
    def __init__(self, host, port):
        self.base_url = f'http://{host}:{port}/api/'

    def get(self, model_name: str, id: int):
        url = f'{self.base_url}{model_name}/{id}'
        print('GET', url)
        response = requests.get(url)
        return self.format_response(response)
    
    def get_all(self, model_name: str, all=ACTIVE_ONLY):
        url = f'{self.base_url}{model_name}'
        if all:
            url += f'?all={all}'
        print('GET_ALL', url)
        response = requests.get(url)
        return self.format_response(response)
    
    def delete(self, model_name: str, id: int):
        url = f'{self.base_url}{model_name}/{id}?delete=1'
        print('DELETE', url)
        response = requests.delete(url)
        return self.format_response(response)
    
    def deactivate(self, model_name: str, id: int):
        url = f'{self.base_url}{model_name}/{id}'
        print('DEACTIVATE', url)
        response = requests.delete(url)
        return self.format_response(response)

    def create(self, model_name: str, data: dict):
        url = f'{self.base_url}{model_name}'
        print('CREATE', url)
        response = requests.post(url, json=data)
        return self.format_response(response)

    def update(self, model_name: str, data: dict):
        url = f'{self.base_url}{model_name}'
        print('UPDATE', url)
        response = requests.put(url, json=data)
        return self.format_response(response)
    
    def format_response(self, response):
        if response.status_code == 500:
            return {'error': 'Server error', 'value': None}
        if response.status_code == 404:
            return {'error': 'Page not found', 'value': None}
        if response.status_code == 405:
            return {'error': 'Неприпустимий метод', 'value': None}
        # print(response.status_code, response.text)
        j = response.json()
        if 'error' in j:
            return {'error': j['error'], 'value': None}
        else:
            return {'error': '', 'value': j}
    

