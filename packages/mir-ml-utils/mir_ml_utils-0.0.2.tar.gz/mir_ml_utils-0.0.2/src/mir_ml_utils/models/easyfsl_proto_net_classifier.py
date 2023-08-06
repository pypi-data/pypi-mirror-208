from pathlib import Path
import torch.nn as nn
import torch
from torch.utils.data import DataLoader, Dataset
from typing import Union, List, Tuple, Dict
from loguru import logger
from mir_ml_utils.easyfsl.methods.prototypical_networks import PrototypicalNetworks


def _init_class_dict(classes: List[int]) -> Dict:

    class_dict = {}
    for class_name in classes:
        class_dict[class_name] = 0
    return class_dict


class EasyFSLProtoNetClassifier(PrototypicalNetworks):
    """Wrapper to easyfsl PrototypicalNetwork

    """

    @staticmethod
    def evaluate_on_one_task(prototypes: torch.Tensor,
                             model: Union[nn.Module, "EasyFSLProtoNetClassifier"],
                             support_images: torch.Tensor,
                             support_labels: torch.Tensor,
                             query_images: torch.Tensor,
                             query_labels: torch.Tensor) -> Tuple:
        """ Returns the number of correct predictions of query labels, and the total number of predictions.
        """

        if prototypes is None:
            model.process_support_set(support_images, support_labels)
        else:
            model.set_prototypes(prototypes=prototypes)

            # add the support images to the query images
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

        model_outputs = model(query_images)
        model_outputs = model_outputs.detach().data
        max_preds_out = torch.max(model_outputs, 1)[1]
        max_preds = (max_preds_out == query_labels).sum().item()
        return max_preds, len(query_labels), max_preds_out, model.prototypes

    @staticmethod
    def do_test_prototypical_network(model: "EasyFSLProtoNetClassifier", dataloader: DataLoader,
                                     classes: List[int]):

        if isinstance(dataloader, Dataset):
            raise ValueError("Cannot test using a Dataset.")

        logger.info(f"Test set size={len(dataloader)}")
        total_predictions = 0
        correct_predictions = 0

        model.eval()

        best_accuracy_on_test = 0
        best_prototypes: torch.Tensor = None
        batch_monitors = {"error": {}, "correct":{}}
        with torch.no_grad():

            for episode_index, (support_images, support_labels,
                                query_images, query_labels, class_ids) in enumerate(dataloader):

                logger.info("=================================================")
                logger.info(f"Test batch index={episode_index}")
                logger.info(f"Number of support images: {support_images.size()}")
                logger.info(f"Number of query images: {query_images.size()}")

                support_images = support_images.to(model.device)
                support_labels = support_labels.to(model.device)
                query_images = query_images.to(model.device)
                query_labels = query_labels.to(model.device)

                correct, total, model_outputs, prototypes = EasyFSLProtoNetClassifier.evaluate_on_one_task(
                    prototypes=model.prototypes,
                    model=model,
                    support_images=support_images,
                    support_labels=support_labels,
                    query_images=query_images,
                    query_labels=query_labels)

                logger.info(f"Total number of predictions={total}")
                class_errors = _init_class_dict(classes)
                class_correct = _init_class_dict(classes)

                for i, label in enumerate(query_labels):
                    ground_truth = label
                    label_ground = ground_truth.detach().item()
                    predicted = model_outputs[i].item()

                    if ground_truth == predicted:
                        # this is a correct classification for this label
                        class_correct[label_ground] += 1
                    else:
                        # this is an incorrect classification for this label
                        class_errors[label_ground] += 1

                batch_monitors["error"][episode_index] = class_errors
                batch_monitors["correct"][episode_index] = class_correct
                # monitor the accuracy of the task
                task_accuracy = float(correct) / float(total)

                if task_accuracy > best_accuracy_on_test:
                    best_accuracy_on_test = task_accuracy
                    best_prototypes = prototypes

                total_predictions += total
                correct_predictions += correct
                logger.info(f"Batch accuracy={task_accuracy}")
                logger.info("=================================================")
            test_accuracy = (100 * correct_predictions / total_predictions)
            logger.info(f"Model tested on {len(dataloader)} tasks. "
                        f"Accuracy: {test_accuracy:.2f}%")

        return best_prototypes, test_accuracy, batch_monitors

    def __init__(self, backbone: nn.Module, model_name: str,
                 device: str, use_softmax: bool = True):
        super(EasyFSLProtoNetClassifier, self).__init__(backbone, use_softmax=use_softmax)
        self.name = model_name
        self.device = device

    def load_prototypes(self, prototypes_paths: Path, device: str) -> None:
        """Load the prototypes from the given paths

        Parameters
        ----------
        device
        prototypes_paths

        Returns
        -------

        """
        self.set_prototypes(prototypes=torch.load(prototypes_paths,
                                                  map_location=torch.device(device)))
        self.device = device

    def set_prototypes(self, prototypes: torch.Tensor) -> None:
        """Set the prototypes for the network. Is assumes that
        the data is already mapped in the proper device

        Parameters
        ----------
        prototypes: The prototypes for the network

        Returns
        -------

        """
        self.prototypes = prototypes

    def save_prototypes(self, filename: Path):
        """Save the prototypes of this model in the given
        filename. Raises ValueError if self.prototypes is not
        an instance to torch.Tensor

        Parameters
        ----------
        filename

        Returns
        -------

        """
        if isinstance(self.prototypes, torch.Tensor):
            torch.save(self.prototypes, str(filename))
            return

        raise ValueError("Model prototypes are not an instance of torch.Tensor")
