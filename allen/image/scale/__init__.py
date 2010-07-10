import logging
from PIL import Image as PilImage
from StringIO import StringIO

from zope.interface import implements
from interfaces import IThumbnail
from z3c.blobfile.image import Image
logger = logging.getLogger('allen.image.scale')

class Thumbnail(object):
    """ Adapter for zope.app.file.image.Image object to generate thumbnails
    """
    implements(IThumbnail)

    def __init__(self, context):
        self.context = context
        self.quality = 100

    @property
    def templates(self):
        return {
            'album': (100, 100),
            'thumbnail': (128, 128),
            'normal': (192, 192),
            'large': (480, 480),
            'icon': (32, 32),
            'link': (16, 16),
        }

    def get_crop_box(self, width, height):
        if width == height:
            return 0, 0, width, height
        elif width > height:
            return width/2 - height/2, 0, width/2 + height/2, height
        return 0, 0, width, width

    def get_crop_aspect_ratio(self, size):
        img_width, img_height = self.context.getImageSize()
        if img_width == img_height:
            return size, size

        width = height = size
        sw = float(width) / img_width
        sh = float(height) / img_height
        if img_width > img_height:
            width = int(sh * img_width + 0.5)
        else:
            height = int(sw * img_height + 0.5)
        return width, height

    def get_aspect_ratio(self, width, height):
        #return proportional dimensions within desired size
        img_width, img_height = self.context.getImageSize()
        sw = float(width) / img_width
        sh = float(height) / img_height
        if sw <= sh: height = int(sw * img_height + 0.5)
        else: width = int(sh * img_width + 0.5)
        return width, height

    def _resize(self, display, crop=False):
        if display not in self.templates.keys():
            display = 'thumbnail'
        width, height = self.templates.get(display)

        # Calculate image width, size
        if crop:
            width, height = self.get_crop_aspect_ratio(width)
        else:
            width, height = self.get_aspect_ratio(width, height)

        # Resize image
        newimg = StringIO()
        img = PilImage.open(StringIO(self.context.data))
        fmt = img.format
        try:
            img = img.resize((width, height), Image.ANTIALIAS)
        except AttributeError:
            img = img.resize((width, height))

        # Crop if needed
        if crop:
            box = self.get_crop_box(width, height)
            img = img.crop(box)
        img.save(newimg, fmt, quality=self.quality)
        newimg.seek(0)
        return newimg.read()

    def resize(self, size):
        crop = False
        if size == 'album':
            crop = True
        try:
            img = self._resize(size, crop)
        except IOError, err:
            logger.exception(err)
            img = ''
        return img
