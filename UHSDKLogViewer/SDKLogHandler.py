# -*- coding: utf-8 -*-
"""
# Class to handle reading of SDK Log Data as a pipe/fifo for 
# Windows and Unix, to avoid big log files.
----------------------------------------------------------
"""
import platform
import os
import tempfile

IS_WINDOWS = platform.system().lower() == "windows"
if IS_WINDOWS:
    try:
        import win32pipe, win32file
    except:
        print("*** WARNING: PyWin dependencies not found for Windows - Please install via:\n\n pip3 install --user pywin32 \n")

class SDKLogPipeHandler(object):
    def __init__(self, is_windows=True):
        super(SDKLogPipeHandler, self).__init__()
        
        # Do we need Unix/Windows setup?
        self.isWindows = is_windows

        # A default location to create a named pipe
        # This shall be used instead of writing the SDK Log to a file.
        if self.isWindows:
            self.pipe_name = r'\\.\pipe\UHSDK'
        else:
            tmpdir = tempfile.mkdtemp()
            self.pipe_name = os.path.join(tmpdir, 'myfifo')

        self.namedPipe = None
        self.xyzi_regex = r'\[(-?[0-9.]+),(-?[0-9.]+),(-?[0-9.]+)\] intensity (-?[0-9.]+)'

        # Number of bytes to read from SDK Log on Windows
        self.num_bytes = 64*1024

    def setupNamedPipe(self):
        # On Windows, we use the win32pipe module
        if self.isWindows:
            if not self.namedPipe:
                self.namedPipe = win32pipe.CreateNamedPipe(self.pipe_name, win32pipe.PIPE_ACCESS_DUPLEX,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                    win32pipe.PIPE_UNLIMITED_INSTANCES, 
                    self.num_bytes, 
                    self.num_bytes,
                    0,
                    None)
        # Else, on Unix systems, use mkfifo
        else:
            if not self.namedPipe:
                try:
                    self.namedPipe = os.mkfifo(self.pipe_name)
                except:
                    print("EXCEPTION: Pipe for %s exists!" % self.pipe_name)     

    # win32pipe, Windows only methods
    def connectToSDKPipe(self):
        win32pipe.ConnectNamedPipe(self.namedPipe, None)

    def getDataFromNamedPipe(self):
        data = win32file.ReadFile(self.namedPipe, self.num_bytes)
        return data      
