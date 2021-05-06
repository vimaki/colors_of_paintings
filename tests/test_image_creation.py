import os
import pytest

from get_primary_colors import get_image
from image_creation import *
from test_get_primary_colors import images

rgb_colors = [np.array([0, 0, 0]), np.array([255, 255, 255]),
              np.array([0, 0, 255]), np.array([128, 0, 128]),
              np.array([11, 122, 233])]

cluster_capacity = [{0: 5},
                    {0: 5, 1: 10},
                    {0: 3, 1: 11, 2: 43, 3: 23, 4: 7}]

center_colors = [np.array([[255, 0, 0]]),
                 np.array([[255, 0, 0], [0, 255, 0]]),
                 np.array([[0, 0, 0], [50, 0, 0], [0, 50, 0],
                           [0, 0, 50], [50, 50, 50]])]

labels_for_colors = [['100.0 % - #FF0000 - Red'],

                     ['33.3 % - #FF0000 - Red', '66.7 % - #00FF00 - Lime'],

                     ['3.4 % - #000000 - Black', '12.6 % - #320000 - Chocolate',
                      '49.4 % - #003200 - Deep Fir', '26.4 % - #000032 - Black Rock',
                      '8.0 % - #323232 - Mine Shaft']]


@pytest.fixture(scope='module')
def color_features(request):
    return get_color_features(*request.param)


@pytest.fixture(scope='function')
def loaded_image(request):
    image = get_image(request.param)
    yield image
    os.remove('tests/infrastructure/output_image.jpg')


class TestRGB2HEX:

    @pytest.mark.parametrize('color', rgb_colors)
    def test_rgb2hex_type(self, color):
        hex_code = rgb2hex(color)
        assert isinstance(hex_code, str)

    @pytest.mark.parametrize('color', rgb_colors)
    def test_rgb2hex_length(self, color):
        hex_code = rgb2hex(color)
        assert len(hex_code) == 7

    @pytest.mark.parametrize('color', rgb_colors)
    def test_rgb2hex_hash_sign(self, color):
        hex_code = rgb2hex(color)
        assert hex_code.startswith('#')

    @pytest.mark.parametrize('color', rgb_colors)
    def test_rgb2hex_content(self, color):
        hex_code = rgb2hex(color)
        hex_letters = ['A', 'B', 'C', 'D', 'E', 'F']
        assert all(map(lambda x: x.isnumeric() or x in hex_letters,
                       hex_code[1:]))


class TestGetColourName:

    @pytest.mark.parametrize('color', rgb_colors)
    def test_get_colour_name_type(self, color):
        color_name = get_colour_name(color)
        assert isinstance(color_name, str)

    @pytest.mark.parametrize('color', rgb_colors)
    def test_get_colour_name_content(self, color):
        color_name = get_colour_name(color)
        assert all(char.isalpha() or char.isspace() for char in color_name)

    @pytest.mark.parametrize('color, expected_name',
                             zip(rgb_colors, ['Black', 'White', 'Blue',
                                              'Purple', 'Azure Radiance']))
    def test_get_colour_name_values(self, color, expected_name):
        color_name = get_colour_name(color)
        assert color_name == expected_name


class TestGetColorFeatures:

    @pytest.mark.parametrize('capacities, centers',
                             zip(cluster_capacity, center_colors))
    def test_get_color_features_percentages_length(self, capacities, centers):
        percentages, *_ = get_color_features(capacities, centers)
        assert len(capacities) == len(percentages)

    @pytest.mark.parametrize('capacities, centers',
                             zip(cluster_capacity, center_colors))
    def test_get_color_features_hex_codes_length(self, capacities, centers):
        _, hex_codes, _ = get_color_features(capacities, centers)
        assert len(capacities) == len(hex_codes)

    @pytest.mark.parametrize('capacities, centers',
                             zip(cluster_capacity, center_colors))
    def test_get_color_features_names_length(self, capacities, centers):
        *_, names = get_color_features(capacities, centers)
        assert len(capacities) == len(names)

    @pytest.mark.parametrize('capacities, centers',
                             zip(cluster_capacity, center_colors))
    def test_get_color_features_percentages_type(self, capacities, centers):
        percentages, *_ = get_color_features(capacities, centers)
        assert all(isinstance(el, float) for el in percentages)

    @pytest.mark.parametrize('capacities, centers',
                             zip(cluster_capacity, center_colors))
    def test_get_color_features_hex_codes_type(self, capacities, centers):
        _, hex_codes, _ = get_color_features(capacities, centers)
        assert all(isinstance(el, str) for el in hex_codes)

    @pytest.mark.parametrize('capacities, centers',
                             zip(cluster_capacity, center_colors))
    def test_get_color_features_names_type(self, capacities, centers):
        *_, names = get_color_features(capacities, centers)
        assert all(isinstance(el, str) for el in names)

    @pytest.mark.parametrize('capacities, centers',
                             zip(cluster_capacity, center_colors))
    def test_get_color_features_percentages_sum(self, capacities, centers):
        percentages, *_ = get_color_features(capacities, centers)
        assert sum(percentages) == 1.


class TestCreateLabels:

    @pytest.mark.parametrize('color_features',
                             zip(cluster_capacity, center_colors),
                             indirect=True)
    def test_create_labels_elementwise_type(self, color_features):
        labels = create_labels(*color_features)
        assert all(isinstance(label, str) for label in labels)

    @pytest.mark.parametrize('color_features, expected_labels',
                             zip(zip(cluster_capacity, center_colors),
                                 labels_for_colors),
                             indirect=['color_features'])
    def test_create_labels_content(self, color_features, expected_labels):
        labels = create_labels(*color_features)
        assert labels == expected_labels


class TestPlotColorBar:

    @pytest.mark.parametrize('color_features, center',
                             zip(zip(cluster_capacity, center_colors),
                                 center_colors),
                             indirect=['color_features'])
    def test_plot_color_bar_type(self, color_features, center):
        bar = plot_color_bar(color_features[0], center)
        assert isinstance(bar, np.ndarray)

    @pytest.mark.parametrize('color_features, center',
                             zip(zip(cluster_capacity, center_colors),
                                 center_colors),
                             indirect=['color_features'])
    def test_plot_color_bar_elementwise_type(self, color_features, center):
        bar = plot_color_bar(color_features[0], center)
        assert np.issubdtype(bar.dtype, np.integer)

    @pytest.mark.parametrize('color_features, center',
                             zip(zip(cluster_capacity, center_colors),
                                 center_colors),
                             indirect=['color_features'])
    def test_plot_color_bar_dimensions(self, color_features, center):
        bar = plot_color_bar(color_features[0], center)
        assert bar.ndim == 3

    @pytest.mark.parametrize('color_features, center',
                             zip(zip(cluster_capacity, center_colors),
                                 center_colors),
                             indirect=['color_features'])
    def test_plot_color_bar_shapes(self, color_features, center):
        bar = plot_color_bar(color_features[0], center)
        assert bar.shape[0] == 50
        assert bar.shape[1] == 300
        assert bar.shape[2] == 3

    @pytest.mark.parametrize('color_features, center',
                             zip(zip(cluster_capacity, center_colors),
                                 center_colors),
                             indirect=['color_features'])
    def test_plot_color_bar_values(self, color_features, center):
        bar = plot_color_bar(color_features[0], center)
        assert np.all((bar >= 0) & (bar <= 255))


class TestCreateOutputImage:

    @pytest.mark.parametrize('loaded_image, capacity, center',
                             zip(images, 2 * cluster_capacity, 2 * center_colors),
                             indirect=['loaded_image'])
    def test_create_output_image_exist(self, loaded_image, capacity, center):
        create_output_image(loaded_image, capacity, center,
                            image_path='tests/infrastructure/output_image.jpg')
        assert os.path.exists('tests/infrastructure/output_image.jpg')
