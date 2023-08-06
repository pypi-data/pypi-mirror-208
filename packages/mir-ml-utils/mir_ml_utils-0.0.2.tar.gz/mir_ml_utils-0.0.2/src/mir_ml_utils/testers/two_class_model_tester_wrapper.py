import numpy as np
from typing import List, Union
from pathlib import Path
import os
from PIL import Image
from loguru import logger
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
import cv2

import src.data_handlers.img_utils as img_utils
from src.models.easyfsl_proto_net_classifier import EasyFSLProtoNetClassifier


class TwoClassPyTorchModelTester(object):

    def __init__(self, options: dict):
        self.options: dict = options

    def evaluate(self, model: nn.Module, dataloader: DataLoader):

        if self.options['create_simple_segmentation']:
            logger.info(f"Building simple segmentations. Output path={self.options['simple_segmentation_out']}")
            TwoClassPyTorchModelTester.build_simple_segmentation(model=model,
                                                                 options=self.options)

        if self.options['evaluate_few_shot_learner']:
            return TwoClassPyTorchModelTester.evaluate_few_show_model(model=model,
                                                                      dataloader=dataloader,
                                                                      device=self.options['device'],
                                                                      class0_name=self.options['class0_name'],
                                                                      class1_name=self.options['class1_name'],
                                                                      options=self.options)

        if isinstance(dataloader, DataLoader):
            return TwoClassPyTorchModelTester.evaluate_on_dataloader(model,
                                                                     dataloader,
                                                                     device=self.options['device'],
                                                                     class0_name=self.options['class0_name'],
                                                                     class1_name=self.options['class1_name'])
        elif isinstance(dataloader, Dataset):
            return TwoClassPyTorchModelTester.evaluate_on_dataset(model,
                                                                  dataloader,
                                                                  device=self.options['device'],
                                                                  class0_name=self.options['class0_name'],
                                                                  class1_name=self.options['class1_name'])
        else:
            raise ValueError("Invalid dataloader type. Dataloader has to be in "
                             "[torch.utils.data.DataLoader, torch.utils.data.Dataset]")

    @staticmethod
    def build_simple_segmentation(model: nn.Module, options: dict):

        # get the images
        test_class_0_images = img_utils.get_img_files(img_dir=options['test_class_0_images_path'],
                                                      img_formats=['jpg', 'png', 'jpeg'])

        test_class_1_images = img_utils.get_img_files(img_dir=options['test_class_1_images_path'],
                                                      img_formats=['jpg', 'png', 'jpeg'])

        images = test_class_1_images + test_class_0_images

        data_out_dir = options['simple_segmentation_out']

        counter = 0
        for image_path in images:
            file, ext = os.path.splitext(str(image_path))
            image_name = "crop_" + file.split('/')[-1] + "_" + str(counter)
            image_name += ext
            filename = data_out_dir / image_name
            output_image = TwoClassPyTorchModelTester.predict_on_crops(input_image=image_path,
                                                                       img_transform=options['img_transform'],
                                                                       model=model,
                                                                       img_shape=options['img_shape'],
                                                                       class1_name=options['class1_name'],
                                                                       class0_name=options['class0_name'],
                                                                       device=options['device'],
                                                                       class1_threshold=options['class1_threshold'])

            cv2.imwrite(str(filename), output_image)
            counter += 1

    @staticmethod
    def predict_image(model: nn.Module, image: torch.Tensor,
                      img_size: List[int] = [3, 256, 256],
                      use_cuda: bool = False):

        if torch.cuda.is_available() and use_cuda:
            test_image_tensor = image.view(1, img_size[0], img_size[1], img_size[2]).cuda()
        else:
            test_image_tensor = image.view(1, img_size[0], img_size[1], img_size[2])

        with torch.no_grad():
            model.eval()
            # Model outputs log probabilities
            model_out = model(test_image_tensor)
            probabilities = torch.nn.functional.softmax(model_out, dim=1)
            model_out = probabilities.detach().numpy()
            pred = np.argmax(model_out)
            return pred, probabilities.detach().numpy().flatten()

    @staticmethod
    def predict_on_crops(input_image: Path,
                         model: nn.Module,
                         img_transform: transforms.Compose,
                         device: str,
                         class0_name: str = "Class 0",
                         class1_name: str = "Class 1",
                         class1_threshold: float = 0.9,
                         img_shape: tuple = (256, 256)):

        height = img_shape[1]
        width = img_shape[0]

        im = cv2.imread(str(input_image))
        imgheight, imgwidth, channels = im.shape

        output_image = np.zeros_like(im)

        for i in range(0, imgheight, height):
            for j in range(0, imgwidth, width):

                a = im[i:i + height, j:j + width]

                predicted_class, probabilities = TwoClassPyTorchModelTester.predict_image(model,
                                                                                          img_transform(
                                                                                              Image.fromarray(a)),
                                                                                          use_cuda=device == 'cuda:0')

                if class1_threshold is not None:

                    ## Put predicted class on the image
                    if predicted_class == 1 and probabilities[1] >= class1_threshold:
                        image_text = class1_name
                        image_text += " p={:0.2f}".format(probabilities[1])
                        color = (0, 0, 255)
                    else:

                        image_text = class0_name
                        image_text += " p={:0.2f}".format(probabilities[0])
                        color = (0, 255, 0)
                else:

                    if predicted_class == 1:
                        image_text = class1_name
                        image_text += " p={:0.2f}".format(probabilities[1])
                        color = (0, 0, 255)
                    else:

                        image_text = class0_name
                        image_text += " p={:0.2f}".format(probabilities[0])
                        color = (0, 255, 0)

                cv2.putText(a, image_text, (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                            color, 1, cv2.LINE_AA)

                b = np.zeros_like(a, dtype=np.uint8)
                b[:] = color
                add_img = cv2.addWeighted(a, 0.9, b, 0.1, 0)
                output_image[i:i + height, j:j + width, :] = add_img

        return output_image

    @staticmethod
    def evaluate_on_dataset(model: nn.Module, dataloader: Dataset, device: str,
                            class0_name: str = "Class 0",
                            class1_name: str = "Class 1"):

        """Evaluate the performance of the given model
        on the supplied dataset. It is assumed that the datapoints
        are coming one-by-one

        Parameters
        ----------
        class0_name
        class1_name
        model: The model to evaluate
        dataloader: The object that holds the test data
        device: The device the model is loaded
        Returns
        -------

        """
        total_predictions = 0
        correct_predictions = 0
        incorrect_class_1_images = 0
        correct_class_1_images = 0
        incorrect_class_0_images = 0
        correct_class_0_images = 0

        with torch.no_grad():
            for batch, (x, y) in enumerate(dataloader):
                print(f"Working on point instance {batch}")

                if isinstance(y, int):
                    ground_truth = y
                elif isinstance(y, torch.Tensor):
                    ground_truth = y.detach().numpy()
                else:
                    raise ValueError("Label type not in [int, torch.Tensor]")

                x = x.to(device)
                model_out = model(x.unsqueeze(0))
                model_out = torch.nn.functional.softmax(model_out, dim=1)

                # if we are on cuda we need to bring
                # the model output to the host
                if device == 'cuda:0':
                    model_out = model_out.cpu().detach().numpy()
                else:
                    model_out = model_out.detach().numpy()

                pred = np.argmax(model_out)

                if pred == 0 and ground_truth == 0:
                    correct_class_0_images += 1
                elif pred == 0 and ground_truth == 1:
                    incorrect_class_1_images += 1
                elif pred == 1 and ground_truth == 1:
                    correct_class_1_images += 1
                elif pred == 1 and ground_truth == 0:
                    incorrect_class_0_images += 1

                total_predictions += 1

        return TwoClassPyTorchModelTester._print_test_info(total_predictions=total_predictions,
                                                           correct_predictions=correct_predictions,
                                                           incorrect_class_1_images=incorrect_class_1_images,
                                                           correct_class_1_images=correct_class_1_images,
                                                           incorrect_class_0_images=incorrect_class_0_images,
                                                           correct_class_0_images=correct_class_0_images,
                                                           class1_name=class1_name, class0_name=class0_name)

    @staticmethod
    def evaluate_on_dataloader(model: nn.Module, dataloader: DataLoader, device: str,
                               class0_name: str = "Class 0", class1_name: str = "Class 1"):
        total_predictions = 0
        correct_predictions = 0
        incorrect_class_1_images = 0
        correct_class_1_images = 0
        incorrect_class_0_images = 0
        correct_class_0_images = 0

        with torch.no_grad():
            for batch, (x, y) in enumerate(dataloader):

                x = x.to(device)
                model_out = model(x)
                model_out = torch.nn.functional.softmax(model_out, dim=1)

                # if we are on cuda we need to bring
                # the model output to the host
                if device == 'cuda:0':
                    model_out = model_out.cpu().detach().numpy()
                else:
                    model_out = model_out.detach().numpy()

                ground_truth = y.detach().numpy()
                batch_predictions = [np.argmax(pred) for pred in model_out]

                for pred, ground in zip(batch_predictions, ground_truth):

                    if pred == 0 and ground == 0:
                        correct_class_0_images += 1
                    elif pred == 0 and ground == 1:
                        incorrect_class_1_images += 1
                    elif pred == 1 and ground == 1:
                        correct_class_1_images += 1
                    elif pred == 1 and ground == 0:
                        incorrect_class_0_images += 1

                total_predictions += len(batch_predictions)

                batch_correct_predictions = sum(y.detach().numpy() == np.array(batch_predictions))
                correct_predictions += batch_correct_predictions
                batch_accuracy = float(batch_correct_predictions) / float(len(batch_predictions))
                logger.info(f"Batch {batch} model accuracy {batch_accuracy}")

        return TwoClassPyTorchModelTester._print_test_info(total_predictions=total_predictions,
                                                           correct_predictions=correct_predictions,
                                                           incorrect_class_1_images=incorrect_class_1_images,
                                                           correct_class_1_images=correct_class_1_images,
                                                           incorrect_class_0_images=incorrect_class_0_images,
                                                           correct_class_0_images=correct_class_0_images,
                                                           class1_name=class1_name, class0_name=class0_name)

    @staticmethod
    def evaluate_few_show_model(model: nn.Module, dataloader: DataLoader, device: str,
                                options: dict,
                                class0_name: str = "Class 0",
                                class1_name: str = "Class 1",
                                ):

        def evaluate_on_one_task(prototypes: torch.Tensor,
                                 model: Union[nn.Module | EasyFSLProtoNetClassifier],
                                 support_images: torch.Tensor,
                                 support_labels: torch.Tensor,
                                 query_images: torch.Tensor,
                                 query_labels: torch.Tensor) -> [int, int]:
            """
            Returns the number of correct predictions of query labels, and the total number of predictions.
            """

            if prototypes is None:
                model.process_support_set(support_images, support_labels)
            else:
                model.set_prototypes(prototypes=prototypes)

                #add the support images to the query images
                query_images_all = []
                query_labels_all = []
                for item, label in zip(query_images, query_labels):
                    query_images_all.append(item)
                    query_labels_all.append(label)

                for item, label in zip(support_images, support_labels):
                    query_images_all.append(item)
                    query_labels_all.append(label)

                query_images = torch.stack(query_images_all)
                query_labels = torch.stack(query_labels_all)

            model_outputs = model(query_images).detach().data
            max_preds_out = torch.max(model_outputs, 1)[1]
            max_preds = (max_preds_out == query_labels).sum().item()
            return max_preds, len(query_labels), max_preds_out, model.prototypes

        def do_test_model(prototypes, model, dataloader):

            logger.info(f"Test set size={len(dataloader)}")
            total_predictions = 0
            correct_predictions = 0
            incorrect_class_1_images = 0
            correct_class_1_images = 0
            incorrect_class_0_images = 0
            correct_class_0_images = 0

            model.eval()

            best_accuracy_on_test = 0
            best_prototypes = None

            with torch.no_grad():
                #for episode_index, (support_images, support_labels, query_images, query_labels, class_ids) in \
                #        tqdm(enumerate(dataloader), total=len(dataloader), desc="Testing"):

                #for episode_index, (support_images, support_labels, query_images, query_labels, class_ids) in enumerate(dataloader):

                for episode_index, (x, y) in enumerate(dataloader):

                    logger.info(f"Test batch ={episode_index}")
                    logger.info(f"Number of support images: {support_images.size()}")
                    logger.info(f"Number of query images: {query_images.size()}")
                    x = x.to(device)
                    support_labels = support_labels.to(device)
                    query_images = query_images.to(device)
                    query_labels = query_labels.to(device)
                    correct, total, model_outputs, prototypes = evaluate_on_one_task(prototypes=prototypes,
                                                                                     model=model,
                                                                                     support_images=support_images,
                                                                                     support_labels=support_labels,
                                                                                     query_images=query_images,
                                                                                     query_labels=query_labels)

                    logger.info(f"Total number of predictions ={total}")

                    error_class_0 = 0
                    error_class_1 = 0

                    for i, label in enumerate(query_labels):
                        ground_truth = label
                        predicted = model_outputs[i].item()

                        if ground_truth == 0 and predicted == 1:
                            error_class_0 += 1
                            incorrect_class_0_images += 1
                        elif ground_truth == 1 and predicted == 0:
                            error_class_1 += 1
                            incorrect_class_1_images += 1
                        elif ground_truth == 0 and predicted == 0:
                            correct_class_0_images += 1
                        elif ground_truth == 1 and predicted == 1:
                            correct_class_1_images += 1

                    task_accuracy = float(correct) / float(total)

                    if task_accuracy > best_accuracy_on_test:
                        best_accuracy_on_test = task_accuracy
                        best_prototypes = prototypes

                    #logger.info(f"\n")
                    #logger.info(f"On test task {episode_index}  {class0_name}  incorrect points = {error_class_0}")
                    #logger.info(f"On test task {episode_index}  {class1_name}  incorrect points = {error_class_1}")

                    total_predictions += total
                    correct_predictions += correct

                test_accuracy = (100 * correct_predictions / total_predictions)
                logger.info(f"Model tested on {len(dataloader)} tasks. "
                            f"Accuracy: {test_accuracy:.2f}%")

            out = TwoClassPyTorchModelTester._print_test_info(total_predictions=total_predictions,
                                                              correct_predictions=correct_predictions,
                                                              incorrect_class_1_images=error_class_1,
                                                              correct_class_1_images=correct_class_1_images,
                                                              incorrect_class_0_images=error_class_0,
                                                              correct_class_0_images=correct_class_0_images,
                                                              class0_name=class0_name,
                                                              class1_name=class1_name)

            return out, best_prototypes

        prototypes: torch.Tensor = None
        if options['few_shot_inference_with'] == 'with_prototypes':

            logger.info(f"Loading prototypes from {options['few_shot_prototypes_file_path']}")
            prototypes = torch.load(options['few_shot_prototypes_file_path'],
                                    map_location=torch.device(device))

            logger.info(f"Testing with prototypes")
            model.set_prototypes(prototypes=prototypes)
            return TwoClassPyTorchModelTester.evaluate_on_dataloader(dataloader=dataloader, model=model,
                                                                     class0_name=class0_name, class1_name=class1_name,
                                                                     device=device)
            #out, best_prototypes = do_test_model(prototypes=prototypes, model=model, dataloader=dataloader)
            #out, best_prototypes = do_test_model(prototypes=None, model=model, dataloader=dataloader)

        elif options['few_shot_inference_with'] == 'usual_testing':
            logger.info(f"Using usual testing")
            logger.info(f"Loading prototypes from {options['few_shot_prototypes_file_path']}")
            prototypes = torch.load(options['few_shot_prototypes_file_path'],
                                    map_location=torch.device(device))

            model.set_prototypes(prototypes=prototypes)
            out = TwoClassPyTorchModelTester.evaluate_on_dataloader(model=model,
                                                                    dataloader=dataloader,
                                                                    device=device,
                                                                    class0_name=class0_name,
                                                                    class1_name=class1_name)
            best_prototypes = prototypes

        else:
            logger.info(f"Testing without prototypes")
            out, best_prototypes = do_test_model(prototypes=None, model=model, dataloader=dataloader)

        return out, best_prototypes

    @staticmethod
    def _print_test_info(total_predictions: int,
                         correct_predictions: int,
                         incorrect_class_1_images: int,
                         correct_class_1_images: int,
                         incorrect_class_0_images: int,
                         correct_class_0_images: int,
                         class0_name: str,
                         class1_name: str):

        accuracy = float(correct_predictions) / float(total_predictions)
        logger.info(f"Model accuracy {accuracy}")
        logger.info(f"Model TP (i.e {class1_name} img and model predicted it)={correct_class_1_images}")
        logger.info(f"Model TN (i.e {class0_name} img  and model predicted it)={correct_class_0_images}")
        logger.info(f"Model FP (i.e this is not {class1_name} img but model predicted it)={incorrect_class_0_images}")
        logger.info(
            f"Model FN (i.e this is  {class1_name} img  but model did not predicted it. It predicted {class0_name})={incorrect_class_1_images}")

        tp = correct_class_1_images
        tn = correct_class_0_images
        fp = incorrect_class_0_images
        fn = incorrect_class_1_images

        recall = float(tp) / (float(tp) + float(fn))
        precision = float(tp) / (float(tp) + float(fp))
        fscore = (2 * recall * precision) / (precision + recall)

        logger.info(f"Model recall={recall}")
        logger.info(f"Model precision={precision}")
        logger.info(f"Model fscore={fscore}")
        return {"accuracy": accuracy, "recall": recall,
                "precision": precision, "Fscore": fscore,
                "details": {"tp": tp, "tn": tn, "fp": fp, "fn": fn}}
