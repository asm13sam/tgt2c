from PyQt6.QtCore import (
    Qt,
    QDate,
    pyqtSignal,
    QEvent,
    QModelIndex,
    )
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
    )

from dialogs import error, CustomDialog
from widgets import ProtoWidget, Table, TableModel
from model import Item


class CustomForm(QWidget, ProtoWidget):
    formChanged = pyqtSignal(bool)
    saveRequested = pyqtSignal(dict)
    def __init__(self, type_name: str):
        super().__init__()
        self.name = type_name
        self.value = {}
        self.widgets = {}
        self.labels = {}
        self.fields = list(self.get_fields().keys())
        self.headers = [v['hum'] for v in self.hum[self.name]['fields'].values()]

        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.setContentsMargins(0, 0, 0, 0)
        
        # form_names_color = self.colors['form_names_color'] if 'form_names_color' in self.colors else 'lightgreen'
        form_names_color = 'lightgreen'
        self.setStyleSheet(f'color: {form_names_color}; padding: 0px;')
        
        rows = self.create_widgets()
        self.save_but = QPushButton("Зберегти")
        self.grid.addWidget(self.save_but, rows+1, 1)
        self.save_but.clicked.connect(self.get_value)
        self.is_changed = False

    def set_value(self, value: dict):
        self.value = value
        for k, w in self.widgets.items():
            if k.endswith('_id'):
                w.setValue({'id':value[k], 'name':value[k[:-3]]})
                continue    
            w.setValue(value[k])
        self.set_changed(False)
    
    def hide_save_btn(self):
        self.save_but.setVisible(False)

    def set_changed(self, changed=True):
        if changed == self.is_changed:
            return
        self.is_changed = changed
        self.formChanged.emit(changed)

    def changed(self):
        return self.is_changed

    def create_widgets(self):
        # form_values_color = self.colors['form_values_color'] if 'form_values_color' in self.colors else 'yellow'
        # form_bg_color = self.colors['form_bg_color'] if 'form_bg_color' in self.colors else 'black'
        form_values_color = 'yellow'
        form_bg_color = 'black'
        align = Qt.AlignmentFlag.AlignRight
        row, n = 0, 0
        fields_num = len(self.fields)
        fields_dict = self.get_fields()
        while n < fields_num:
            field = self.fields[n]
            header = self.headers[n]
            default = fields_dict[field]['def']
            td = type(default)
            self.labels[field] = QLabel(header)
            if field == 'id':
                w = LabelWidget()
            elif field.endswith('_id'):
                w = SelectorWidget(field[:-3])
            elif td == int:
                w = IntWidget()
            elif td == float:
                w = DoubleWidget()
            elif td == bool:
                w = CheckWidget()
            else:
                w = LineEditWidget()
            w.valChanged.connect(self.set_changed)
            w.setStyleSheet(f'color:{form_values_color}; padding: 2px; background-color: {form_bg_color};')
            self.widgets[field] = w
            self.grid.addWidget(self.labels[field], row, 0, align)
            self.grid.addWidget(self.widgets[field], row, 1)
            row += 1
            n += 1
            
        self.grid.addWidget(QLabel(''), row, 0)
        self.grid.setRowStretch(row, 10)
        return row

    def get_value(self):
        for k in self.widgets:
            # print(k, type(self.widgets[k]))
            v = self.widgets[k].value()
            # check if value set
            self.value[k] = v
        self.saveRequested.emit(self.value)
        return True


class SelectorWidget(QPushButton, ProtoWidget):
    valChanged = pyqtSignal()
    def __init__(self, type_name: str):
        self.name = type_name
        self.title = self.hum[type_name]['hum']
        self.full_value = {}
        super().__init__("Оберіть")
        self.clicked.connect(self.dialog)

    def dialog(self):
        item = Item(self.name)
        m = TableModel(self.name)
        w = Table(m)
        err = item.get_all()
        if err:
            error(err)
            return
        w.set_values(item.values)
        dlg = CustomDialog(w, f'Оберіть {self.title}')
        res = dlg.exec()
        if res:
            self.setValue(dlg.result)

    def setValue(self, value: dict):
        self.full_value = value
        self.setText(value['name'])
        self.valChanged.emit()

    def set_value(self, value: dict):
        self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(False)

    def value(self) -> str:
        return self.full_value['id']


class DoubleWidget(QDoubleSpinBox):
    valChanged = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setRange(-100000000.0, 100000000.0)
        self.valueChanged.connect(lambda: self.valChanged.emit())

    def setValue(self, val: float) -> None:
        val = round(val, 2)
        return super().setValue(val)

    def set_value(self, value):
        self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(False)

    def value(self) -> float:
        val = super().value()
        return round(val, 2)
    

class LineEditWidget(QLineEdit):
    valChanged = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.textChanged.connect(lambda: self.valChanged.emit())

    def setValue(self, value: str):
        self.setText(value)

    def set_value(self, value: str):
        self.blockSignals(True)
        self.setText(value)
        self.blockSignals(False)

    def value(self) -> str:
        return self.text()


class IntWidget(QSpinBox):
    valChanged = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setRange(-1000000000, 1000000000)
        self.valueChanged.connect(lambda: self.valChanged.emit())

    def set_value(self, value: int):
        self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(False)
    
class LabelWidget(QLabel):
    valChanged = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.id = 0

    def setValue(self, value: int):
        self.id = value
        self.setText(str(value))

    def set_value(self, value: int):
        self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(False)
    
    def value(self):
        return self.id


class CheckWidget(QCheckBox):
    valChanged = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.stateChanged.connect(lambda: self.valChanged.emit())

    def setValue(self, value: bool):
        self.setCheckState(Qt.CheckState.Checked if value else Qt.CheckState.Unchecked)

    def set_value(self, value: bool):
        self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(False)

    def value(self):
        return self.checkState() == Qt.CheckState.Checked
