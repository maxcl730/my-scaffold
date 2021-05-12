# -*- coding: utf-8 -*-
from PIL import Image as PillowImage
from flask import current_app
# from werkzeug.utils import secure_filename
from werkzeug._compat import text_type, PY2
from datetime import datetime
from uuid import uuid4
import os.path as op
import os
import re
from common import Log
from trialcenter.models.image import Image
from common.date import Date


class ImageService(object):
    @classmethod
    def allowed_file(cls, filename):
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        return '.' in cls.secure_filename(filename) and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @classmethod
    def generate_image_path_info(cls, filename):
        fn, extension = op.splitext(filename)
        date_path = datetime.now().strftime("%Y%m%d")
        path = op.join(current_app.config['UPLOAD_FOLDER'], date_path)
        if not op.exists(path):
            os.makedirs(path)
        fn = uuid4().__str__().replace('-', '') + extension
        url = date_path + '/' + fn
        return op.join(path, fn), url

    @classmethod
    def image_upload(cls, file, width=0, height=0, thumbnail=False):
        if not cls.allowed_file(file.filename):
            Log.warn("Filename's suffix was not allowed.")
            raise Exception("Filename's suffix was not allowed.")
        if file:
            filename, url = cls.generate_image_path_info(file.filename)
            file.save(filename)
            pillow_image = PillowImage.open(filename).convert('RGB')
            if width != 0 and height != 0:
                if width != pillow_image.width or height != pillow_image.height:
                    Log.warn("Invalid image size.")
                    os.remove(filename)
                    raise Exception('Invalid image size.')
            if pillow_image:
                if thumbnail:
                    # 生成缩略图
                    if pillow_image.height > pillow_image.width:
                        # 竖图
                        pos = (pillow_image.height - pillow_image.width) // 2
                        crop_image = pillow_image.crop((0, pos, pillow_image.width, pillow_image.height - pos))
                        thumb_img = crop_image.resize((current_app.config['APP']['thumb_height'],
                                                       current_app.config['APP']['thumb_width']),
                                                      PillowImage.ANTIALIAS)
                    elif pillow_image.height < pillow_image.width:
                        # 横图
                        pos = (pillow_image.width - pillow_image.height) // 2
                        crop_image = pillow_image.crop((pos, 0, pillow_image.width - pos, pillow_image.height))
                        thumb_img = crop_image.resize((current_app.config['APP']['thumb_height'],
                                                       current_app.config['APP']['thumb_width']),
                                                      PillowImage.ANTIALIAS)
                    else:
                        thumb_img = pillow_image.resize((current_app.config['APP']['thumb_height'],
                                                         current_app.config['APP']['thumb_width']),
                                                        PillowImage.ANTIALIAS)
                    thumb_img.save(filename + '_thumb.jpg', format='jpeg', quality=80)
                image = Image(filename=filename,
                              url=url,
                              size=op.getsize(filename),
                              height=pillow_image.height,
                              width=pillow_image.width
                              ).save()
                Log.info('Success upload file: {}.'.format(filename))
                return image
            else:
                Log.warn('Can not open image file.')
                raise Exception('Can not open image file.')
        else:
            Log.warn('Invalid file data.')
            raise Exception('Invalid file data.')

    @classmethod
    def secure_filename(cls, filename):
        r"""Pass it a filename and it will return a secure version of it.  This
        filename can then safely be stored on a regular file system and passed
        to :func:`os.path.join`.  The filename returned is an ASCII only string
        for maximum portability.

        On windows systems the function also makes sure that the file is not
        named after one of the special device files.

        >>> secure_filename("My cool movie.mov")
        'My_cool_movie.mov'
        >>> secure_filename("../../../etc/passwd")
        'etc_passwd'
        >>> secure_filename(u'i contain cool \xfcml\xe4uts.txt')
        'i_contain_cool_umlauts.txt'

        The function might return an empty filename.  It's your responsibility
        to ensure that the filename is unique and that you generate random
        filename if the function returned an empty one.

        .. versionadded:: 0.5

        :param filename: the filename to secure
        """
        _filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_.-]')
        _windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
                                 'LPT2', 'LPT3', 'PRN', 'NUL')

        if isinstance(filename, text_type):
            from unicodedata import normalize
            filename = normalize('NFKD', filename).encode('ascii', 'ignore')
            if not PY2:
                filename = filename.decode('ascii')
        if filename.startswith('.'):
            filename = 'chinese_' + str(Date.datetime_toTimestamp(datetime.now())) + filename
        for sep in os.path.sep, os.path.altsep:
            if sep:
                filename = filename.replace(sep, ' ')
        filename = str(_filename_ascii_strip_re.sub('', '_'.join(
                       filename.split()))).strip('._')
        # on nt a couple of special files are present in each folder.  We
        # have to ensure that the target file is not such a filename.  In
        # this case we prepend an underline
        if os.name == 'nt' and filename and \
           filename.split('.')[0].upper() in _windows_device_files:
            filename = '_' + filename

        return filename
