from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QApplication,
    QTabWidget,
    )
from PyQt6.QtGui import QKeySequence, QShortcut, QFont

import sys
import qdarktheme

from widgets import Info, Table, Tree, TableModel, DTable
from model import Item
from form import CustomForm
from dialogs import error


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таргет")
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.tabs = QTabWidget()
        self.vbox.addWidget(self.tabs, stretch=10)
        self.tabs.currentChanged.connect(self.reload_tab)
     

        info = Info('measure')
        measure = Item('measure')
        err = measure.get(1)
        if not err:
            info.set_value(measure.value)
        self.tabs.addTab(info, 'Одиниця виміру')

        mes_tbl_model = TableModel('measure')
        mes_tbl = DTable(mes_tbl_model)
        err = measure.get_all()
        if not err:
            mes_tbl.set_values(measure.values)
        self.tabs.addTab(mes_tbl, 'Одиниці виміру')
        mes_tbl.actionInvoked.connect(lambda action, value, item=measure: self.action(item, value, action))

        mg_form = CustomForm('matherial_group')
        mg = Item('matherial_group')
        err = mg.get(3)
        if not err:
            mg_form.set_value(mg.value)
        self.tabs.addTab(mg_form, 'Форма Група матеріалів')
        mg_form.saveRequested.connect(lambda value, item=mg: self.save_form(item, value))

        me_form = CustomForm('measure')
        me = Item('measure')
        err = me.get(5)
        if not err:
            me_form.set_value(me.value)
        self.tabs.addTab(me_form, 'Форма Me')
        me_form.saveRequested.connect(lambda value, item=me: self.save_form(item, value))

       
        mg_table = Table(TableModel('matherial_group'))
        err = mg.get_all()
        if not err:
            mg_table.set_values(mg.values)
        self.tabs.addTab(mg_table, 'Група матеріалів')

        mg_tree = Tree('matherial_group')
        mg_tree.set_values(mg.values)
        self.tabs.addTab(mg_tree, 'Група матеріалів')

        mg_info = Info('matherial_group')
        mg1 = Item('matherial_group')
        err = mg1.get(3)
        if not err:
            mg_info.set_value(mg1.value)
        self.tabs.addTab(mg_info, 'Група матеріалів')

        mat_info = Info('matherial')
        mat = Item('matherial')
        err = mat.get(3)
        if not err:
            mat_info.set_value(mat.value)
        self.tabs.addTab(mat_info, 'Матеріал')

        mat_form = CustomForm('matherial')
        err = mat.get(5)
        if not err:
            mat_form.set_value(mat.value)
        self.tabs.addTab(mat_form, 'Форма Mat')
        mat_form.saveRequested.connect(lambda value, item=mat: self.save_form(item, value))


    def save_form(self, item, value):
        item.value = value
        err = item.create()
        if err:
            error(err)
            return
        print(item.value)

    def reload_tab(self, index):
        w = self.tabs.widget(index)
        w.reload_widget()

    def action(self, item, value, action):
        item.value = value
        if action == 'delete':
            err = item.delete(value['id'])
            if err:
                error(err)
                return
            print(item.name, 'deleted')

        
    

class MainWindow():
    def __init__(self):
        self.qt_app = QApplication(sys.argv)
        self.window = Window()
        color = "#99BCBC"
        qss = """
        QToolTip {
            background-color: black;
            color: white;
            border: black solid 1px
                }
        """
        qdarktheme.setup_theme(custom_colors={'primary': color}, additional_qss=qss)
        font = QFont()
        QApplication.instance().setFont(font)
        font.setPointSize(10)

    def run(self):
        self.window.show()
        sys.exit(self.qt_app.exec())
