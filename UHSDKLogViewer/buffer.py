# A circular buffer to handle X-Y-Z-I data
class CircularBuffer(object):
    def __init__(self, size=512):
        """initialization"""
        self.index = 0
        self.size = size
        self._data = []

    def record(self, value):
        """append an element"""
        if len(self._data) == self.size:
            self._data[self.index]= value
        else:
            self._data.append(value)
        
        self.index = (self.index + 1) % self.size

    def __getitem__(self, key):
        """get element by index like a regular array"""
        return(self._data[key])

    def __repr__(self):
        """return string representation"""
        return self._data.__repr__() + ' (' + str(len(self._data))+' items)'

    def get_all(self):
        """return a list of all the elements"""
        return(self._data)

    def clear_all(self):
        """return a list of all the elements"""
        self._data = []
