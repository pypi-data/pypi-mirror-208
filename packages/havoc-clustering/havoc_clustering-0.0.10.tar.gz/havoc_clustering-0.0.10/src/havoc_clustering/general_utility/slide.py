from enum import Enum
import openslide
import re
import pathlib
from PIL import Image
import logging
from collections import namedtuple
from datetime import datetime

Image.MAX_IMAGE_PIXELS = 100000000000


class ImageType(Enum):
    # our supported image types
    SVS = '.svs'
    JPG = '.jpg'
    NDPI = '.ndpi'

    @classmethod
    def supports(cls, value):
        '''
        Checks if given value is a supported image type
        :param value: str
        :return:
        '''
        return any(value == item.value for item in cls)


class ImageTypeError(Exception):
    pass


class MissingMetadataError(Exception):
    pass


class Slide:
    '''
    A slide object
    '''

    def __init__(self, path, img_requirements=None, stain_type='Unknown'):
        '''
        Creates a slide object with all possible data of the slide extracted

        :param path:
        :param img_requirements: dictionary of required svs configurations
        '''

        if pathlib.Path(path).is_dir():
            raise ImageTypeError("This is a directory")

        self.path = path
        self.name = pathlib.Path(path).stem
        self.image_type = pathlib.Path(path).suffix
        if not Slide.has_valid_extension(path):
            raise ImageTypeError("We currently do not support images of type {}".format(self.image_type))
        self.stain_type = stain_type

        # the actual instance of the image at the given path
        if self.image_type == ImageType.SVS.value or self.image_type == ImageType.NDPI.value:
            i = openslide.OpenSlide(self.path)
            w, h = i.dimensions
        elif self.image_type == ImageType.JPG.value:
            i = Image.open(self.path)
            w, h = i.width, i.height
        else:
            raise ImageTypeError("Functionality for valid image type {} missing".format(self.image_type))

        Coordinate = namedtuple('Coordinate', 'x y')
        self.start_coordinate = Coordinate(0, 0)
        self.width = w
        self.height = h
        self.image = i

        # get svs data if its an svs path
        if self.image_type == ImageType.SVS.value:
            curr_slide_data = Slide.extract_data_svs(path)
        elif self.image_type == ImageType.NDPI.value:
            curr_slide_data = Slide.extract_data_ndpi(path)
        else:
            curr_slide_data = Slide.extract_data_jpg(path)

        self.date_scanned = curr_slide_data['date_scanned']
        self.time_scanned = curr_slide_data['time_scanned']
        self.compression = curr_slide_data['compression']
        self.mpp = curr_slide_data['mpp']
        self.apparent_magnification = curr_slide_data['apparent_magnification']  # only here while in process of removal

        # compare slide info with required info
        self._satisfies_slide_requirements(img_requirements)

    def crop(self, coordinates):
        '''
        Updates internal slide properties so that we will only use a section of the slide

        :param coordinates: use only a section of the slide (top_left_x, top_left_y, bot_right_x, bot_right_y)
        :return:
        '''
        Coordinate = namedtuple('Coordinate', 'x y')
        self.start_coordinate = Coordinate(coordinates[0], coordinates[1])
        self.width = coordinates[2] - coordinates[0]
        self.height = coordinates[3] - coordinates[1]

    def get_thumbnail(self, factor=25):
        '''
        Return PIL image of the slide with a scale factor of 25x smaller

        :param factor:
        :return:
        '''
        if factor < 25: raise Exception('Thumbnail factor too small')

        wh_dims = (self.width // factor, self.height // factor)
        if isinstance(self.image, openslide.OpenSlide):
            return self.image.get_thumbnail(wh_dims)
        else:
            return self.image.resize(wh_dims)

    def _satisfies_slide_requirements(self, img_requirements):
        '''
        Returns true if the slide is a svs that satisfies the image requirements.
        Image requirements can specify None if a specific property is unrestricted
        If image is a jpg, trivially returns true

        :param img_requirements: dictionary of required svs configurations
        :return: boolean
        '''

        if img_requirements is None:
            return

        req_comp = img_requirements['compression']
        req_mpp = img_requirements['mpp']

        # metadata check for svs
        if self.image_type == ImageType.SVS.value:

            # if it is an svs, it MUST have compression and mpp values
            if self.compression is None:
                raise MissingMetadataError(
                    "SKIPPING {}. SVS without a compression".format(self.name)
                )
            elif self.mpp is None:
                raise MissingMetadataError(
                    "SKIPPING {}. SVS without a MPP".format(self.name)
                )

            # check if our compression is a part of the required compressions
            if req_comp is not None and self.compression not in req_comp:
                raise ImageTypeError(
                    "SKIPPING {}. SVS with comp {} but must be one of {}".format(self.name, self.compression, req_comp)
                )

            # check if our mpp is a part of the required mpps
            if req_mpp is not None and self.mpp not in req_mpp:
                raise ImageTypeError(
                    "SKIPPING {}. SVS with MPP {} but must be one of {}".format(self.name, self.mpp, req_mpp)
                )

            print("{} has MPP {} and compression {}. Valid".format(
                self.name, self.mpp, self.compression))

        else:
            pass

    @staticmethod
    def has_valid_extension(path):
        '''
        Returns True if the image is a valid type

        :param path:
        :return:
        '''
        return ImageType.supports(pathlib.Path(path).suffix)

    @staticmethod
    def extract_data_svs(slide_path):
        '''
        Extracts useful metadata from the svs

        :param slide_path:
        :return:
        '''

        # dictionary of properties
        image_properties = openslide.OpenSlide(slide_path).properties

        if 'aperio.Date' not in image_properties:
            date_scanned = None
            time_scanned = None
        else:
            # for date and time
            date_scanned = image_properties['aperio.Date']
            # check if was a datetime (requires separation) or just date (there is another property for time)
            if 'aperio.Time' not in image_properties:
                date_scanned = re.search('\d{4}-\d{2}-\d{2}', image_properties['aperio.Date']).group()
                time_scanned = re.search('\d{2}:\d{2}:\d{2}', image_properties['aperio.Date']).group()
            else:
                time_scanned = image_properties['aperio.Time']

        # check if we have mag/compression data
        if 'tiff.ImageDescription' not in image_properties:
            mpp = compression = None
        else:
            mpp = re.search('MPP = ([\d.]+)', image_properties['tiff.ImageDescription'])
            compression = re.search('Q=(\d+)', image_properties['tiff.ImageDescription'])

            # get just the numeric portion of the above regex result
            if mpp is not None:
                mpp = float(mpp.group(1))
            if compression is not None:
                compression = int(compression.group(1))

        # archived. should NOT use this
        if 'aperio.AppMag' in image_properties:
            apparent_magnification = int(float(image_properties['aperio.AppMag']))
        else:
            apparent_magnification = None

        return {
            'date_scanned': date_scanned,
            'time_scanned': time_scanned,
            'compression': compression,
            'mpp': mpp,
            'apparent_magnification': apparent_magnification
        }

    @staticmethod
    def extract_data_ndpi(slide_path):
        '''
        Extracts useful metadata from the ndpi

        :param slide_path:
        :return:
        '''

        # dictionary of properties
        image_properties = openslide.OpenSlide(slide_path).properties

        # https://github.com/InsightSoftwareConsortium/ITKIOOpenSlide/blob/master/examples/ExampleOutput.txt

        datetime2 = datetime.strptime(image_properties['tiff.DateTime'], '%Y:%m:%d %H:%M:%S')

        return {
            'date_scanned': datetime2.strftime('%m/%d/%y'),
            'time_scanned': datetime2.strftime('%H:%M:%S'),
            'compression': None,
            'mpp': float(image_properties['openslide.mpp-x']) if 'openslide.mpp-x' in image_properties else None,
            'apparent_magnification': None
        }

    @staticmethod
    def extract_data_jpg(slide_path):
        '''
        Extracts useful metadata from the jpg

        :param slide_path:
        :return:
        '''

        return {
            'date_scanned': None,
            'time_scanned': None,
            'compression': None,
            'mpp': None,
            'apparent_magnification': None
        }
