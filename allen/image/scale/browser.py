from zope.interface import implements
from zope.component import getAdapter
from zope.publisher.interfaces import NotFound
from zope.publisher.browser import BrowserPage
from interfaces import IThumbnail
from interfaces import IImageScale
from zope.traversing.browser import absoluteURL
from zope.app.file.image import Image

from allen.utils.cache import servercache

class ImageScale(BrowserPage):
    """ Access resized image
    """
    implements(IImageScale)
    _name = ''

    @property
    def etag(self):
        etag = absoluteURL(self.context, self.request)
        etag += '/scale/' + self._name
        return etag

    @servercache
    def resize(self, name):
        thumb = getAdapter(self.context, IThumbnail)
        return thumb.resize(name)

    def publishTraverse(self, request, name):
        self._name = name
        thumb = self.resize(name)
        if not thumb:
            raise NotFound(self, name, request)
        return Image(thumb)
