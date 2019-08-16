try:
    import numpy as np
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize, QSettings
    from PyQtGraph3DWidgets import Scatter3DPlot, Scatter3DScene

    # The below imports are only necessary due to a PyInstaller Error
    # TODO: remove these once the PyInstaller process is properly understood!
    import numpy.random.common
    import numpy.random.bounded_integers
    import numpy.random.entropy
except Exception as e:
    print("Exception on thirdparty import: " + str(e))
    print("*** WARNING: Unable to import dependencies. Please install via:\n\n pip3 install --user pyqt5 pyqtgraph numpy PyOpenGL atom \n")

from buffer import CircularBuffer

class UHSDKLogViewer(QWidget):

    def __init__(self, exe_path=None, auto_launch=False):
        super(UHSDKLogViewer, self).__init__()

        self.pointBuffer = CircularBuffer(size=512)

        self.painterThreadTimer = QTimer()
        self.painterThreadTimer.timeout.connect(self.updatePlot)
        self.painterThreadTimer.start()

        pos = np.random.random(size=(512*256,3))
        pos *= [10,-10,10]
        d2 = (pos**2).sum(axis=1)**0.5
        pos[:, 2] = d2
        color = [0, 1, 0, 0.5]
        size = 10

        self.plot3D = Scatter3DPlot(pos=pos, size=size, color=color)
        self.scene3D = Scatter3DScene(plot=self.plot3D)
        self.scene3D._widget.setMinimumSize(QSize(500, 700))
        
        # Scaling of control point space
        self._scaling = 10

        # Build UI
        self.createUI()

    def createUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.scene3D._widget)
        self.setLayout(mainLayout)
    
    def updatePlot(self):
        if len(self.pointBuffer[:])>0:
            pts = np.array(self.pointBuffer[:])
            intensity = pts[:,3]
            color = np.ones((pts.shape[0], 4))
            color[:,3] = intensity
            self.plot3D._plot.setData(pos=pts[:,0:3], color = color)

    def setControlPointsFromFromRegexMatch(self, match):
        if (match):
            pts = [self._scaling*float(match[1]),
                   self._scaling*float(match[2]),
                   self._scaling*float(match[3]),
                   float(match[4])]
            self.pointBuffer.record(pts)
        else:
            self.pointBuffer.record([0.0,0.0,0.0,0.0])
