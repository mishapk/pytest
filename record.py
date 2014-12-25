import pyaudio
import wave
import audioop, numpy, struct, math
import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic, QtCore, QtSql
class RPlayer(QThread):
    levelProgress = pyqtSignal(int)
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS =2 
    RATE = 44100
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "output.wav"
    VOLUME=1.0
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
    p2 = pyaudio.PyAudio()
    stream2 = p2.open(format=FORMAT,channels=CHANNELS,rate=RATE,output=True)
    def getVolume(self,data):
        mx = audioop.max(data, 2)*100/2**15
        print(mx)
        self.levelProgress.emit(mx)
    def setVolume(self,volume):
        self.VOLUME=volume/100
    def changeVolume(self,data):
        decodedata = numpy.fromstring(data, numpy.int16)
        newdata = (decodedata * self.VOLUME).astype(numpy.int16)
        return newdata.tostring()
    def echocancel(self,outputdata, inputdata):
        pos = audioop.findmax(outputdata, 800)    # one tenth second
        out_test = outputdata[pos*2:]
        in_test = inputdata[pos*2:]
        ipos, factor = audioop.findfit(in_test, out_test)
        # Optional (for better cancellation):
        # factor = audioop.findfactor(in_test[ipos*2:ipos*2+len(out_test)],
        #              out_test)
        prefill = '\0'*(pos+ipos)*2
        postfill = '\0'*(len(inputdata)-len(prefill)-len(outputdata))
        outputdata = prefill + audioop.mul(outputdata,2,-factor) + postfill
        return audioop.add(inputdata, outputdata, 2)
    def run(self):
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = self.stream.read(self.CHUNK)
            data = self.changeVolume(data)
            #data = self.echocancel(data,data)
            self.stream2.write(data)
            self.getVolume(data)


        self.levelProgress.emit(0)		  

class AOPlayer(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        ChangeVolume = pyqtSignal(int)
        self.a=RPlayer()
        self.a.finished.connect(self.Stop)
         
        self.initGraphics()
    def initGraphics(self):
        grid = QGridLayout(self)
	# Column 0
        label1=QLabel('Датчик:')
        label2=QLabel('Сообщение:')
        self.mpSeek = QSlider(Qt.Horizontal)
        

	
        grid.addWidget(label1,0,0)   
        grid.addWidget(label2,1,0) 
        grid.addWidget(self.mpSeek,3,0,1,2)
 	       
	# Column 1
        self.lineSensor= QLineEdit()
        self.lineMessage= QLineEdit()
        #==========VolumeSlider======================[
        self.mpVolume = QSlider(Qt.Horizontal)
        self.mpVolume.setMinimum(0)
        self.mpVolume.setMaximum(100)
        self.mpVolume.setValue(100)
        self.mpVolume.valueChanged.connect(self.a.setVolume)
        #----------------VolumeSlider----------------]
        self.bPlay = QToolButton()
        self.bStop = QToolButton()
        self.bMute = QToolButton()
        self.bPlay.setIcon( self.style().standardIcon(QStyle.SP_MediaPlay))
        self.bStop.setIcon( self.style().standardIcon(QStyle.SP_MediaStop))
        self.bMute.setIcon( self.style().standardIcon(QStyle.SP_MediaVolume))

        self.layout=QHBoxLayout()
	
        self.layout.addWidget(self.bPlay)
        self.layout.addWidget(self.bStop)
        self.layout.addWidget(self.bMute)
        self.layout.addWidget(self.mpVolume)
       
        grid.addLayout(self.layout,4,1)

        grid.addWidget(self.lineSensor,0,1) 
        grid.addWidget(self.lineMessage,1,1) 

	# Column 2
        self.mGBox= QGroupBox('Экстренны микрофон')
        grid2 = QGridLayout(self.mGBox)
        #=============Button=Record===========================
        self.bRecord = QToolButton()
        self.bRecord.setFixedSize(40,40) 
        self.bRecord.setCheckable(True)

        pixmap = QPixmap(80, 80)
        pixmap.fill(Qt.color0)
        painter = QPainter()
        painter.begin(pixmap)
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(0, 0, 80, 80)
        painter.end()
        self.bRecord.setIcon( QIcon(pixmap))
        self.bRecord.clicked.connect(self.cb) 
        #--------=Button=Record-------------------------------

        self.label3 =QLabel('готов')
        self.cbDirect = QCheckBox(' Прямой') 
        self.pbVolume = QProgressBar()
        self.pbVolume.setTextVisible(False)
        self.pbVolume.setStyleSheet(" QProgressBar { border: 1px solid grey; border-radius: 0px; text-align: center; } QProgressBar::chunk {background-color: #3add36; width: 1px;}")

        grid2.addWidget(self.bRecord,0,0,2,1) 
        grid2.addWidget(self.label3,0,1,Qt.AlignCenter) 
        grid2.addWidget(self.cbDirect,1,1,Qt.AlignCenter) 
        grid.addWidget(self.mGBox,0,2,4,1) 
        grid.addWidget(self.pbVolume,4,2) 

        self.a.levelProgress.connect(self.pbVolume.setValue) 


    def cb(self):
        self.a.start()
    def Stop(self):
        self.bRecord.setChecked(False)
        
	


