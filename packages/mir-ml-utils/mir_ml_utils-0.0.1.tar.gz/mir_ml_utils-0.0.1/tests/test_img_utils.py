import unittest

from src.config import TESTING_DATA_DIR
from src.data_handlers.img_utils import load_img
from src.data_handlers.img_utils import get_img_files


class TestImgUtils(unittest.TestCase):

    def test_load_img(self):
        img_path = TESTING_DATA_DIR / "hull001_label.jpg"
        img = load_img(path=img_path, transformer=None)

        self.assertEqual(img.size[0], 3799)
        self.assertEqual(img.size[1], 2256)

    def test_get_img_files_empty_list(self):
        img_path = TESTING_DATA_DIR

        img_files = get_img_files(img_dir=img_path, img_formats=[])
        self.assertEqual(len(img_files), 0)

    def test_get_img_files_with_jpg(self):
        img_path = TESTING_DATA_DIR

        img_files = get_img_files(img_dir=img_path, img_formats=['jpg'])
        self.assertEqual(len(img_files), 1)

    def test_get_img_files_with_jpg_png(self):
        img_path = TESTING_DATA_DIR

        img_files = get_img_files(img_dir=img_path, img_formats=['jpg', 'png'])
        self.assertEqual(len(img_files), 2)


if __name__ == '__main__':
    unittest.main()
