import sys
import time
import heapq
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QToolTip, QHBoxLayout, QVBoxLayout, \
        QPushButton, QApplication, QMessageBox, QMainWindow, QAction, \
        qApp, QMenu, QLabel, QLineEdit, QTextEdit, QGridLayout, QSlider, \
        QLCDNumber, QComboBox
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtCore import QDate, QTime, QEvent
from multiprocessing import Process
from test_oli import main_process

# TODO: add degassing valve option
# add timestep as input
# make look nicer


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
def formatActionParam (ac_type, ac_min, ac_sec, t_start, valve_number = None):
    #, valve_option = None):
    ret = {}

    ret['type'] = ac_type
    ret['minutes'] = ac_min
    ret['seconds'] = ac_sec
    ret['start'] = t_start
    ret['valve number'] = valve_number
    #ret['valve option'] = valve_option

    return ret

def formatDict (listAction, bond_duration):
    aux = "Bond Duration is of {} hours\n".format(bond_duration)

    for _name, _list_param in listAction.items():

        # explanation: use short local names: better readability,
        # and you'll use less time typing them out

        _type, _min, _sec, _start = \
                _list_param["type"], _list_param["minutes"], \
                _list_param["seconds"], list_param["start"]

        # explanation: try to split operations if they go over multiple
        # lines (max widht 80), and to find common factors you can pull 
        # outside any if test, for loop, etc

        aux += "{0}: {1} ".format(_name, _list_param["type"])

        if _list_param['type'] == 'PUMP':
            aux += "for a duration of {2} [min] {3} [sec]".format(_min, _sec)
        else:
            _valno = _list_param["valve number"]
            aux += "-->  There will be opening of Valve # {2} ".format(_valno)
            aux += "for a duration of {3} [min] {4} [sec]".format(_min, _sec)
        aux += ", starting at {4} [sec]\n".format(_start)

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

        # explanation: variables starts with lower case, by convention

        self.actionDisplay = ''

        self.listAction = {} #dictionary

        #default dictionary
        #self.listAction["OPEN"] = formatActionParam ('VALVE_ACTION', \
                #0, 20, 0, 4)#, 'OPENING')
        #self.listAction["PUMP"] = formatActionParam ('PUMP', \
                #0, 16, 5, 0)#, 'NO_VALVE')
        #self.listAction["OPEN2"] = formatActionParam ('VALVE_ACTION', \
                #0, 20, 10, 17)#, 'OPENING')

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
        self.actionDisplay = AcListEdit

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
            self.listAction[self.ac_name_obj.text()] = formatActionParam (ac_type, ac_min, ac_sec, t_start, valve_number)#, valve_option)
            self.actionDisplay.setText(formatDict(self.listAction, bondTime))

        except ValueError:
            error = QMessageBox()
            error.setText("Please enter a number for Time Start or 0 for chip bonding time")
            error.exec_()

    def chip_bonding(self):

        bond_duration = self.bond_duration_obj.text()
        bondMin = int(bond_duration)#int(bond_duration*60)

        print('called chip bonding')
        
        # explanation: repetative operation --> for loop

        keys = ["PUMP", "I1", "O1", "O2", "I2", "O3", "O4", "I3", "O5", \
                "O6", "I4", "O7", "O8", "SLEEP"]
        actions = ["PUMP"] + 13*["VALVE_ACTION"]
        ac_mins = [0]*14
        ac_secs = [25] + 12*[3] + [35]
        t_starts = [0, 0, 3, 3, 6, 9, 9, 12, 15, 15, 18, 21, 21, 25]
        valve_numbers = [0, 17, 6, 13, 4, 19, 12, 27, 14, 15, 22, 18, 23, 0]
        ac_min, ac_sec = 0, 3
        
        for (key, action, ac_min, ac_sec, t_start, valve_number) in \
                zip(keys, actions, ac_mins, ac_secs, t_starts, valve_numbers):
            self.listAction(key) = formatActionParam(action, ac_min,
                    ac_sec, t_start, valve_number)
        
        #time.sleep(35)

        self.actionDisplay.setText(formatDict(self.listAction, bond_duration))

        for i in range (1, bondMin):
            #print(i)
            #print('BondSetAction2: {}'.format(self.listAction))
            
            for (key, action, ac_min, ac_sec, t_start, valve_number) in \
                    zip(keys, actions, ac_mins, ac_secs, t_starts, valve_numbers):
                _key = key + ", round{}".format(i)
                _sec = ac_secs + i*60          # wouldn't this really be minutes?
                _t_start = t_start + i*60

                self.listAction[_key] = formatActionParam(action, ac_min, \
                        _sec, _t_start, valve_number)
            
            i=i+1 # ??

            #print(self.listAction)

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
        self.time_setup = TimeSetup(self.listAction, self.bond_duration_obj)
        self.time_setup.show()
#------------------------------------------------------------------------------------

class TimeSetup(QMainWindow, QWidget):

    def __init__(self, set_action, bond_duration):
        super().__init__()

        self.wid2 = QWidget()
        self.actionDisplay2 = ''
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
        self.actionDisplay2 = AcSummaryEdit
        self.actionDisplay2.setText(formatDict(self.set_action, self.bond_duration_obj2))

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
