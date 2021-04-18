"""Creating an image with the results of calculating the primary colors.

Functions
---------
rgb2hex
    Representation of RGB color in HEX format.
get_colour_name
    Matches the RGB value of a color to its name.
get_color_features
    Determining the necessary representations of the colors provided.
create_labels
    Concatenates different color information into a single label.
plot_color_bar
    Creating an image with the results of calculating the primary colors.

References
----------
nearest_color.pickle or nearest_color_by_rgb.py
    A serialized file or a module for its creation contains a model that
    maps a color RGB value to its name.
"""

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pickle
import webcolors
from matplotlib.patches import Patch
from nptyping import NDArray
from typing import Any, Dict, List, Tuple


def rgb2hex(color: NDArray[(3,), np.int]) -> str:
    """Representation of RGB color in HEX format."""
    return "#{:02X}{:02X}{:02X}".format(color[0], color[1], color[2])


def get_colour_name(requested_colour: NDArray[(3,), np.int]) -> str:
    """Matches the RGB value of a color to its name.

    Using the third-party library Webcolors determines from the RGB
    color value the appropriate name. If a color name is not found
    in this way, find the name closest by RGB value from a large list
    of color names "rgb_color_names.csv" using the kNN algorithm.

    Parameters
    ----------
    requested_colour : np.ndarray((3), dtype=int)
        RGB value of color.

    Returns
    -------
    str
        The exact or closest name of the color.
    """

    try:
        # noinspection PyTypeChecker
        color_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        # The name is not found with Webcolors, so we use the kNN algorithm
        with open('nearest_color.pickle', 'rb') as f:
            nearest_color = pickle.load(f)
            color_name = nearest_color.predict([requested_colour])[0]
    return color_name


def get_color_features(cluster_capacity: Dict[int, int],
                       center_colors: NDArray[(Any, 3), np.int]) -> \
        Tuple[List[float], List[str], List[str]]:
    """Determining the necessary representations of the colors provided.

    Based on the RGB values and frequency of colors in the image,
    the percentage of colors, HEX values, and names of colors are found.
    This data is needed to visualize the results of the calculations.

    Parameters
    ----------
    cluster_capacity : dict[int, int]
        A container is storing the number of pixels belonging to each
        of the primary colors of the image.
    center_colors : np.ndarray((N, 3), dtype=int)
        A container is storing the RGB values of each of the primary
        colors of the image.

    Returns
    -------
    list[float]
        A list with the percentages of the primary colors of the image.
    list[str]
        A list with the HEX values of the primary colors of the image.
    list[str]
        A list with the names of the primary colors of the image.
    """

    # We get ordered colors by iterating through the keys
    ordered_colors = [center_colors[i] for i in cluster_capacity.keys()]
    pixel_number = sum(cluster_capacity.values())
    ratio_colors = [cluster_capacity[i] / pixel_number
                    for i in cluster_capacity.keys()]
    hex_colors = [rgb2hex(ordered_colors[i])
                  for i in cluster_capacity.keys()]
    name_colors = [get_colour_name(ordered_colors[i])
                   for i in cluster_capacity.keys()]
    return ratio_colors, hex_colors, name_colors


def create_labels(ratio_colors: List[float], hex_colors: List[str],
                  name_colors: List[str]) -> List[str]:
    """Concatenates different color information into a single label."""
    percent_colors = list(map(lambda x: str(round(x * 100, 1)) + ' %',
                              ratio_colors))
    labels = list(map(' - '.join,
                      zip(percent_colors, hex_colors, name_colors)))
    return labels


def plot_color_bar(ratio_colors: List[float],
                   center_colors: NDArray[(Any, 3), np.int]) -> np.ndarray:
    """Create a custom bar plot of color distribution.

    Parameters
    ----------
    ratio_colors : list[float]
        A list with the percentages of the primary colors of the image.
    center_colors : np.ndarray((N, 3), dtype=int)
        A container is storing the RGB values of each of the primary
        colors of the image.

    Returns
    -------
    np.ndarray((50, 300, 3), dtype=uint)
        A NumPy array that can be converted into an image that represents
        a bar plot of color distribution.
    """

    bar = np.zeros((50, 300, 3), dtype="uint8")
    start_point = 0

    for (ratio, color) in zip(ratio_colors, center_colors):
        end_point = start_point + (ratio * 300)
        cv2.rectangle(bar, (int(start_point), 0), (int(end_point), 50),
                      color.astype("uint8").tolist(), -1)
        start_point = end_point

    return bar


def create_output_image(image: NDArray[(Any, Any, 3), np.int],
                        cluster_capacity: Dict[int, int],
                        center_colors: NDArray[(Any, 3), np.int]) -> None:
    """Creating an image with the results of calculating the primary colors.

    Creates an image which is consisting of three parts arranged
    vertically, one after the other. At the top is the original image.
    The middle part contains a custom bar plot showing the distribution
    of the averaged primary colors of the image. The bottom part
    contains a legend to the plot, showing the percentage of colors,
    their HEX values, and names.

    Parameters
    ----------
    image : np.ndarray((H, W, 3), dtype=int)
        The original image represented as a NumPy array of size H x W x C,
        where H is height, W is width, and C is the number of channels.
    cluster_capacity : dict[int, int]
        A container is storing the number of pixels belonging to each
        of the primary colors of the image.
    center_colors : np.ndarray((N, 3), dtype=int)
        A container is storing the RGB values of each of the primary
        colors of the image (number of colors equals N).

    Returns
    -------
    None
    """

    plt.ioff()
    output_image = plt.figure(figsize=(10, 12))

    ratio_colors, hex_colors, name_colors = get_color_features(
        cluster_capacity, center_colors)

    # Output of the processed image
    plt.subplot2grid((7, 1), (0, 0), rowspan=4)
    plt.axis('off')
    plt.imshow(image)

    # The output of selected colors with respect to the proportions
    plt.subplot2grid((7, 1), (4, 0))
    bar = plot_color_bar(ratio_colors, center_colors)
    plt.axis('off')
    plt.imshow(bar)

    # Description of the resulting colors
    plt.subplot2grid((7, 1), (5, 0), rowspan=2)
    labels = create_labels(ratio_colors, hex_colors, name_colors)
    plt.axis('off')
    legend_elements = [Patch(facecolor=i) for i in hex_colors]
    column_number = 1 if len(cluster_capacity) < 11 else 2
    plt.legend(handles=legend_elements, labels=labels, loc='upper center',
               frameon=False, fontsize='large', ncol=column_number)

    plt.tight_layout(h_pad=5.0)
    plt.savefig('examples/output_1.png')
    plt.close(output_image)
