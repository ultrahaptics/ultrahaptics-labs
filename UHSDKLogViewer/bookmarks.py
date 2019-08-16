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
        self.settings.clear()
        self.bookmarks = []

    # Inserts a new Bookmark at index 0. 
    # Increase the index of other bookmarks and limit to 10
    def addNewBookmark(self, path):
        original_bookmarks = self.getBookmarks()
        if len(original_bookmarks) > 10:
            original_bookmarks[-1].pop()

        # First set the new path at index 0
        self.settings.setValue('bookmark/0', path)

        # Now move 0-1, 1->2 etc.
        for n in range(0,len(original_bookmarks)):
            self.settings.setValue('bookmark/%s' % (str(n+1)), original_bookmarks[n])