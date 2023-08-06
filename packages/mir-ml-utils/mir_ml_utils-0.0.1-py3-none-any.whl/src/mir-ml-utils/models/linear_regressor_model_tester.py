import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


class LinearRegressorPyTorchModelTester(object):

    def __init__(self):
        pass

    @staticmethod
    def evaluate(model: nn.Module, dataloader: DataLoader, device: str):

        if isinstance(dataloader, DataLoader):
            return LinearRegressorPyTorchModelTester.evaluate_on_dataloader(model, dataloader, device)
        elif isinstance(dataloader, Dataset):
            return LinearRegressorPyTorchModelTester.evaluate_on_dataset(model, dataloader, device)
        else:
            raise ValueError("Invalid dataloader type. Dataloader has to be in "
                             "[torch.utils.data.DataLoader, torch.utils.data.Dataset]")

    @staticmethod
    def evaluate_on_dataset(model: nn.Module, dataloader: Dataset, device: str):
        """Evaluate the performance of the given model
        on the supplied dataset. It is assumed that the datapoints
        are coming one-by-one

        Parameters
        ----------
        model: The model to evaluate
        dataloader: The object that holds the test data
        device: The device the model is loaded
        Returns
        -------

        """
        total_predictions = 0
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
                model_out = model_out.detach()  # .numpy()
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

        accuracy = float(correct_class_1_images + correct_class_0_images) / float(total_predictions)
        print(f"Model accuracy {accuracy}")
        print(f"Model TP (i.e class 1 img and model predicted it)={correct_class_1_images}")
        print(f"Model TN (i.e class 0 img  and model predicted it)={correct_class_0_images}")
        print(f"Model FP (i.e this is not class 1 img but model predicted it)={incorrect_class_0_images}")
        print(f"Model FN (i.e this is  class 1 img  but model did not predicted it)={incorrect_class_1_images}")

        tp = correct_class_1_images
        tn = correct_class_0_images
        fp = incorrect_class_0_images
        fn = incorrect_class_1_images

        recall = float(tp) / (float(tp) + float(fn)) if tp != 0 else 0.0
        precision = float(tp) / (float(tp) + float(fp)) if tp != 0 else 0.0
        fscore = (2 * recall * precision) / (precision + recall) if tp != 0 else 0.0

        print(f"Model recall={recall}")
        print(f"Model precision={precision}")
        print(f"Model fscore={fscore}")
        return {"accuracy": accuracy, "recall": recall,
                "precision": precision, "Fscore": fscore,
                "details": {"tp": tp, "tn": tn, "fp": fp, "fn": fn}}

    @staticmethod
    def evaluate_on_dataloader(model: nn.Module, dataloader: DataLoader, device: str,
                               norm: float):
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
                print(f"Batch {batch} model accuracy {batch_accuracy}")

        accuracy = float(correct_predictions) / float(total_predictions)
        print(f"Model accuracy {accuracy}")
        print(f"Model TP (i.e class 1 img and model predicted it)={correct_class_1_images}")
        print(f"Model TN (i.e class 0 img  and model predicted it)={correct_class_0_images}")
        print(f"Model FP (i.e this is not class 1 img but model predicted it)={incorrect_class_0_images}")
        print(f"Model FN (i.e this is  class 1 img  but model did not predicted it)={incorrect_class_1_images}")

        tp = correct_class_1_images
        tn = correct_class_0_images
        fp = incorrect_class_0_images
        fn = incorrect_class_1_images

        recall = float(tp) / (float(tp) + float(fn))
        precision = float(tp) / (float(tp) + float(fp))
        fscore = (2 * recall * precision) / (precision + recall)

        print(f"Model recall={recall}")
        print(f"Model precision={precision}")
        print(f"Model fscore={fscore}")
        return {"accuracy": accuracy, "recall": recall,
                "precision": precision, "Fscore": fscore,
                "details": {"tp": tp, "tn": tn, "fp": fp, "fn": fn}}