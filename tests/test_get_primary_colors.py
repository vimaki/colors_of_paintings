import pytest

from get_primary_colors import *

images = ['tests/infrastructure/image_1.png',
          'tests/infrastructure/image_2.webp',
          'tests/infrastructure/image_3.bmp',
          'tests/infrastructure/image_4.tiff',
          'tests/infrastructure/image_5.jpeg',
          'tests/infrastructure/image_6.exr']

images_as_arrays = [np.random.randint(0, 255, size=(1000, 800, 3)),
                    np.random.randint(0, 255, size=(777, 1000, 3)),
                    np.random.randint(0, 255, size=(1000, 500, 3)),
                    np.random.randint(0, 255, size=(500, 500, 3)),
                    np.random.randint(0, 255, size=(1000, 400, 3)),
                    np.random.randint(0, 255, size=(400, 300, 3))]


class TestGetImage:

    @pytest.mark.parametrize('image', images)
    def test_get_image_output_type(self, image):
        img = get_image(image)
        assert isinstance(img, np.ndarray)

    @pytest.mark.parametrize('image', images)
    def test_get_image_output_elementwise_type(self, image):
        img = get_image(image)
        assert np.issubdtype(img.dtype, np.integer)

    @pytest.mark.parametrize('image', images)
    def test_get_image_dimensions(self, image):
        img = get_image(image)
        assert img.ndim == 3

    @pytest.mark.parametrize('image', images)
    def test_get_image_channels(self, image):
        img = get_image(image)
        assert img.shape[2] == 3

    @pytest.mark.parametrize('image, expected_shape',
                             zip(images, [(904, 889), (1500, 3270), (830, 976),
                                          (4032, 3024), (1946, 2008)]))
    def test_get_image_shape(self, image, expected_shape):
        img = get_image(image)
        assert img.shape[0], img.shape[1] == expected_shape

    @pytest.mark.parametrize('image', images)
    def test_get_image_values(self, image):
        img = get_image(image)
        assert np.all((img >= 0) & (img <= 255))


class TestCalculateImageSize:

    @pytest.mark.parametrize('array', images_as_arrays)
    def test_calculate_image_size_length(self, array):
        length = len(calculate_image_size(array))
        assert length == 2

    @pytest.mark.parametrize('array', images_as_arrays)
    def test_calculate_image_size_elementwise_type(self, array):
        sizes = calculate_image_size(array)
        assert all(isinstance(size, int) for size in sizes)

    @pytest.mark.parametrize('array', images_as_arrays)
    def test_calculate_image_size_positive(self, array):
        sizes = calculate_image_size(array)
        assert all(map(lambda size: size > 0, sizes))

    @pytest.mark.parametrize('array', images_as_arrays)
    def test_calculate_image_size_max(self, array):
        sizes = calculate_image_size(array, 500)
        assert max(sizes) <= 500

    @pytest.mark.parametrize('array, expected_sizes',
                             zip(images_as_arrays, [(500, 400), (388, 500),
                                                    (500, 250), (500, 500),
                                                    (500, 200), (400, 300)]))
    def test_calculate_image_size_output(self, array, expected_sizes):
        sizes = calculate_image_size(array, 500)
        assert sizes == expected_sizes


class TestGetPrimaryColors:

    @pytest.mark.parametrize('image_path', [1, 1.1, True, ('image.png',)])
    def test_get_primary_colors_image_type(self, image_path):
        with pytest.raises(TypeError) as exc_info:
            get_primary_colors(image_path, create_image=False)
        assert str(exc_info.value) == TYPE_ERROR_IMAGE

    @pytest.mark.parametrize('image_path',
                             ['image', 'image.pdf', 'image.psd', 'image.gif',
                              'image.eps', 'image.ai', 'image.svg', 'image.raw',
                              'image.cdr', 'image.jpegbmp'])
    def test_get_primary_colors_image_value(self, image_path):
        with pytest.raises(ValueError) as exc_info:
            get_primary_colors(image_path, create_image=False)
        assert str(exc_info.value) == VALUE_ERROR_IMAGE

    @pytest.mark.parametrize('number_of_colors', ['3', 3.0, True, (3,)])
    def test_get_primary_colors_number_of_colors_type(self, number_of_colors):
        with pytest.raises(TypeError) as exc_info:
            get_primary_colors(images[0], number_of_colors, create_image=False)
        assert str(exc_info.value) == TYPE_ERROR_NUMBER_OF_COLORS

    @pytest.mark.parametrize('number_of_colors', [-1, 0, 50])
    def test_get_primary_colors_number_of_colors_value(self, number_of_colors):
        with pytest.raises(ValueError) as exc_info:
            get_primary_colors(images[0], number_of_colors, create_image=False)
        assert str(exc_info.value) == VALUE_ERROR_NUMBER_OF_COLORS

    @pytest.mark.parametrize('create_image', ['True', 1, 1.0, (True,)])
    def test_get_primary_colors_create_image_type(self, create_image):
        with pytest.raises(TypeError) as exc_info:
            get_primary_colors(images[0], create_image=create_image)
        assert str(exc_info.value) == TYPE_ERROR_CREATE_IMAGE

    @pytest.mark.parametrize('n_colors', [1, 5, 10])
    def test_get_primary_colors_output_length(self, n_colors):
        colors = get_primary_colors(images[0], number_of_colors=n_colors,
                                    create_image=False)
        assert len(colors) == n_colors

    @pytest.mark.parametrize('image', images)
    def test_get_primary_colors_output_elements_length(self, image):
        colors = get_primary_colors(image, number_of_colors=3, create_image=False)
        assert all(len(elem) == 3 for elem in colors)

    @pytest.mark.parametrize('image', images)
    def test_get_primary_colors_output_elementwise_type(self, image):
        colors = get_primary_colors(image, number_of_colors=3, create_image=False)
        assert all(np.issubdtype(elem.dtype, np.integer) for elem in colors)

    @pytest.mark.parametrize('image', images)
    def test_get_primary_colors_values(self, image):
        colors = get_primary_colors(image, number_of_colors=3, create_image=False)
        assert all([np.all((color >= 0) & (color <= 255)) for color in colors])
