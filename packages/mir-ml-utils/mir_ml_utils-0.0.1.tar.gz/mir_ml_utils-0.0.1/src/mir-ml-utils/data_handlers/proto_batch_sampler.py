
import numpy as np
import torch


class PrototypicalBatchSampler(object):
    """PrototypicalBatchSampler: yield a batch of indexes at each iteration.
    Indexes are calculated by keeping in account 'classes_per_it' and 'num_samples',
    In fact at every iteration the batch indexes will refer to  'num_support' + 'num_query' samples
    for 'classes_per_it' random classes.  __len__ returns the number of episodes per epoch (same as 'self.iterations').

    """

    def __init__(self, labels, classes_per_it, num_samples, iterations):
        """Initialize the PrototypicalBatchSampler object. We can use the num_samples to control
        the batch size and hence the memory requirements. Since num_samples = suport_pts + query_pts
        we should have at least 1 query point assuming the support points are predetermined

        Parameters
        ----------
        labels: an iterable containing all the labels for the current dataset
        samples indexes will be inferred from this iterable.
        classes_per_it: Number of random classes for each iteration
        num_samples: Number of samples for each iteration for each class (support + query)
        iterations: Number of iterations (episodes) per epoch
        """

        super(PrototypicalBatchSampler, self).__init__()
        self.labels = labels
        self.classes_per_it = classes_per_it
        self.sample_per_class = num_samples
        self.iterations = iterations

        self.classes, self.counts = np.unique(self.labels, return_counts=True)
        self.classes = torch.LongTensor(self.classes)

        # create a matrix, indexes, of dim: classes X max(elements per class)
        # fill it with nans
        # for every class c, fill the relative row with the indices samples belonging to c
        # in numel_per_class we store the number of samples for each class/row
        self.idxs = range(len(self.labels))
        self.indexes = np.empty((len(self.classes), max(self.counts)), dtype=int) * np.nan
        self.indexes = torch.Tensor(self.indexes)
        self.numel_per_class = torch.zeros_like(self.classes)
        for idx, label in enumerate(self.labels):
            label_idx = np.argwhere(self.classes == label).item()
            self.indexes[label_idx, np.where(np.isnan(self.indexes[label_idx]))[0][0]] = idx
            self.numel_per_class[label_idx] += 1

    def __iter__(self):
        """Yield a batch of indexes

        Returns
        -------

        """

        spc = self.sample_per_class
        cpi = self.classes_per_it
        batch_size = spc * cpi

        for it in range(self.iterations):
            #batch_size = spc * cpi
            batch = torch.LongTensor(batch_size)
            c_idxs = torch.randperm(len(self.classes))[:cpi]

            for i, c in enumerate(self.classes[c_idxs]):

                s = slice(i * spc, (i + 1) * spc)
                # FIXME when torch.argwhere will exists
                label_idx = torch.arange(len(self.classes)).long()[self.classes == c].item()
                sample_idxs = torch.randperm(self.numel_per_class[label_idx])[:spc]
                batch[s] = self.indexes[label_idx][sample_idxs]
            batch = batch[torch.randperm(len(batch))]
            yield batch

    def __len__(self) -> int:
        """Returns the number of iterations (episodes) per epoch

        Returns
        -------

        """
        return self.iterations
