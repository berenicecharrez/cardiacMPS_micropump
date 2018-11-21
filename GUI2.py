import sys
import time
import heapq
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
# add timestep as input
#make look nicer


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
def formatActionParam (ac_type, ac_min, ac_sec, t_start, valve_number = None):#, valve_option = None):
    ret = {}

    ret['type'] = ac_type
    ret['minutes'] = ac_min
    ret['seconds'] = ac_sec
    ret['start'] = t_start
    ret['valve number'] = valve_number
    #ret['valve option'] = valve_option

    return ret

def formatDict (listAction, bond_duration):
    aux = 'Bond Duration is of {} hours\n'.format(bond_duration)

    for _name, _list_param in listAction.items():

        if _list_param['type'] == 'PUMP':

            aux += '{0}: {1} for a duration of {2} [min] {3} [sec], starting at {4} [sec]\n'.format(_name, _list_param['type'],
                _list_param['minutes'], _list_param['seconds'], _list_param['start'])

        else:
            aux += '{0}: {1} -->  There will be opening of Valve # {2} for a duration of {3} [min] {4} [sec], starting at {5} [sec]\n'.format(_name, _list_param['type'], \
            _list_param['valve number'], _list_param['minutes'], _list_param['seconds'], _list_param['start'])

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
        #self.valve_option_action_obj = None
        self.t_start_obj = None
        self.bond_duration_obj = None


        self.ActionDisplay = ''

        self.ListAction = {} #dictionary

        #default dictionary
        #self.ListAction["OPEN"] = formatActionParam ('VALVE_ACTION', 0, 20, 0, 4)#, 'OPENING')
        #self.ListAction["PUMP"] = formatActionParam ('PUMP', 0, 16, 5, 0)#, 'NO_VALVE')
        #self.ListAction["OPEN2"] = formatActionParam ('VALVE_ACTION', 0, 20, 10, 17)#, 'OPENING')

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
        AcTypes = ['PUMP', 'VALVE ACTION']
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
        """IfValve = QLabel('If Action type is "Valve" ONLY, select options below. \n' 'Keep the Valve number at 0 if PUMPNG selected',self)

        ValveOption = QLabel('Valve Option')
        ValveOptions = ['NO VALVE','OPENING', 'CLOSING']
        ValveOptionBox = QComboBox()
        ValveOptionBox.addItems(ValveOptions)
        self.valve_option_action_obj = ValveOptionBox
        """
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

#chip bonding button
        Bondingbtn = QPushButton('Chip Bonding', self)
        Bondingbtn.clicked.connect(self.chip_bonding)
        Bondingbtn.resize(Bondingbtn.sizeHint())

#bonding duration
        BondDuration = QLabel('Bond Duration [h]', self)
        BondDurationEdit = QLineEdit()
        self.bond_duration_obj = BondDurationEdit

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

        #grid.addWidget(IfValve, 5, 0)

        #grid.addWidget(ValveOption,6, 0 )
        #grid.addWidget(ValveOptionBox, 6, 1)
        grid.addWidget(ValveNumber, 6, 2)
        grid.addWidget(ValveNumberLCD, 6, 3)
        grid.addWidget(sliderValveNumber, 6, 4)

        grid.addWidget(Bondingbtn, 8, 3)
        grid.addWidget(BondDuration, 8, 1)
        grid.addWidget(BondDurationEdit, 8, 2)

        grid.addWidget(AcList, 9, 0)
        grid.addWidget(AcListEdit, 9, 1, 1, 4)

        grid.addWidget(Valvebtn, 7, 1)
        grid.addWidget(qbtn, 11, 7)
        grid.addWidget(nextbtn, 10, 1)


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
        #valve_option = self.valve_option_action_obj.currentText()
        valve_number = self.valve_number_obj.value()
        ac_min = self.ac_duration_min_obj.value()
        ac_sec = self.ac_duration_sec_obj.value()
        t_start = self.t_start_obj.text()
        bondTime = self.bond_duration_obj.text()

        try:
            t_start = int(t_start)
            bondTime = int(bondTime)
            """if valve_option == 'NO VALVE':
                valve_option = None
                valve_number = None
            """
            self.ListAction[self.ac_name_obj.text()] = formatActionParam (ac_type, ac_min, ac_sec, t_start, valve_number)#, valve_option)
            self.ActionDisplay.setText(formatDict(self.ListAction, bondTime))

        except ValueError:
            error = QMessageBox()
            error.setText("Please enter a number for Time Start or 0 for chip bonding time")
            error.exec_()

    def chip_bonding(self):

        bond_duration = self.bond_duration_obj.text()
        bondMin = int(bond_duration)#int(bond_duration*60)

        print('called chip bonding')

        self.ListAction["PUMP"] = formatActionParam ('PUMP', 0, 25, 0, 0)    #pump starting at 0 for 25[sec]

        self.ListAction["I1"] = formatActionParam ('VALVE ACTION', 0, 3, 0, 17) #ac_type, ac_min, ac_sec, t_start, valve_number = None
        self.ListAction["O1"] = formatActionParam ('VALVE ACTION', 0, 3, 3, 6)
        self.ListAction["O2"] = formatActionParam ('VALVE ACTION', 0, 3, 3, 13)
        self.ListAction["I2"] = formatActionParam ('VALVE ACTION', 0, 3, 6, 4)
        self.ListAction["O3"] = formatActionParam ('VALVE ACTION', 0, 3, 9, 19)
        self.ListAction["O4"] = formatActionParam ('VALVE ACTION', 0, 3, 9, 12)
        self.ListAction["I3"] = formatActionParam ('VALVE ACTION', 0, 3, 12, 27)
        self.ListAction["O5"] = formatActionParam ('VALVE ACTION', 0, 3, 15, 14)
        self.ListAction["O6"] = formatActionParam ('VALVE ACTION', 0, 3, 15, 15)
        self.ListAction["I4"] = formatActionParam ('VALVE ACTION', 0, 3, 18, 22)
        self.ListAction["O7"] = formatActionParam ('VALVE ACTION', 0, 3, 21, 18)
        self.ListAction["O8"] = formatActionParam ('VALVE ACTION', 0, 3, 21, 23)
        self.ListAction["SLEEP"] = formatActionParam ('VALVE ACTION', 0, 35, 25, 0)

        #time.sleep(35)

        self.ActionDisplay.setText(formatDict(self.ListAction, bond_duration))

        for i in range (1, bondMin):
            #print(i)
            #print('BondSetAction2: {}'.format(self.ListAction))
            self.ListAction["PUMP, round{}".format(i)] = formatActionParam ('PUMP', 0, 25+i*60, 0+i*60, 0)    #pump starting at 0 for 25[sec]

            self.ListAction["I1, round{}".format(i)] = formatActionParam ('VALVE ACTION', 0, 3+i*60, 0+i*60, 17) #ac_type, ac_min, ac_sec, t_start, valve_number = None
            self.ListAction["O1, round{}".format(i)] = formatActionParam ('VALVE ACTION', 0, 3+i*60, 3+i*60, 6)
            self.ListAction["O2, round{}".format(i)] = formatActionParam ('VALVE ACTION', 0, 3+i*60, 3+i*60, 13)
            self.ListAction["I2, round{}".format(i)] = formatActionParam ('VALVE ACTION', 0, 3+i*60, 6+i*60, 4)
            self.ListAction["O3, round{}".format(i)] = formatActionParam ('VALVE ACTION', 0, 3+i*60, 9+i*60, 19)
            self.ListAction["O4, round{}".format(i)] = formatActionParam ('VALVE ACTION', 0, 3+i*60, 9+i*60, 12)
            self.ListAction["I3, round{}".format(i)] = formatActionParam ('VALVE ACTION', 0, 3+i*60, 12+i*60, 27)
            self.ListAction["O5, round{}".format(i)] = formatActionParam ('VALVE ACTION', 0, 3+i*60, 15+i*60, 14)
            self.ListAction["O6, round{}".format(i)] = formatActionParam ('VALVE ACTION', 0, 3+i*60, 15+i*60, 15)
            self.ListAction["I4, round{}".format(i)] = formatActionParam ('VALVE ACTION', 0, 3+i*60, 18+i*60, 22)
            self.ListAction["O7, round{}".format(i)] = formatActionParam ('VALVE ACTION', 0, 3+i*60, 21+i*60, 18)
            self.ListAction["O8, round{}".format(i)] = formatActionParam ('VALVE ACTION', 0, 3+i*60, 21+i*60, 23)

            self.ListAction["SLEEP, round{}".format(i)] = formatActionParam ('VALVE ACTION', 0, 35+i*60, 25+i*60, 0)

            i=i+1
            #print(self.ListAction)

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
        self.time_setup = TimeSetup(self.ListAction, self.bond_duration_obj)
        self.time_setup.show()
#------------------------------------------------------------------------------------

class TimeSetup(QMainWindow, QWidget):

    def __init__(self, set_action, bond_duration):
        super().__init__()

        self.wid2 = QWidget()
        self.ActionDisplay2 = ''
        self.set_action = set_action
        #self.BondSet_action = {}
        self.process_trigger_event = None
        self.bond_duration_obj2 = bond_duration.text()
        self.initUI2() #creation of the GUI

    def initUI2(self):

        self.setCentralWidget(self.wid2)
        QToolTip.setFont(QFont('SansSerif', 10))

#Valve action list

        AcSummary = QLabel('Action Summary', self)
        AcSummaryEdit = QTextEdit()
        AcSummaryEdit.autoFormatting ()
        self.ActionDisplay2 = AcSummaryEdit
        self.ActionDisplay2.setText(formatDict(self.set_action, self.bond_duration_obj2))

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
#start event

    def startEvent(self):
        print ('STARTING...')
        bondTime = float(self.bond_duration_obj2)
        #try:

        print('bondtime:{} hours'.format(bondTime))
        time_init = time.time()
        time_current = time.time() - time_init

        self.process_trigger_event = Process(target = main_process, args = (self.set_action,))
        self.process_trigger_event.start()

#        if bondTime != 0:
#            round = 0
#            while time_current < bondTime*2*60*60:
#                #time_current = time.time() - time_init
#                print('time current before round: {}'.format(time_current))
#                print('bondtime:{}'.format(bondTime*60))
#                self.process_trigger_event = Process(target = main_process, args = (self.set_action,))
#                self.process_trigger_event.start()


#                time.sleep(35)
#                print('round {} finished'.format(round))
#                time_current = time.time() - time_init
#                print('time current after round: {}'.format(time_current))
#                round= round+1

            #self.stopEvent()
            #self.process_trigger_event.terminate()

#        elif bondTime == 0:
#            print('bondtime is 0')
#            self.process_trigger_event = Process(target = main_process, args = (self.set_action,))
#           self.process_trigger_event.start()


    #self.process_trigger_event.terminate()
    #self.close()

        #except ValueError:
        #    error = QMessageBox()
        #    error.setText("Please enter a number for chip bonding time")
        #    error.exec_()

#stop event

    def stopEvent(self):
        print('STOPPING')
        self.process_trigger_event.terminate()
        #closeEvent()
        self.closeEvent2()

if __name__ == '__main__':

    app = QApplication(sys.argv)

    action = Action()
    action.show()

    sys.exit(app.exec_())
