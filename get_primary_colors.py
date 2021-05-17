#!/usr/bin/python

"""Get primary colors from an image.

Finds the specified number of primary colors (averaged for close values)
in the processed image. The result is provided as a list with RGB values.
A graphical representation of the result is also possible.

Functions
---------
get_image
    Read an image in RGB color space.
calculate_image_size
    Calculate new image sizes.
get_primary_colors
    Get primary colors from an image.

References
----------
image_creation.py
    A module is for creating an image based on the results of calculations.
nearest_color.pickle or nearest_color_by_rgb.py
    A serialized file or a module for its creation contains a model that
    maps a color RGB value to its name.
"""

import argparse
import cv2
import numpy as np
import re
from collections import Counter
from nptyping import NDArray
from sklearn.cluster import KMeans
from typing import Any, List, Optional, Tuple

from image_creation import create_output_image

TYPE_ERROR_IMAGE = 'The first argument must be a string'
VALUE_ERROR_IMAGE = 'The image format must be supported by OpenCV'
TYPE_ERROR_NUMBER_OF_COLORS = 'The second argument must be an integer'
VALUE_ERROR_NUMBER_OF_COLORS = 'The second argument must be in the range of 1 to 20'
TYPE_ERROR_CREATE_IMAGE = 'The third argument must be a boolean value'


def get_image(image_path: str) -> NDArray[(Any, Any, 3), np.int]:
    """Read an image in RGB color space."""
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def calculate_image_size(image: NDArray[(Any, Any, 3), np.int],
                         max_size: int = 800) -> Tuple[int, int]:
    """Calculate new image sizes.

    Equate the maximum image size (height or width) to the number
    specified in the max_size parameter, and calculate the remaining
    size in proportion to the original image.

    Parameters
    ----------
    image : np.ndarray((H, W, 3), dtype=int)
        The original image represented as a NumPy array of size H x W x C,
        where H is height, W is width, and C is the number of channels.
    max_size : int, optional
        The value is assigned to the maximum image size (default is
        800 pixels).

    Returns
    -------
    tuple(int, int)
        A tuple of length 2, which contains the new height and
        width of the image.
    """

    height, width = image.shape[0], image.shape[1]
    if max(height, width) < max_size:
        return height, width
    if height > width:
        return max_size, int(max_size * (width / height))
    else:
        return int(max_size * (height / width)), max_size


def get_primary_colors(image: str, number_of_colors: int = 5,
                       create_image: bool = True,
                       output_image_path: Optional[str] = None) \
        -> List[NDArray[(3,), np.int]]:
    """Get primary colors from an image.

    Extracts several (a number equal to the parameter number_of_colors)
    averaged primary colors that dominate the image. Finding the necessary
    colors is done by clustering the pixels of the image with K-Means
    algorithm. Thus, each color obtained is equal to the centroid of the
    corresponding cluster.

    Parameters
    ----------
    image : str
        The path to the image to be processed. The image format must be
        supported by library OpenCV.
    number_of_colors : int, optional
        The number of primary colors to extract from the image. The number
        of found colors must be in the range from 1 to 20. The default is 5.
    create_image : bool, optional
        If this is set to True (default value), this function will
        generate an image that visualizes the distribution of the
        input picture's primary colors.
    output_image_path: None (default) or str
        The path where the resulting image will be saved.
        If the value None (default) is passed, the image will be saved
        in 'examples/output_1.png'.

    Returns
    -------
    list[np.ndarray((3), dtype=int)]
        A list is containing NumPy arrays of three integers. Each array
        corresponds to one of the primary colors of the image and
        represents its RGB value.
    """

    # Checking the types and values of the arguments
    opencv_readable_formats = ['bmp', 'dib', 'jpeg', 'jpg', 'jpe', 'jp2', 'png',
                               'webp', 'pbm', 'pgm', 'ppm', 'pxm', 'pnm', 'pfm',
                               'sr', 'ras', 'tiff', 'tif', 'exr', 'hdr', 'pic']
    formats_str = '|'.join(opencv_readable_formats)

    if not isinstance(image, str):
        raise TypeError(TYPE_ERROR_IMAGE)
    if not re.fullmatch(r'.+\.({})$'.format(formats_str), image):
        raise ValueError(VALUE_ERROR_IMAGE)

    if type(number_of_colors) is not int:
        raise TypeError(TYPE_ERROR_NUMBER_OF_COLORS)
    if not 1 <= number_of_colors <= 20:
        raise ValueError(VALUE_ERROR_NUMBER_OF_COLORS)

    if not isinstance(create_image, bool):
        raise TypeError(TYPE_ERROR_CREATE_IMAGE)

    # Convert the image into a numpy array
    image = get_image(image)

    # Reducing the size of the image to decrease the calculation time
    new_height, new_width = calculate_image_size(image)
    modified_image = cv2.resize(image, (new_height, new_width),
                                interpolation=cv2.INTER_AREA)
    
    modified_image = modified_image.reshape((modified_image.shape[0] *
                                             modified_image.shape[1], 3))
    
    clt = KMeans(n_clusters=number_of_colors, random_state=0)
    labels = clt.fit_predict(modified_image)
    
    # A container keeping the number of items in each cluster
    cluster_capacity = Counter(labels)
    cluster_capacity = dict(sorted(cluster_capacity.items()))
    # A container keeping RGB values for each cluster
    center_colors = np.around(clt.cluster_centers_).astype(int)

    rgb_colors = [center_colors[i] for i in cluster_capacity.keys()]

    if create_image:
        create_output_image(image, cluster_capacity,
                            center_colors, output_image_path)
    
    return rgb_colors


def main():
    # Set the arguments available from the command line
    parser = argparse.ArgumentParser(description='Get primary colors from an image')
    parser.add_argument('--image_path', default='examples/input_1.png',
                        help='The path to the image to be processed')
    parser.add_argument('--number_of_colors', type=int, default=5,
                        help='The number of primary colors to be found')
    parser.add_argument('-i', '--create_image', action='store_false',
                        help='Flag indicating the need to create an image')
    parser.add_argument('--output_image_path', type=str,
                        default='examples/output_1.png',
                        help='The path to the created infographic')
    args = parser.parse_args()

    get_primary_colors(args.image_path, args.number_of_colors,
                       args.create_image, args.output_image_path)


if __name__ == '__main__':
    main()
