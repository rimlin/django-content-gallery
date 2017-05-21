import os

from django.test import TestCase, mock

from .. import utils
from .. import settings

from .utils import create_image_file, get_image_size

class TestGetChoicesUrlPattern(TestCase):

    def test_removing_pk(self):
        url = utils.get_choices_url_pattern()
        self.assertEqual(url, '/gallery/ajax/choices/')


class TestCalculateImageSize(TestCase):

    max_size = (100, 100)

    def test_larger_width(self):
        size = utils.calculate_image_size((200, 100), self.max_size)
        self.assertEqual(size[0], 100)
        self.assertEqual(size[1], 50)

    def test_larger_height(self):
        size = utils.calculate_image_size((100, 200), self.max_size)
        self.assertEqual(size[0], 50)
        self.assertEqual(size[1], 100)

    def test_larger_size(self):
        size = utils.calculate_image_size((200, 200), self.max_size)
        self.assertEqual(size[0], 100)
        self.assertEqual(size[1], 100)

    def test_same_size(self):
        size = utils.calculate_image_size(self.max_size, self.max_size)
        self.assertEqual(size[0], 100)
        self.assertEqual(size[1], 100)

    def test_smaller_size(self):
        size = utils.calculate_image_size((50, 50), self.max_size)
        self.assertEqual(size[0], 50)
        self.assertEqual(size[1], 50)


class TestFilenameUtils(TestCase):

    def test_get_ext_single(self):
        ext = utils.get_ext('foo.jpg')
        self.assertEqual(ext, '.jpg')

    def test_get_ext_double(self):
        ext = utils.get_ext('foo.bar.jpg')
        self.assertEqual(ext, '.jpg')

    def test_get_ext_none(self):
        ext = utils.get_ext('filename')
        self.assertEqual(ext, '')

    def test_get_ext_path(self):
        ext = utils.get_ext('/path/to/foo.jpg')
        self.assertEqual(ext, '.jpg')

    def test_get_name_single(self):
        name = utils.get_name('foo.jpg')
        self.assertEqual(name, 'foo')

    def test_get_name_double(self):
        name = utils.get_name('foo.bar.jpg')
        self.assertEqual(name, 'foo.bar')

    def test_get_filename_none(self):
        name = utils.get_name('foo')
        self.assertEqual(name, 'foo')

    def test_get_name_path(self):
        name = utils.get_name('/path/to/foo.jpg')
        self.assertEqual(name, '/path/to/foo')

    @mock.patch('gallery.settings.GALLERY_PATH', 'gallery')
    @mock.patch('gallery.settings.MEDIA_ROOT', '/media')
    def test_create_path(self):
        path = utils.create_path('foo.jpg')
        self.assertEqual(path, '/media/gallery/foo.jpg')

    @mock.patch('gallery.settings.GALLERY_PATH', 'gallery')
    @mock.patch('gallery.settings.MEDIA_ROOT', '/media/')
    def test_create_path_right_slash_in_media_root(self):
        path = utils.create_path('foo.jpg')
        self.assertEqual(path, '/media/gallery/foo.jpg')

    @mock.patch('gallery.settings.GALLERY_PATH', 'gallery/')
    @mock.patch('gallery.settings.MEDIA_ROOT', '/media')
    def test_create_path_slash_in_gallery_path(self):
        path = utils.create_path('foo.jpg')
        self.assertEqual(path, '/media/gallery/foo.jpg')

    @mock.patch('gallery.settings.GALLERY_PATH', 'gallery/')
    @mock.patch('gallery.settings.MEDIA_ROOT', '/media/')
    def test_create_path_slash_in_both(self):
        path = utils.create_path('foo.jpg')
        self.assertEqual(path, '/media/gallery/foo.jpg')

    @mock.patch('gallery.settings.GALLERY_PATH', 'gallery')
    @mock.patch('gallery.settings.MEDIA_URL', '/media/')
    def test_create_url(self):
        url = utils.create_url('foo.jpg')
        self.assertEqual(url, '/media/gallery/foo.jpg')

    @mock.patch('gallery.settings.GALLERY_PATH', '/gallery')
    @mock.patch('gallery.settings.MEDIA_URL', '/media/')
    def test_create_url_left_slash_in_gallery_path(self):
        url = utils.create_url('foo.jpg')
        self.assertEqual(url, '/media/gallery/foo.jpg')

    @mock.patch('gallery.settings.GALLERY_PATH', 'gallery/')
    @mock.patch('gallery.settings.MEDIA_URL', '/media/')
    def test_create_url_right_slash_in_gallery_path(self):
        url = utils.create_url('foo.jpg')
        self.assertEqual(url, '/media/gallery/foo.jpg')

    @mock.patch('gallery.settings.GALLERY_PATH', '/gallery/')
    @mock.patch('gallery.settings.MEDIA_URL', '/media/')
    def test_create_url_slashes_in_gallery_path(self):
        url = utils.create_url('foo.jpg')
        self.assertEqual(url, '/media/gallery/foo.jpg')

    @mock.patch('gallery.settings.GALLERY_PATH', '/gallery')
    @mock.patch('gallery.settings.MEDIA_URL', '/media')
    def test_create_url_no_right_slash_in_media_url(self):
        url = utils.create_url('foo.jpg')
        self.assertEqual(url, '/media/gallery/foo.jpg')

    @mock.patch('gallery.settings.GALLERY_PATH', 'gallery')
    def test_create_name_in_db(self):
        name = utils.name_in_db('foo.jpg')
        self.assertEqual(name, 'gallery/foo.jpg')

    @mock.patch('gallery.settings.GALLERY_PATH', 'gallery/')
    def test_create_name_in_db_right_slash(self):
        name = utils.name_in_db('foo.jpg')
        self.assertEqual(name, 'gallery/foo.jpg')

    @mock.patch('django.conf.settings.STATIC_URL', '/static/')
    def test_create_static_url(self):
        name = utils.create_static_url('gallery/foo.jpg')
        self.assertEqual(name, '/static/gallery/foo.jpg')


class TestImageUtils(TestCase):

    image_path = os.path.join(settings.MEDIA_ROOT, 'foo.jpg')

    def setUp(self):
        create_image_file(self.image_path)

    def tearDown(self):
        os.remove(self.image_path)

    def test_resize_image_same_size(self):
        utils.image_resize(self.image_path, self.image_path, (100, 100))
        size = get_image_size(self.image_path)
        self.assertEqual(size[0], 100)
        self.assertEqual(size[1], 100)

    def test_resize_image_smaller_width(self):
        utils.image_resize(self.image_path, self.image_path, (50, 100))
        size = get_image_size(self.image_path)
        self.assertEqual(size[0], 50)
        self.assertEqual(size[1], 50)

    def test_resize_image_smaller_height(self):
        utils.image_resize(self.image_path, self.image_path, (100, 50))
        size = get_image_size(self.image_path)
        self.assertEqual(size[0], 50)
        self.assertEqual(size[1], 50)

    def test_resize_image_smaller_size(self):
        utils.image_resize(self.image_path, self.image_path, (50, 50))
        size = get_image_size(self.image_path)
        self.assertEqual(size[0], 50)
        self.assertEqual(size[1], 50)

    def test_create_in_memory_image(self):
        img = utils.create_in_memory_image(self.image_path, 'foo', (50, 50))
        size = get_image_size(img)
        self.assertEqual(img.name, 'foo')
        self.assertEqual(size[0], 50)
        self.assertEqual(size[1], 50)



class TestCreateImageData(TestCase):

    @mock.patch('gallery.settings.GALLERY_IMAGE_WIDTH', 1024)
    @mock.patch('gallery.settings.GALLERY_IMAGE_HEIGHT', 768)
    @mock.patch('gallery.settings.GALLERY_SMALL_IMAGE_WIDTH', 800)
    @mock.patch('gallery.settings.GALLERY_SMALL_IMAGE_HEIGHT', 600)
    def test_create_image_data(self):
        image = mock.MagicMock()
        image.image_url = 'foo'
        image.small_image_url = 'bar'
        data = utils.create_image_data(image)
        self.assertEqual(data['image']['url'], 'foo')
        self.assertEqual(data['image']['width'], 1024)
        self.assertEqual(data['image']['height'], 768)
        self.assertEqual(data['small_image']['url'], 'bar')
        self.assertEqual(data['small_image']['width'], 800)
        self.assertEqual(data['small_image']['height'], 600)