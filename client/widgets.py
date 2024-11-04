from PyQt6.QtCore import (
    Qt,
    QDate,
    pyqtSignal,
    QEvent,
    QModelIndex,
    )
from PyQt6 import QtGui

from PyQt6.QtGui import QStandardItemModel, QStandardItem, QKeyEvent
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QWidget,
    QLineEdit,
    QTextEdit,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QCalendarWidget,
    QSplitter,
    QApplication,
    QGridLayout,
    QTabWidget,
    QTableView,
    QHeaderView,
    QAbstractItemView,
    QTreeWidget,
    QTreeWidgetItem,
    QComboBox,
    )

from dialogs import error
from model import Item

ID_ROLE = 100
SORT_ROLE = 101


class ProtoWidget:
    app_model: dict
    hum: dict
    colors: dict

    def reload_widget(self):
        pass

    def get_fields(self):
        return self.app_model[self.name]['fields']
    
    def get_hum(self):
        return self.hum[self.name]['hum']

    def prepare_fields_and_headers(self):
        keys = self.app_model[self.name]['fields'].keys()
        self.field_names = []
        self.headers = []
        for k in keys:
            self.field_names.append(k)
            header = self.hum[self.name]['fields'][k]['hum']
            self.headers.append(header)
            if k.endswith('_id'):
                self.field_names.append(k[:-3])
                self.headers[-1] += ' [id]'
                self.headers.append(header)


class Info(QWidget, ProtoWidget):
    def __init__(self, type_name: str):
        self.name = type_name
        self.value = {}
        super().__init__()
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        info = QWidget()
        vbox.addWidget(info)
        vbox.addStretch()
        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setVerticalSpacing(1)
        info.setLayout(self.grid)

        # info_names_color = self.colors['info_names_color'] if 'info_names_color' in self.colors else 'lightgreen'
        # self.setStyleSheet(f'color: {info_names_color}; padding: 0px;')
        # info_values_color = self.colors['info_values_color'] if 'info_values_color' in self.colors else 'yellow'
        # info_bg_color = self.colors['info_bg_color'] if 'info_bg_color' in self.colors else 'black'
        
        info_names_color =  'lightgreen'
        self.setStyleSheet(f'color: {info_names_color}; padding: 0px;')
        info_values_color =  'yellow'
        info_bg_color = 'black'
        

        self.prepare_fields_and_headers()
        self.labels: dict[str, QLabel] = {}
        row = 0
        align = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
        for field, header in zip(self.field_names, self.headers):
            field_hum = QLabel(header)
            self.labels[field] = QLabel('---')
            self.grid.addWidget(field_hum, row, 0, align)
            self.grid.addWidget(self.labels[field], row, 1)
            self.labels[field].installEventFilter(self)
            self.labels[field].setStyleSheet(f'min-width: 5em;color:{info_values_color}; padding: 2px; background-color: {info_bg_color};')
            row += 1

    def clear(self):
        for label in self.labels.values():
            label.setText('---')

    def eventFilter(self, source, event: QEvent):
        if event.type() == QEvent.Type.MouseButtonDblClick:
            clipboard = QApplication.clipboard()
            clipboard.setText(source.text())
        return super(Info, self).eventFilter(source, event)

    def set_value(self, value:dict):
        if self.value:
            self.clear()
        self.value = value
        fields = self.get_fields()
        for field, label in self.labels.items():
            default = fields[field]['def'] if field in fields else ''
            txt = prepare_value_to_str(default, value[field])
            label.setText(txt)


def prepare_value_to_str(def_value, value) -> str:
    t = type(def_value)
    if t == bool:
        return 'Так' if value else 'Ні'
    if t == float:
        return str(round(value, 2))
    if t == str:
        return value
    return str(value)


class TableModel(QStandardItemModel, ProtoWidget):
    def __init__(self, type_name: str):
        super().__init__()
        self.name = type_name
        self.prepare_fields_and_headers()
        self.setHorizontalHeaderLabels(self.headers)
        self.setSortRole(SORT_ROLE)
        self.values = {}

    def set_values(self, values):
        self.clear()
        self.values = {v['id']: v for v in values}
        self.setHorizontalHeaderLabels(self.headers)
        for value in values:
            self.append(value)

    def append(self, value):
        row = []
        for field in self.field_names:
            row.append(self.make_item(value[field], field))
        # row[0].setData(ID_ROLE, value['id'])
        self.appendRow(row)

    def make_item(self, value, field):
        fields = self.get_fields()
        default = fields[field]['def'] if field in fields else ''
        txt = prepare_value_to_str(default, value)
        item = QStandardItem(txt)
        item.setData(value, SORT_ROLE)
        item.setEditable(False)
        return item
    
    def get_row_value(self, row):
        return self.values[int(self.item(row).text())]


class Table(QTableView, ProtoWidget):
    valueSelected = pyqtSignal(dict)
    valueDoubleCklicked = pyqtSignal(dict)
    tableChanged = pyqtSignal()
    def __init__(self, data_model: TableModel):
        super().__init__()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setStretchLastSection(True)

        self._model = data_model
        self.setModel(self._model)
        # self.clicked[QModelIndex].connect(self.value_selected)
        self.doubleClicked[QModelIndex].connect(self.value_dblclicked)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
    # def add_value(self, value):
    #     self._model.append(value)
    #     self.tableChanged.emit()

    def reload_widget(self):
        item = Item(self._model.name)
        err = item.get_all()
        if err:
            error(err)
            return
        self.set_values(item.values)
    
    def set_values(self, values):
        self._model.set_values(values)
        for i in range(self._model.columnCount()):
            self.resizeColumnToContents(i)
        self.sortByColumn(0, Qt.SortOrder.DescendingOrder)
        self.tableChanged.emit()

    def clear(self):
        self._model.clear()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key.Key_Enter or e.key() == Qt.Key.Key_Return:
            indexes = self.selectedIndexes()
            if indexes:
                self.value_dblclicked(indexes[0])
        super().keyPressEvent(e)

    def get_selected_rows(self) -> list:
        indexes = self.selectedIndexes()
        if not indexes:
            return []
        selected_rows = list(set(index.row() for index in indexes))
        return selected_rows

    def delete_values(self):
        while True:
            selected_rows = self.get_selected_rows()
            if not selected_rows:
                return
            self._model.removeRow(selected_rows[0])

    def value_dblclicked(self, index):
        value = self._model.get_row_value(index.row())
        if value:
            self.valueDoubleCklicked.emit(value)

    def currentChanged(self, current, previous) -> None:
        if current == previous:
            return
        value = self._model.get_row_value(current.row())
        if value:
            self.valueSelected.emit(value)

    def get_selected_values(self) -> dict:
        rows = self.get_selected_rows()
        if not rows:
            return []
        values = [self._model.get_row_value(row) for row in rows]
        return values

    def get_selected_ids(self) -> list:
        rows = self.get_selected_rows()
        if not rows:
            return []
        ids = [int(self._model.item(row).text()) for row in rows]
        return ids
    
    def get_selected_value(self) -> dict:
        selected_values = self.get_selected_values()
        if not selected_values or len(selected_values) > 1:
            error('Оберіть один елемент')
            return
        return selected_values[0]

    def values(self) -> dict:
        return self._model.values

TABLE_BUTTONS = {
    'reload':'Оновити', 
    'create':'Створити', 
    'edit':'Редагувати', 
    'copy':'Копіювати', 
    'delete':'Видалити'
    }

class DTable(QWidget):
    actionInvoked = pyqtSignal(str, dict)
    def __init__(self, data_model):
        super().__init__()
        self._table = Table(data_model)
        self.box = QVBoxLayout()
        self.box.setContentsMargins(0,0,0,0)
        self.setLayout(self.box)
        top_widget = QWidget()
        self.box.addWidget(top_widget)
        self.box.addWidget(self._table)
        self.top = QHBoxLayout()
        top_widget.setLayout(self.top)
        self.top.setContentsMargins(0,0,0,0)
        self.add_buttons()

    def reload_widget(self):
        ft = Item(self._table._model.name)
        err = ft.get_all()
        if not err:
            self._table.set_values(ft.values)
        
    def add_buttons(self, buttons=TABLE_BUTTONS):
        for b in TABLE_BUTTONS:
            if b in buttons:
                btn = QPushButton()
                btn.setIcon(QtGui.QIcon(f'images/icons/{b}.png'))
                btn.setToolTip(TABLE_BUTTONS[b])
                btn.clicked.connect(lambda _,action=b: self.action(action))
                self.top.addWidget(btn)
        self.top.addStretch()

    def action(self, action):
        # print(action)
        if action == 'create' or action == 'reload':
            self.actionInvoked.emit(action, {})
        else:
            value = self.get_selected_value()
            if not value:
                return
            self.actionInvoked.emit(action, value)

    def set_values(self, values):
        self._table.set_values(values)

    def clear(self):
        self._table.clear()

    def get_selected_rows(self) -> list:
        return self._table.get_selected_rows()

    def delete_values(self):
        self._table.delete_values()

    def get_selected_values(self) -> dict:
        return self._table.get_selected_values()

    def get_selected_ids(self) -> list:
        return self._table.get_selected_ids()
    
    def get_selected_value(self) -> dict:
        return self._table.get_selected_value()

    def values(self) -> dict:
        return self._table.values()

    
class Tree(QTreeWidget, ProtoWidget):
    valueDoubleCklicked = pyqtSignal(dict)
    itemSelected = pyqtSignal(dict)
    def __init__(self, type_name: str):
        super().__init__()
        self.name = type_name
        self.prepare_fields_and_headers()
        self.key_name = type_name + '_id'
        self.dataset = {}
        self.values = {}

        self.setColumnCount(len(self.field_names)-1)
        self.setHeaderLabels(self.headers[1:])
        header = self.header()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.currentItemChanged.connect(self.cur_changed)
        # self.itemDoubleClicked.connect(self.value_dblclicked)
        
    def set_values(self, values: list):
        self.clear()
        self.dataset = {}
        if not values:
            return
        self.values = {v['id']: v for v in values}

        for v in values:
            if v[self.key_name] not in self.dataset:
                self.dataset[v[self.key_name]] = []    
            self.dataset[v[self.key_name]].append(v['id'])
        self.add_childs(0)
    
    def add_childs(self, group_id, parent_item=None):
        for tid in self.dataset[group_id]:
            if parent_item is None:
                parent_item = self.invisibleRootItem()
            data_item = QTreeWidgetItem()
            # data_item = QTreeWidgetItem(self if parent_item is None else None)
            for i, f in enumerate(self.field_names[1:]):
                fields = self.get_fields()
                default = fields[f]['def'] if f in fields else ''
                txt = prepare_value_to_str(default, self.values[tid][f])
                data_item.setText(i, txt)
            data_item.setData(0, ID_ROLE, tid)
            # data_item.setData(1, FULL_VALUE_ROLE, td)
            if parent_item is not None:
                parent_item.addChild(data_item)
            if 'type' in self.values[tid] and self.values[tid]['type'] != self.name or tid not in self.dataset:
                continue    
            self.add_childs(tid, data_item)

    # def add_value(self, value):
    #     self.clear()
    #     if value[self.key_name] not in self.dataset:
    #         self.dataset[value[self.key_name]] = []    
    #     self.dataset[value[self.key_name]].append(value)
    #     self.add_childs(0)

    # def add_values(self, values):
    #     self.clear()
    #     for value in values:
    #         if value[self.key_name] not in self.dataset:
    #             self.dataset[value[self.key_name]] = []    
    #         self.dataset[value[self.key_name]].append(value)
    #     self.add_childs(0)

    def cur_changed(self, current, previous):
        if not current or current == previous:
            return
        id = current.data(0, ID_ROLE)
        self.itemSelected.emit(self.values[id])

    def values(self):
        return list(self.values.values())

    # def delete_current(self, id=None):
    #     cur = self.currentItem()
    #     if id is None:
    #         id = cur.data(1, FULL_VALUE_ROLE)['id']
    #     root = self.invisibleRootItem()
    #     (cur.parent() or root).removeChild(cur)
    #     for i, v in enumerate(self.dataset[0]):
    #         if v['id'] == id:
    #             break
    #     self.dataset[0].pop(i)
        
    # def value(self):
    #     i = self.currentItem()
    #     if not i:
    #         return
    #     value = i.data(1, FULL_VALUE_ROLE)
    #     return value
    
    # def set_dblclick_cb(self, cb):
    #     self.valueDoubleCklicked.connect(cb)
        
    # def remove_dblclick_cb(self):
    #     try: 
    #         self.valueDoubleCklicked.disconnect()
    #     except Exception: 
    #         pass

    # def value_dblclicked(self, index):
    #     value = self.currentItem().data(1, FULL_VALUE_ROLE)
    #     if value:
    #         self.valueDoubleCklicked.emit(value)

    # def item_by_key(self, key, value):
    #     iterator = QTreeWidgetItemIterator(self)
    #     while iterator.value():
    #         item = iterator.value()
    #         if item.data(1, FULL_VALUE_ROLE)[key] == value:
    #             return item
    #         iterator += 1

    # def set_current_id(self, id: int):
    #     item = self.item_by_key('id', id)
    #     self.setCurrentItem(item)
    #     self.scrollToItem(item)

    # def delete_by_id(self, id):
    #     item = self.item_by_key('id', id)
    #     if not item:
    #         return
    #     root = self.invisibleRootItem()
    #     (item.parent() or root).removeChild(item)
    #     for i, v in enumerate(self.dataset[0]):
    #         if v['id'] == id:
    #             break
    #     self.dataset[0].pop(i)

    # def get_selected_value(self):
    #     value = self.value()
    #     if not value:
    #         error('Оберіть один елемент')
    #         return
    #     return value


class ComboBoxDictSelector(QWidget):
    selectionChanged = pyqtSignal(str)

    def __init__(self, 
                 title: str = '', 
                 values: dict = {}, 
                 title_key = 'name'
                 ):
        super().__init__()
        self.title_key = title_key
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        self.caption = 'Не обрано'
        if title:
            # layout.addWidget(QLabel(title))
            self.caption = title
        self.cb = QComboBox()
        layout.addWidget(self.cb)
        self.cb.currentIndexChanged.connect(self.selection_changed)
        if values:
            self.reload(values)
        
    def reload(self, values: dict):    
        self.values = values
        self.keys = list(values.keys())
        self.cb.clear()
        self.cb.addItem(self.caption, '_')
        for k in self.keys:
            self.cb.addItem(values[k][self.title_key], k)
        self.keys = ['_',] + self.keys
        
    def selection_changed(self, index: int):
        self.selectionChanged.emit(self.keys[index])

    def value(self):
        return self.keys[self.cb.currentIndex()]
    
    def set_current_id(self, id):
        for i, k in enumerate(self.keys):
            if k == id:
                self.cb.setCurrentIndex(i)