
import sys
from PyQt4 import QtCore, QtGui  
import record

 
def main():
    app = QtGui.QApplication(sys.argv)  
    form = record.AOPlayer()
   # form.PlaySound('output.wav','Sensor Info')
    form.show()

    app.exec()  
 
if __name__ == "__main__":
    sys.exit(main())