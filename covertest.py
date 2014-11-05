__author__ = 'Exter'

import unittest
from pycover import ImageHeader

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(False, False)

class ImageHeaderTestCase(unittest.TestCase):

    def readHeader(self, name):
        f = open(name, 'rb')
        data = f.read(11)
        f.close()
        return data

    def test_bmp(self):
        data = self.readHeader('C:\Users\Exter\Downloads\\aaaa.bmp')
        ih = ImageHeader(data)
        self.assertTrue(ih.Check(), 'this is not supported image')
        self.assertTrue(ih.type == 'BMP', 'this is not BMP image')

    def test_gif(self):
        data = self.readHeader('C:\Users\Exter\Downloads\\aaaa.gif')
        ih = ImageHeader(data)
        self.assertTrue(ih.Check(), 'this is not supported image')
        self.assertTrue(ih.type == 'GIF', 'this is not GIF image')

    def test_jpg(self):
        data = self.readHeader('C:\Users\Exter\Downloads\\aaaa.jpg')
        ih = ImageHeader(data)
        self.assertTrue(ih.Check(), 'this is not supported image')
        self.assertTrue(ih.type == 'JPG', 'this is not JPG image')

    def test_png(self):
        data = self.readHeader('C:\Users\Exter\Downloads\\aaaa.png')
        ih = ImageHeader(data)
        self.assertTrue(ih.Check(), 'this is not supported image')
        self.assertTrue(ih.type == 'PNG', 'this is not PNG image')

    def test_fail_ok(self):
        data = self.readHeader('C:\Users\Exter\Downloads\\aaaa.mobi')
        ih = ImageHeader(data)
        self.assertFalse(ih.Check(), 'this is supported image %s' % ih.Check() )
        self.assertTrue(ih.type == '', 'there should be no image type')


if __name__ == '__main__':
    unittest.main()
