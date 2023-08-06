import unittest
import pytest

from src.data_handlers.img_pipeline import ImgPipeline, ImgPipelineItem


def dummy_pipeline_item(img, *args):
    pass


class TestImgPipeline(unittest.TestCase):

    def test_ops_list_is_none(self):
        pipe_line = ImgPipeline(ops_list=None, image=None)

        with pytest.raises(ValueError) as ex:
            pipe_line()

            self.assertEqual(str(ex), "The ops_list is empty for this pipeline")

    def test_ops_list_is_empty(self):
        pipe_line = ImgPipeline(ops_list=[], image=None)

        with pytest.raises(ValueError) as ex:
            pipe_line()

            self.assertEqual(str(ex), "The ops_list is empty for this pipeline")

    def test_ops_source_image_empty(self):
        pipe_line = ImgPipeline(ops_list=[ImgPipelineItem(dummy_pipeline_item, [])], image=None)

        with pytest.raises(ValueError) as ex:
            pipe_line()

            self.assertEqual(str(ex), "The source image for this pipeline has not been specified")


if __name__ == '__main__':
    unittest.main()