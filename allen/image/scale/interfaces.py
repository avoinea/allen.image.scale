from zope import schema
from zope.interface import Interface

class IThumbnail(Interface):
    """ Generate thumbnail images
    """
    templates = schema.Dict()

    def resize(size):
        """ Resize using PIL"""

class IImageScale(Interface):
    """ Access image sizes from annotation
    """
