UHSDKLogViewer 
--------------
An SDK Log visualiser built with PyQt which plots control points in 3D space

![](icons/visualiser.gif)


Usage:
-------
1. Ensure that this file (UHSDKLogViewer.py) is executable by settings its permissions:
```$ chmod +x UHSDKLogViewer.py``` 
2. Run with -e (--exePath) flag from the command line, to launch an Ultrahaptics executable you wish to monitor
```
$ python3 UHSDKLogViewer.py -e=/path/to/my/process
```

Alternatively, run the compiled applications in the [Executables](https://github.com/ultrahaptics/ultrahaptics-labs/tree/master/UHSDKLogViewer/Executables) directory (Mac and Windows only)

Dependencies:
-------------
1. Python 3.7.x (http://python.org)
2. The following Python modules are required: pyqt5, pyqtgraph, numpy, PyOpenGL, atom
  The recommended way to install these via pip (for Python 3)
  To install with pip3 run this command:
```
$ pip3 install --user pyqt5 pyqtgraph numpy PyOpenGL atom
```
3. Windows only will also require: 
```
$ pip3 install --user pypiwin32
```
