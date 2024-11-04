import json

from repository import Data
from gui import MainWindow
from model import Item
from widgets import ProtoWidget

with open ('config.json', "r") as f:
    cfg = json.loads(f.read())

with open ('model.json', "r") as f:
    app_model = json.loads(f.read())

with open ('hum.json', "r") as f:
    app_hum = json.loads(f.read())


clt_data = Data(cfg['host'], cfg['port'])
Item.model = app_model
Item.repo = clt_data
ProtoWidget.app_model = app_model
ProtoWidget.hum = app_hum
# ProtoWidget.colors = cfg['colors']


w = MainWindow()
w.run()
