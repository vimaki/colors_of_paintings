"""Matches the RGB value of a color to its name.

Finds the nearest color name by the given RGB value using the kNN algorithm.
The resulting model is serialized and loaded into file nearest_color.pickle.

References
----------
rgb_color_names.csv
    A file containing a table in which each line contains RGB color values
    and the corresponding name. The number of described colors is 1567.
"""

import pandas as pd
import pickle
from sklearn.neighbors import KNeighborsClassifier


def main():
    map_rgb_to_color_name = pd.read_csv('rgb_color_names.csv')
    rgb = map_rgb_to_color_name.iloc[:, :-1].values
    color_name = map_rgb_to_color_name.iloc[:, -1].values

    model_knn = KNeighborsClassifier(n_neighbors=1)
    model_knn.fit(rgb, color_name)

    with open('nearest_color.pickle', 'wb') as f:
        pickle.dump(model_knn, f)


if __name__ == '__main__':
    main()
