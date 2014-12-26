#!-*-coding:utf-8-*-
import pyaudio
import wave
import audioop, numpy, struct, math,time
import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic, QtCore, QtSql

class OPlayer(QThread):

    levelProgress = pyqtSignal(int)
    maxDurationProgress = pyqtSignal(int)    # Максимальная продолжительнасть  сек
    currentDurationProgress = pyqtSignal(int) # Текущая продолжительнасть  сек
    textProgress = pyqtSignal(str)
    VOLUME=1.0
    stp=False
    def __init__(self,fileName,  parent=None):
        super(OPlayer, self).__init__(parent)
        self.fileName = fileName
        #print('sart Oplay')
    def Stop(self):
        self.stp=True
    def getVolume(self,data):
        mx = audioop.max(data, 2)*100/2**15
        #print(mx)
        self.levelProgress.emit(mx)
    def setVolume(self,volume):
        self.VOLUME=volume/100
    def changeVolume(self,data):
        decodedata = numpy.fromstring(data, numpy.int16)
        newdata = (decodedata * self.VOLUME).astype(numpy.int16)
        return newdata.tostring()
    def run(self):
        CHUNK = 1024
        wf = wave.open(self.fileName, 'rb')
        p = pyaudio.PyAudio()
        RATE= wf.getframerate()
        FORMAT = p.get_format_from_width(wf.getsampwidth())
        CHANNELS =wf.getnchannels()
        RECORD_SECONDS= wf.getnframes()/wf.getframerate()

        stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True)
        self.maxDurationProgress.emit(RECORD_SECONDS*10)
        data = wf.readframes(CHUNK)
        sm=RATE / CHUNK
        i=0
        while data != '' and not self.stp:
            data = self.changeVolume(data)
            self.getVolume(data)
            stream.write(data)
            sec=(i/sm)-RECORD_SECONDS
            self.currentDurationProgress.emit((sec+RECORD_SECONDS)*10)
            data = wf.readframes(CHUNK)
            i+=1

        self.currentDurationProgress.emit(0)
        self.levelProgress.emit(0)
        stream.stop_stream()
        stream.close()
        p.terminate()
    def __del__(self):
        pass
        #print('del-PlayrMusic')

class RPlayer(QThread):
    levelProgress = pyqtSignal(int)
    maxDurationProgress = pyqtSignal(int)    # Максимальная продолжительнасть  сек
    currentDurationProgress = pyqtSignal(int) # Текущая продолжительнасть  сек
    textProgress = pyqtSignal(str)
    VOLUME=1.0
    stp=False
    def __init__(self,micMode,  parent=None):
        super(RPlayer, self).__init__(parent)
        self.micMode = micMode

    def Stop(self):
        self.stp=True
    def getVolume(self,data):
        mx = audioop.max(data, 2)*100/2**15
        #print(mx)
        self.levelProgress.emit(mx)
    def setVolume(self,volume):
        self.VOLUME=volume/100
    def changeVolume(self,data):
        decodedata = numpy.fromstring(data, numpy.int16)
        newdata = (decodedata * self.VOLUME).astype(numpy.int16)
        return newdata.tostring()


    def run(self):

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS =2
        RATE = 44100
        RECORD_SECONDS = 10
        WAVE_OUTPUT_FILENAME = "output.wav"

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE, input=True,output = True, frames_per_buffer=CHUNK)
        frames = []

        sm=RATE / CHUNK
        self.maxDurationProgress.emit(RECORD_SECONDS*10)
        i=0
        while (i<int(RATE / CHUNK * RECORD_SECONDS)) and not self.stp:
            data = stream.read(CHUNK)
            data = self.changeVolume(data)
            self.getVolume(data)
            sec=(i/sm)-RECORD_SECONDS
            self.currentDurationProgress.emit((sec+RECORD_SECONDS)*10)

            if self.micMode:
                stream.write(data)
                text="{} {:.2f} {}".format('Трансляция ',sec,'с' )
                self.textProgress.emit(text)
            else:
                frames.append(data)
                text="{} {:.2f} {}".format('Запись ',sec,'с' )
                self.textProgress.emit(text)
            i+=1
        #-----End While------------
        self.levelProgress.emit(0)
        i=0
        while(i<len(frames) and not self.stp):
            data=frames[i]
            stream.write(data)
            sec="{} {:.2f} {}".format('Трансляция ',(i/sm)-RECORD_SECONDS,'с' )
            self.textProgress.emit(sec)
            self.getVolume(data)
            self.currentDurationProgress.emit(((i/sm)+1)*10)
            i+=1
         #--------------------
        self.textProgress.emit('Готов')
        self.currentDurationProgress.emit(0)
        stream.stop_stream()
        stream.close()
        p.terminate()
        self.levelProgress.emit(0)
    def __del__(self):
        pass
        #print('del-playREcordEnd')
class AOPlayer(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        ChangeVolume = pyqtSignal(int)

         
        self.initGraphics()
    def initGraphics(self):
        grid = QGridLayout(self)
	# Column 0
        label1=QLabel('Датчик:')
        label2=QLabel('Сообщение:')
        self.mpSeek = QSlider(Qt.Horizontal)
        

	
        grid.addWidget(label1,0,0)   
        grid.addWidget(label2,1,0) 
        grid.addWidget(self.mpSeek,3,0,1,3)
 	       
	# Column 1
        self.lineSensor= QLineEdit()
        self.lineMessage= QLineEdit()
        #==========VolumeSlider======================[
        self.mpVolume = QSlider(Qt.Horizontal)
        self.mpVolume.setMinimum(0)
        self.mpVolume.setMaximum(100)
        self.mpVolume.setValue(100)

        #----------------VolumeSlider----------------]
        self.bPlay = QToolButton()
        self.bPlay.clicked.connect(self.Play)
        self.bStop = QToolButton()
        self.bStop.clicked.connect(self.Stop)
        self.bMute = QToolButton()
        self.bPlay.setIcon( self.style().standardIcon(QStyle.SP_MediaPlay))
        self.bStop.setIcon( self.style().standardIcon(QStyle.SP_MediaStop))
        self.bMute.setIcon( self.style().standardIcon(QStyle.SP_MediaVolume))

        self.layout=QHBoxLayout()
	
        self.layout.addWidget(self.bPlay)
        self.layout.addWidget(self.bStop)
        self.layout.addWidget(self.bMute)
        self.layout.addWidget(self.mpVolume)
       
        grid.addLayout(self.layout,4,1,1,2)

        grid.addWidget(self.lineSensor,0,1,1,2)
        grid.addWidget(self.lineMessage,1,1) 

    # Column  2
        self.bOpenFile = QToolButton()
        self.bOpenFile.setIcon( self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.bOpenFile.clicked.connect(self.OpenFile)
        grid.addWidget(self.bOpenFile,1,2)

	# Column 3
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

        self.label3 =QLabel('')
        self.cbDirect = QCheckBox(' Прямой') 
        self.pbVolume = QProgressBar()
        self.pbVolume.setTextVisible(False)

        self.pbVolume.setStyleSheet(" QProgressBar { border: 1px solid grey; border-radius: 0px; text-align: center; } QProgressBar::chunk {background-color: #3add36; width: 1px;}")

        grid2.addWidget(self.bRecord,0,0,2,1) 
        grid2.addWidget(self.label3,0,1,Qt.AlignCenter) 
        grid2.addWidget(self.cbDirect,1,1,Qt.AlignCenter) 
        grid.addWidget(self.mGBox,0,3,4,1)
        grid.addWidget(self.pbVolume,4,3)


    def OpenFile(self):
        dialog = QFileDialog()
        urls=[QUrl.fromLocalFile(".")]
        dialog.setSidebarUrls(urls)
        dialog.setFilter('Wav(*.wav)')
        dialog.setDirectory('.')
        dialog.setReadOnly(True)
        dialog.setFileMode(QFileDialog.AnyFile)

        if dialog.exec():

            fileName = dialog.selectedFiles()
            relDir = os.path.relpath(__file__)

            fn=os.path.relpath(fileName[0], relDir)

            self.lineMessage.setText(fn[1:])

    def rbUP(self):
        self.bRecord.setChecked(False)
    def cb(self):
        self.Stop()
        self.a=RPlayer(self.cbDirect.isChecked())
        self.a.finished.connect(self.rbUP)
        self.mpVolume.valueChanged.connect(self.a.setVolume)
        self.a.levelProgress.connect(self.pbVolume.setValue)
        self.a.textProgress.connect(self.label3.setText)
        self.a.maxDurationProgress.connect(self.mpSeek.setMaximum)
        self.a.currentDurationProgress.connect(self.mpSeek.setValue)
        self.a.start()
        self.bRecord.setChecked(True)
    def Stop(self):
        if  hasattr(self,'a') :
            self.a.Stop()
        if  hasattr(self,'m') :
            self.m.Stop()

    def PlaySound(self, fileName,info):
        if(os.path.exists(fileName)):
            self.Stop()
            time.sleep(0.1)
            self.lineMessage.setText(fileName)
            self.lineSensor.setText(info)
            self.m = OPlayer(fileName)
            self.m.finished.connect(self.rbUP)
            self.mpVolume.valueChanged.connect(self.m.setVolume)
            self.m.levelProgress.connect(self.pbVolume.setValue)

            self.m.maxDurationProgress.connect(self.mpSeek.setMaximum)
            self.m.currentDurationProgress.connect(self.mpSeek.setValue)
            self.m.start()
        else:
            print('FileNoFound')
    def Play(self):
        self.PlaySound(self.lineMessage.text(),self.lineSensor.text())









