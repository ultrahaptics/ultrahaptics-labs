#!/usr/bin/env python3
# An SDK Log visualiser built with PyQt which plots control points in 3D space
# Dependencies:
# -Python 3.7.x (http://python.org)
# -The following Python modules are required: pyqt5, pyqtgraph, numpy, PyOpenGL, atom
#   The recommended way to install these via pip (for Python 3)
#   To install with pip3 run this command:
#     $ pip3 install --user pyqt5 pyqtgraph numpy PyOpenGL atom
# On Windows, pywin32 is also required.
import sys
import os
import re
import threading
import argparse
import platform
from subprocess import Popen

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import Qt
except Exception as e:
    print("Exception on thirdparty import: " + str(e))
    print("*** WARNING: Unable to import dependencies. Please install via:\n\n pip3 install --user pyqt5 pyqtgraph numpy PyOpenGL atom \n")

from SDKLogHandler import SDKLogPipeHandler
from bookmarks import BookmarksManager
from ui import UHSDKLogViewer

IS_WINDOWS = platform.system().lower() == "windows"
IS_UNIX = platform.system().lower() in ("darwin", "linux", "mac")

# TODO: Move to build script
def _append_run_path():
    if getattr(sys, 'frozen', False):
        pathlist = []

        # If the application is run as a bundle, the pyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        pathlist.append(sys._MEIPASS)

        # the application exe path
        _main_app_path = os.path.dirname(sys.executable)
        pathlist.append(_main_app_path)

        # append to system path enviroment
        os.environ["PATH"] += os.pathsep + os.pathsep.join(pathlist)
_append_run_path()

class MainWindow(QMainWindow):
    def __init__(self, exe_path=None, auto_launch=True, parent = None):
        super(MainWindow, self).__init__(parent)

        if exe_path:
            print("An executable process was provided: %s" % exe_path)
            self.exePath = exe_path

        self.log_reader_thread = None
        self.executable_process = None
        self.processingSDKLog = True
        self.my_env = None

        layout = QHBoxLayout()

        self.bookmarksManager = BookmarksManager()

        self.items = QDockWidget("Bookmarks", self)
        self.bookmarkListWidget = QListWidget()

        self.bookmarkListWidget.itemDoubleClicked.connect(self.bookmarkDoubleClicked)
        self.items.setWidget(self.bookmarkListWidget)
        self.items.setFloating(False)

        self.viewer = UHSDKLogViewer(exe_path=exe_path, auto_launch=auto_launch)
        self.setCentralWidget(self.viewer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.items)

        # MenuBar actions
        bar = self.menuBar()
        file = bar.addMenu("File")
        playback = bar.addMenu("Playback")
        self.openProcessAction = file.addAction("Open Process")
        self.openProcessAction.triggered.connect(self.launchProcessFromFileDialog)
        self.openProcessAction.setShortcut("Ctrl+O")

        self.clearBookmarksAction = file.addAction("Clear Bookmarks")
        self.clearBookmarksAction.triggered.connect(self.clearBookmarksAndUpdate)
        self.clearBookmarksAction.setShortcut("Ctrl+X")

        # TODO: Fix monitoring pause/resume
        self.activeMonitoringAction = playback.addAction("Disable Monitoring")
        self.activeMonitoringAction.setEnabled(False)
        #self.activeMonitoringAction.setShortcut("Space")
        #self.activeMonitoringAction.triggered.connect(self.toggleProcessingLog)

        self.exitAction = file.addAction("Shutdown")
        self.exitAction.setShortcut("Esc")
        self.exitAction.triggered.connect(self.shutDown)

        # Set up an empty log file location
        self.setEnvironmentForLogging()
        self.startPollingLogReaderThread()

        # Optionally launch an executable on launch of the dialog
        if auto_launch:
            self.launchExecutable()

        # Setup the bookmarks list
        self.updateBookmarkList()        

    def launchProcessFromFileDialog(self):
        dialog = QFileDialog()
        fname = dialog.getOpenFileName(None, 'Select Executable to Monitor', '.', '*',    '*', QFileDialog.DontUseNativeDialog)
        if os.path.isfile(fname[0]):
            if self.executable_process:
                self.executable_process.kill()
            self.exePath = fname[0]
            self.bookmarksManager.addNewBookmark(self.exePath)
            self.updateBookmarkList()
            self.launchExecutable(ask=True)

    def updateBookmarkList(self):
        self.bookmarkListWidget.clear()
        for bookmark in self.bookmarksManager.getBookmarks():
            self.bookmarkListWidget.addItem(bookmark)

    def clearBookmarksAndUpdate(self):
        print("clearBookmarksAndUpdate")
        self.bookmarksManager.clearBookmarks()
        self.updateBookmarkList()

    def bookmarkDoubleClicked(self, value):
        self.exePath = value.text()
        self.launchExecutable(ask=True)

    def shutDown(self):
        if self.executable_process:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Preparing to close.")
            msg.setInformativeText("Do you want to kill your monitored process?")
            msg.setWindowTitle("Quit")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            retval = msg.exec_()
            if retval == QMessageBox.No:
                return
            else:
                try:
                    self.executable_process.kill()
                except:
                    print("Unable to kill the executable process: " + str(self.executable_process))
        sys.exit(app.exec_())

    def closeEvent(self, event):
        self.shutDown()
        return QMainWindow.closeEvent(self, event)

    def launchExecutable(self, ask=False):
        print("Launching: %s" % (self.exePath))

        if not os.path.isfile(self.exePath):
            print("WARNING: Unable to launch: (%s) - check path exists and is executable" % self.exePath)
            return

        exe_root = os.path.dirname(self.exePath)

        if not ask:
            self.executable_process = Popen([self.exePath], env=self.my_env, cwd=exe_root)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Launching:\n%s" % self.exePath)
            msg.setInformativeText("Do you want to start monitoring this App?");
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            retval = msg.exec_()
            if retval == QMessageBox.No:
                return
            else:
                try:
                    self.executable_process = Popen([self.exePath], env=self.my_env, cwd=exe_root)
                except:
                    print("Unable to kill the process: " + str(self.exePath))            

    def setEnvironmentForLogging(self):
        self.logHandler = SDKLogPipeHandler(is_windows=IS_WINDOWS)
        self.logHandler.setupNamedPipe()        
        os.environ["UH_LOG_LEVEL"] = "4"
        os.environ["UH_LOG_DEST"] = self.logHandler.pipe_name
        os.environ["UH_LOG_LEVEL_FORCE"] = "1"
        os.environ["UH_LOG_DEST_FORCE"] = "1"

        # Store a copy of the environment, so it can be passed to the subprocess
        self.my_env = os.environ.copy()

    # Method for thread to process the Log on Unix - consider moving to SDKLogHandler Class
    def processLogUnix(self):
        with open(self.logHandler.pipe_name) as fifo:
            while self.processingSDKLog:
                try:               
                    data = fifo.readline()
                    match = re.search(self.logHandler.xyzi_regex, data)
                    self.viewer.setControlPointsFromFromRegexMatch(match)                      
                except Exception as e:
                    print (e)

    # Methof for thread to process the Log on Windows - consider moving to SDKLogHandler Class
    def processLogWindows(self):
        while self.processingSDKLog:
            if not self.logHandler.namedPipe:
                self.logHandler.setupNamedPipe()
                self.logHandler.connectToSDKPipe()
            try:
                data = self.logHandler.getDataFromNamedPipe()
            except Exception as e:
                print ("Errors processing log on Windows: " + str(e))
                self.logHandler.namedPipe = None
                continue

            if len(data)<2:
                print("No valid Pipe data available")
                continue

            lines = str(data[1], "utf-8").split(os.linesep)

            for line in lines:
                match = re.search(self.logHandler.xyzi_regex, line)
                self.viewer.setControlPointsFromFromRegexMatch(match)                

    def startPollingLogReaderThread(self):
        if IS_UNIX:
            self.log_reader_thread = threading.Thread(target=self.processLogUnix)
        elif IS_WINDOWS:
            self.log_reader_thread = threading.Thread(target=self.processLogWindows)

        self.log_reader_thread.daemon = True
        self.processingSDKLog = True
        self.log_reader_thread.start()
        self.activeMonitoringAction.setText("Disable Monitoring")

    def stopPollingLogReaderThread(self):
        self.processingSDKLog = False
        if self.log_reader_thread.is_alive():
            # Fix this - it will quit the process!
            self.log_reader_thread.join()
            self.activeMonitoringAction.setText("Enable Monitoring")

    def toggleProcessingLog(self):
        self.processingSDKLog = not self.processingSDKLog
        if not self.processingSDKLog:
            self.stopPollingLogReaderThread()
        else:
            self.startPollingLogReaderThread()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setOrganizationName("Ultrahaptics");
    app.setOrganizationDomain("com.ultrahaptics");
    app.setApplicationName("Ultrahaptics Visualiser");
    app.setQuitOnLastWindowClosed(False)

    parser = argparse.ArgumentParser(usage="-e <executable path> -a <add to automatically launch the executable>")
    parser.add_argument('-e', '--exePath', required=False, help='The executable process to lauch. If specified, the specified executable will be launched and monitored.')
    parser.add_argument('-a', '--autoLaunch', action="store_true", default=False, required=False, help='If specified, will automatically launch the specified executable on launch.')
    args = parser.parse_args()

    exePath = args.exePath
    autoLaunch = args.autoLaunch
    
    ex = MainWindow(exe_path = exePath, auto_launch = autoLaunch)
    ex.setWindowTitle("Ultrahaptics Visualiser")
    ex.show()
    sys.exit(app.exec_())
