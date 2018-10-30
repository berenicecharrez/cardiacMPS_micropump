import sys
import time
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QWidget, QToolTip, QHBoxLayout, QVBoxLayout,
    QPushButton, QApplication, QMessageBox, QMainWindow, QAction, qApp, QMenu, QLabel, QLineEdit,
    QTextEdit, QGridLayout, QSlider, QLCDNumber, QComboBox)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtCore import QDate, QTime, QEvent
from multiprocessing import Process
from test_oli import main_process

# TODO: add degassing valve option
# put all valves to close when start

"""
print(time.time())
now = QDateTime.currentDateTime()
time2 = QTime.currentTime()

print(time2.toString(Qt.DefaultLocaleLongDate))
#universal time with the toUTC() method from the date time object
print("Universal datetime: ", now.toUTC().toString(Qt.ISODate))
#difference between universal time and local time in seconds
print("The offset from UTC is: {0} seconds".format(now.offsetFromUtc()))
"""
def formatActionParam (ac_type, ac_min, ac_sec, t_start, valve_number = None, valve_option = None):
    ret = {}

    ret['type'] = ac_type
    ret['minutes'] = ac_min
    ret['seconds'] = ac_sec
    ret['start'] = t_start
    ret['valve number'] = valve_number
    ret['valve option'] = valve_option

    return ret

def formatDict (listAction):
    aux = ''

    for _name, _list_param in listAction.items():

        if _list_param['valve option'] == None:

            aux += '{0}: {1} for a duration of {2} [min] {3} [sec], starting at {4} [sec]\n'.format(_name, _list_param['type'],
                _list_param['minutes'], _list_param['seconds'], _list_param['start'])

        else:
            aux += '{0}: {1} -->  There will be {2} of Valve # {3} for a duration of {4} [min] {5} [sec], starting at {6} [sec]\n'.format(_name, _list_param['type'],
                _list_param['valve option'], _list_param['valve number'], _list_param['minutes'], _list_param['seconds'], _list_param['start'])

    return aux

class Action(QMainWindow, QWidget):

    def __init__(self):
        super().__init__()

        # Class member
        self.ac_name_obj = None
        self.ac_type_obj = None
        self.ac_duration_min_obj = None
        self.ac_duration_sec_obj = None
        self.valve_number_obj = None
        self.valve_option_action_obj = None
        self.t_start_obj = None

        self.ActionDisplay = ''

        self.ListAction = {} #dictionary

        #default dictionary
        self.ListAction["OPEN"] = formatActionParam ('VALVE_ACTION', 0, 20, 0, 4, 'OPENING')
        self.ListAction["PUMP"] = formatActionParam ('PUMP', 0, 16, 5, 0, 'NO_VALVE')
        self.ListAction["CLOSE"] = formatActionParam ('VALVE_ACTION', 0, 5, 20, 4, 'CLOSING')

        self.wid = QWidget()
        self.time_setup = None

        self.initUI() #creation of the GUI


    def initUI(self):

#Layout: You need to create a QWidget and set it as the central widget on the QMainWindow and assign the QLayout to th

        #wid = QWidget(self)
        self.setCentralWidget(self.wid)

        QToolTip.setFont(QFont('SansSerif', 10))

#labels

        AcName = QLabel('Action Name', self)
        AcNameEdit = QLineEdit()
        self.ac_name_obj = AcNameEdit

        AcType = QLabel('Action Type', self)
        AcTypes = ['PUMPING', 'VALVE ACTION']
        # Create and fill the combo box to choose the tyoe of action
        AcTypeBox = QComboBox()
        AcTypeBox.addItems(AcTypes)
        self.ac_type_obj = AcTypeBox

        #minutes
        AcDurationMin = QLabel('Action Duration [min]', self)
        AcDurationLCDMin = QLCDNumber()
        AcDurationLCDMin.setSegmentStyle(QLCDNumber.Flat)

        #change color of LCD, not working
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(170, 255, 0))
        palette.setColor(QPalette.Base, QColor(170, 255, 0))
        palette.setColor(QPalette.AlternateBase, QColor(170, 255, 0))
        AcDurationLCDMin.setPalette(palette)

        sliderAcDurMin = QSlider(Qt.Horizontal, self)
        sliderAcDurMin.setMaximum(60)
        sliderAcDurMin.valueChanged.connect(AcDurationLCDMin.display)
        self.ac_duration_min_obj = sliderAcDurMin

        #seconds
        AcDurationSec = QLabel('[sec]', self)
        AcDurationLCDSec = QLCDNumber()
        AcDurationLCDSec.setSegmentStyle(QLCDNumber.Flat)

        sliderAcDurSec = QSlider(Qt.Horizontal, self)
        sliderAcDurSec.setMaximum(60)
        sliderAcDurSec.valueChanged.connect(AcDurationLCDSec.display)
        self.ac_duration_sec_obj = sliderAcDurSec

        #tStart
        TStart = QLabel('Time Start [sec]', self)
        TStartEdit = QLineEdit()
        self.t_start_obj = TStartEdit

        #valve options
        IfValve = QLabel('If Action type is "Valve" ONLY, select options below. \n' 'Keep the Valve number at 0 if PUMPNG selected',self)

        ValveOption = QLabel('Valve Option')
        ValveOptions = ['NO VALVE','OPENING', 'CLOSING']
        ValveOptionBox = QComboBox()
        ValveOptionBox.addItems(ValveOptions)
        self.valve_option_action_obj = ValveOptionBox

        ValveNumber = QLabel('Valve Number', self)
        ValveNumberLCD = QLCDNumber()
        ValveNumberLCD.setSegmentStyle(QLCDNumber.Flat)
        sliderValveNumber = QSlider(Qt.Horizontal, self)
        sliderValveNumber.setMaximum(24)
        sliderValveNumber.valueChanged.connect(ValveNumberLCD.display)
        self.valve_number_obj = sliderValveNumber

#Valve action list

        AcList = QLabel('Action list', self)
        AcListEdit = QTextEdit()
        AcListEdit.autoFormatting ()
        self.ActionDisplay = AcListEdit

#valve option button
        Valvebtn = QPushButton('Add Action', self)
        Valvebtn.clicked.connect(self.AddAction)
        Valvebtn.resize(Valvebtn.sizeHint())

#quit button

        qbtn = QPushButton('Quit', self) #second parameter is the parent widget
        qbtn.clicked.connect(self.closeEvent)
        #qbtn.clicked.connect(QApplication.instance().quit)
        #btn.setToolTip('This is a <b>QPushButton</b> widget') --> text when pointing at the button
        qbtn.resize(qbtn.sizeHint()) #recommended size for the button
        #qbtn.move(1600, 900) #position in absolute position

#next button

        nextbtn = QPushButton('Next', self) #second parameter is the parent widget
        nextbtn.clicked.connect(self.GoToNext)
        nextbtn.resize(nextbtn.sizeHint()) #recommended size for the butto


#grid Layout

        grid = QGridLayout()

        grid.addWidget(AcName, 1, 0)
        grid.addWidget(AcNameEdit, 1, 1)

        grid.addWidget(AcType, 2, 0)
        grid.addWidget(AcTypeBox, 2, 1)

        grid.addWidget(AcDurationMin, 3, 0)
        grid.addWidget(AcDurationLCDMin, 3, 1)
        grid.addWidget(sliderAcDurMin, 3, 2)

        grid.addWidget(AcDurationSec, 3, 3)
        grid.addWidget(AcDurationLCDSec, 3, 4)
        grid.addWidget(sliderAcDurSec, 3, 5)

        grid.addWidget(TStart, 4, 0)
        grid.addWidget(TStartEdit, 4, 1)

        grid.addWidget(IfValve, 5, 0)

        grid.addWidget(ValveOption,6, 0 )
        grid.addWidget(ValveOptionBox, 6, 1)
        grid.addWidget(ValveNumber, 6, 2)
        grid.addWidget(ValveNumberLCD, 6, 3)
        grid.addWidget(sliderValveNumber, 6, 4)

        grid.addWidget(AcList, 8, 0)
        grid.addWidget(AcListEdit, 8, 1, 1, 4)

        grid.addWidget(Valvebtn, 7, 1)
        grid.addWidget(qbtn, 10, 7)
        grid.addWidget(nextbtn, 9, 1)

        #print(sliderAcDur.value())

        for i in range(0, 6):
            grid.setColumnStretch(i, 1)
            grid.setRowStretch(i, 1)
            grid.setSpacing (1)
            grid.setHorizontalSpacing (1)
            grid.setVerticalSpacing (1)

        self.wid.setLayout(grid)

#menu bar

        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(exitAct)

#submenu

        impMenu = QMenu('Import', self)
        impAct = QAction('Import mail', self)
        impMenu.addAction(impAct)

        newAct = QAction('New', self)

        fileMenu.addAction(newAct)
        fileMenu.addMenu(impMenu)

#window geometry
        self.setGeometry(0, 0, 1800, 1000) # x start, y start, x length, y length
        self.setWindowTitle('Micropump GUI _ Action')
        #self.show()

#message box
    def closeEvent(self):

        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.close()

#Valve options
    def AddAction (self):

        ac_name = self.ac_name_obj.text()
        ac_type = self.ac_type_obj.currentText()
        valve_option = self.valve_option_action_obj.currentText()
        valve_number = self.valve_number_obj.value()
        ac_min = self.ac_duration_min_obj.value()
        ac_sec = self.ac_duration_sec_obj.value()
        t_start = self.t_start_obj.text()

        try:
            t_start = int(t_start)

            if valve_option == 'NO VALVE':
                valve_option = None
                valve_number = None

            self.ListAction[self.ac_name_obj.text()] = formatActionParam (ac_type, ac_min, ac_sec, t_start, valve_number, valve_option)
            self.ActionDisplay.setText(formatDict(self.ListAction))

        except ValueError:
            error = QMessageBox()
            error.setText("Please enter a number for Time Start")
            error.exec_()

#if press Next button go to next window for time setup
    def GoToNext (self):

        reply = QMessageBox.question(self, 'Message',
            'Are you sure all your actions are correctly inserted? \n'
            'To modify values to an action, keep the same name, it will automatically update values', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.NewWindow()

        # TODO: send data through ??? to the RaspBerry Pi

#if press ESC button it terminates
    def keyPressEvent(self, e):

        if e.key() == Qt.Key_Escape:
            self.close()

    def NewWindow(self):
        #action = Action()
        #action.close()
        self.time_setup = TimeSetup(self.ListAction)
        self.time_setup.show()
#------------------------------------------------------------------------------------

class TimeSetup(QMainWindow, QWidget):

    def __init__(self, set_action):
        super().__init__()

        self.wid2 = QWidget()
        self.ActionDisplay2 = ''
        self.set_action = set_action
        self.process_trigger_event = None
        self.initUI2() #creation of the GUI

    def initUI2(self):

        self.setCentralWidget(self.wid2)
        QToolTip.setFont(QFont('SansSerif', 10))

#Valve action list

        AcSummary = QLabel('Action Summary', self)
        AcSummaryEdit = QTextEdit()
        AcSummaryEdit.autoFormatting ()
        self.ActionDisplay2 = AcSummaryEdit
        self.ActionDisplay2.setText(formatDict(self.set_action))

#quit button

        quitbtn = QPushButton('Quit2', self) #second parameter is the parent widget
        quitbtn.clicked.connect(self.closeEvent2)
        quitbtn.resize(quitbtn.sizeHint()) #recommended size for the button

#start button
        startbtn = QPushButton('START', self) #second parameter is the parent widget
        startbtn.clicked.connect(self.startEvent)
        startbtn.resize(startbtn.sizeHint()) #recommended size for the button

#stop button
        stopbtn = QPushButton('STOP', self) #second parameter is the parent widget
        stopbtn.clicked.connect(self.stopEvent)
        stopbtn.resize(stopbtn.sizeHint()) #recommended size for the button

#grid Layout

        grid = QGridLayout()

        grid.addWidget(AcSummary, 1, 0)
        grid.addWidget(AcSummaryEdit, 1, 1)
        grid.addWidget(quitbtn, 5, 4)
        grid.addWidget(startbtn, 4, 2)
        grid.addWidget(stopbtn, 4, 3)

        self.wid2.setLayout(grid)

#window geometry
        self.setGeometry(0, 0, 900, 500) # x start, y start, x length, y length
        self.setWindowTitle('Time Setup Window')

#message box
    def closeEvent2(self):

        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit window 2 ?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.close()

    def startEvent(self):
        print ('STARTING...')
        self.process_trigger_event = Process(target = main_process, args = (self.set_action,))
        self.process_trigger_event.start()

    def stopEvent(self):
        print('STOPPING')
        self.process_trigger_event.terminate()

if __name__ == '__main__':

    app = QApplication(sys.argv)

    action = Action()
    action.show()

    sys.exit(app.exec_())
