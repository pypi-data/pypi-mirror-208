import numpy as np
import cv2
import openslide
import time


class TileExtractor:
    DEFAULT_MIN_NON_BLANK_AMT = 0.4

    def __init__(self, slide, tile_size=1024, desired_tile_mpp=0.5040, coordinates=None):
        '''
        Creates a tile extractor object for the given slide

        Default MPP used is for 20x magnification. Regardless of the the MPP of the slide given is, the tiles produced
        will be of the `desired_tile_mpp`

        If desired MPP and slide MPP match, then this serves as a raw tile extractor.
        If they don't match:
            if slide MPP is smaller (larger magnification), takes a larger tile size and resizes the tile down
            if slide MPP is larger (smaller magnification), takes a smaller tile size and resizes the tile up

        :param slide: slide object
        :param tile_size:
        :param desired_tile_mpp: the mpp of tiles that the tile extractor returns
        '''

        self.slide = slide
        self.original_tile_size = tile_size
        self.desired_tile_mpp = desired_tile_mpp

        # NOTE: the slides could have different but very similar mpp which can result in errors later
        if slide.mpp and np.abs(slide.mpp - desired_tile_mpp) < 0.01: slide.mpp = desired_tile_mpp

        # resize tile size if required. if the slide's mpp has too high precision, round down to avoid numerical issues
        factor = desired_tile_mpp / round(slide.mpp, 3) if slide.mpp else 1
        modified_tile_size = int(tile_size * factor)
        self.modified_tile_size = modified_tile_size
        self.tile_size_resize_factor = factor

        # 'Crop' leftover from right and bottom
        self.trimmed_width = slide.width - (slide.width % modified_tile_size)
        self.trimmed_height = slide.height - (slide.height % modified_tile_size)
        self.chn = 3

        # for use with ImageCreator. the actual output dimensions once we extract all tiles
        self.output_width = int(self.trimmed_width / factor)
        self.output_height = int(self.trimmed_height / factor)

        self.coordinates = self.get_all_possible_coordinates() if coordinates is None else coordinates
        # keeps track of which coordinates end up being used
        self.used_coordinates_mask = []

    @staticmethod
    def amount_blank(tile):
        '''
        Returns percentage of how many pixels are "blank" within the tile

        :param tile: BGR numpy array
        :return:
        '''

        # in rgb form, when pixels are all equal, it is white or black or grey. get all the corresponding pixels whose
        # values are all similar to each other (using std dev)
        return np.sum(np.std(tile, axis=2) < 2.75) / (tile.shape[0] * tile.shape[1])

    def get_all_possible_coordinates(self):
        # initialization
        x = y = 0
        tile_size = self.modified_tile_size

        possible_coordinates = []

        # break out when top left coordinate of next tile is the bottom of image
        while y != self.trimmed_height:

            # Get current sub-image
            x_adj = x + self.slide.start_coordinate.x
            y_adj = y + self.slide.start_coordinate.y

            possible_coordinates.append((x_adj, y_adj, x_adj + tile_size, y_adj + tile_size))

            # move onto next spot
            x += tile_size
            if x == self.trimmed_width:
                x = 0
                y += tile_size

        return possible_coordinates

    def iterate_tiles2(self, min_non_blank_amt=0.0, batch_size=4, print_time=True):
        '''
        A generator that iterates over the tiles within the supplied slide (dictated by self.coordinates)

        :param min_non_blank_amt: tile must have at least this percentage of its pixels "non-blank" ie if the value
        is 0.6, means the tile must have 60%+ of its pixels non-blank
        :param batch_size: get x tiles at once
        :param print_time: for printing out how many tiles/how many to go
        :return: dict containing array of tiles and coordinates
        '''

        if not (0 <= min_non_blank_amt <= 1):
            raise Exception("Minimum non-blank amount must be a percentage between 0.0 and 1.0")

        if batch_size < 1:
            raise Exception('Batch size must be at least 1')

        # initialization
        start_time = time.time()

        # buffer for our batches. will keep updating this each yield
        tiles_buffer = np.zeros((batch_size, self.original_tile_size, self.original_tile_size, self.chn),
                                dtype=np.uint8)
        coordinates_buffer = np.zeros((batch_size, 4), dtype=int)
        buffer_i = 0

        coordinates = list(self.coordinates)
        num_coordinates = len(coordinates)
        while len(coordinates):
            x, y, x2, y2 = coordinates.pop(0)

            # if using the transformed coordinates from homography, need to make sure its valid
            if x < 0 or y < 0:
                self.used_coordinates_mask.append(0)
                continue
            if x2 > self.trimmed_width or y2 > self.trimmed_height:
                self.used_coordinates_mask.append(0)
                continue

            if isinstance(self.slide.image, openslide.OpenSlide):
                tile = np.array(self.slide.image.read_region((x, y), 0, (x2 - x, y2 - y)))[:, :, 2::-1]
            else:
                tile = np.array(self.slide.image.crop((x, y, x2, y2)))[:, :, 2::-1]

            r = 1 / self.tile_size_resize_factor
            if r != 1:
                tile = cv2.resize(tile, (self.original_tile_size, self.original_tile_size))

            # only yield if under maximum blank allowance
            if TileExtractor.amount_blank(tile) <= (1 - min_non_blank_amt):
                top_left_x, top_left_y = int(x * r), int(y * r)
                bot_right_x, bot_right_y = int(x2 * r), int(y2 * r)
                coordinate = (top_left_x, top_left_y, bot_right_x, bot_right_y)

                tiles_buffer[buffer_i] = tile
                coordinates_buffer[buffer_i] = coordinate
                buffer_i += 1

                self.used_coordinates_mask.append(1)

                if buffer_i == batch_size:
                    buffer_i = 0
                    yield {'tiles': tiles_buffer.copy(), 'coordinates': coordinates_buffer.copy()}

            else:
                self.used_coordinates_mask.append(0)

            if print_time:
                if (num_coordinates // 10) and (len(coordinates) % (num_coordinates // 10)) == 0:
                    print("{:0.2f}% ({}/{} cooordinates) in {:0.2f}s".format(
                        (1 - len(coordinates) / num_coordinates) * 100,
                        num_coordinates - len(coordinates),
                        num_coordinates,
                        time.time() - start_time))

        assert len(self.coordinates) == len(self.used_coordinates_mask)

        # may have leftover tiles
        if buffer_i > 0:
            yield {'tiles': tiles_buffer[:buffer_i, :, :, :], 'coordinates': coordinates_buffer[:buffer_i, :]}
