import unittest
import pytest

from src.data_handlers.images_dataset import ImagesDataset
from src.config import TESTING_DATA_DIR
from src.utils.exceptions import SizeMismatchException
from src.data_handlers.img_utils import get_img_files


class TestImagesDataset(unittest.TestCase):

    def test_build_from_file_sources_invalid_data_sizes(self):

        with pytest.raises(SizeMismatchException) as exe:

            filenames = []
            labels = [0, 1]
            ImagesDataset.from_file_sources(filenames=filenames, labels=labels)
            self.assertEqual(str(exe), "Size {0} != {1}".format(len(filenames), len(labels)))

    def test_build_from_file_sources(self):

        filenames = get_img_files(img_dir=TESTING_DATA_DIR / "prototypical_net_test_data" / "inference")

        self.assertEqual(len(filenames), 4)

        labels = [1, 1, 1, 1]
        dataset = ImagesDataset.from_file_sources(filenames=filenames, labels=labels)

        self.assertEqual(len(dataset), len(labels))
        self.assertEqual(dataset.n_classes, 1)


if __name__ == '__main__':
    unittest.main()
