import os
from pathlib import Path
from typing import List

from src.data_handlers.img_utils import remove_metadata_from_image
from src.data_handlers.img_utils import load_images, get_img_files, load_img
from src.data_handlers.img_utils import load_images_from_paths


class RemoveImgMetaData(object):

    def __init__(self, input_dir: Path,
                 output_dir: Path,
                 img_formats: List[str] = ['jpg', 'png', 'jpeg'],
                 do_run: bool = True,
                 **kwargs):

        self.input_dir = input_dir
        self.output_dir = output_dir
        self.img_formats = img_formats
        self.args = kwargs

        if do_run:
            self.run()

    def run(self):

        if not os.path.exists(self.output_dir) and self.args['do_create_dir']:
            os.makedirs(self.output_dir)

        if 'chunk_size' in self.args:
            return self.load_using_chunk()

        if 'keep_image_filename' in self.args:

            img_files = get_img_files(img_dir=self.input_dir,
                                      img_formats=self.img_formats)

            if len(img_files) == 0:
                raise ValueError(f"{self.input_dir} does  not have images with formats {self.img_formats}")

            # collect the images
            images = []
            # load every image in the Path
            for img in img_files:
                images.append(load_img(path=img,
                                       transformer=self.args['transformer'] if 'transformer' in self.args else None,
                                       loader=self.args['loader'] if 'transformer' in self.args else 'PIL'))

            for img_file, img in zip(img_files, images):
                img_filename = img_file.split('/')[-1]
                new_filename = Path(str(self.output_dir)) / img_filename
                remove_metadata_from_image(image=img, new_filename=new_filename)
        else:

            images = load_images(path=self.input_dir,
                                 img_formats=self.img_formats,
                                 loader='PIL',
                                 transformer=self.args['transformer'] if 'transformer' in self.args else None)

            new_img_format = self.args['new_img_format'] if 'new_img_format' in self.args else 'jpg'
            for i, img in enumerate(images):
                img_filename = f'img_{i}.{new_img_format}'
                new_filename = Path(str(self.output_dir)) / img_filename
                remove_metadata_from_image(image=img, new_filename=new_filename)

    def __call__(self, *args, **kwargs):
        return self.run()

    def load_using_chunk(self):

        img_files = get_img_files(img_dir=self.input_dir,
                                  img_formats=self.img_formats)

        if len(img_files) == 0:
            raise ValueError(f"{self.input_dir} does  not have images with formats {self.img_formats}")

        def get_chuncks(images: List[Path], n: int):
            # looping till length l
            for i in range(0, len(images), n):
                yield images[i:i + n]

        # get the image file chuncks
        img_files = list(get_chuncks(img_files, n=self.args['chunk_size']))

        if 'keep_image_filename' in self.args:

            for image_file_chunck in img_files:

                # collect the images in the chunck
                images = []
                for img in image_file_chunck:

                    # load every image in the Path
                    images.append(load_img(path=img,
                                           transformer=self.args['transformer'] if 'transformer' in self.args else None,
                                           loader=self.args['loader'] if 'loader' in self.args else 'PIL'))

                for img_file, img in zip(image_file_chunck, images):
                    img_filename = str(img_file).split('/')[-1]
                    new_filename = Path(str(self.output_dir)) / img_filename
                    remove_metadata_from_image(image=img, new_filename=new_filename)
        else:

            counter = 0
            for i, image_file_chunck in enumerate(img_files):

                images = load_images_from_paths(imgs=image_file_chunck,
                                                loader='PIL',
                                                transformer=self.args['transformer'] if 'transformer' in self.args else None)

                if 'verbose' in self.args:
                    print(f"Working on batch {i} of {len(img_files)}. Images found {len(images)}")

                new_img_format = self.args['new_img_format'] if 'new_img_format' in self.args else 'jpg'
                for j, img in enumerate(images):
                    img_filename = f'img_{counter}.{new_img_format}'
                    new_filename = Path(str(self.output_dir)) / img_filename
                    remove_metadata_from_image(image=img, new_filename=new_filename)
                    counter += 1







