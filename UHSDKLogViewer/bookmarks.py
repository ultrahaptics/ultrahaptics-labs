from PyQt5.QtCore import QSettings

class BookmarksManager(object):
    def __init__(self):
        self.settings = QSettings("UHSDKLogViewer")
        self.bookmarks = []

    # Returns a list of the current bookmarks
    def getBookmarks(self):
        keys = self.settings.allKeys()
        for key in keys:
            if key.startswith('bookmark/'):
                self.bookmarks.append(self.settings.value(key))

        return self.bookmarks

    # Clear ALL of the stored favourites
    def clearBookmarks(self):
        keys = self.settings.allKeys()
        for key in keys:
            self.settings.remove(key)
        self.bookmarks = []

    def _removeDuplicates(self, x):
        return list(dict.fromkeys(x))

    # Inserts a new Bookmark at index 0. 
    # Increase the index of other bookmarks and limit to 10
    def addNewBookmark(self, path):
        original_bookmarks = self.getBookmarks()
        if len(original_bookmarks) > 9:
            original_bookmarks[0:8]

        self.clearBookmarks()

        original_bookmarks.insert(0, path)
        bookmarks = self._removeDuplicates(original_bookmarks)

        # Now move 0-1, 1->2 etc.
        for n in range(0,len(bookmarks)):
            self.settings.setValue('bookmark/%s' % (str(n)), original_bookmarks[n])