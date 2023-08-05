
import scdiffeq_analyses as sdq_an
import numpy as np

NoneType = type(None)



# -- 
from scdiffeq.core.lightning_models.base import SinkhornDivergence
from tqdm.notebook import tqdm
import torch


# -- 
class TemporalDistances:
    """Calculate the distance between steps and the observed time points."""

    def __init__(
        self,
        adata,
        time_key: str = "Time point",
        use_key: str = "X_pca",
        device: str = "cuda:0",
    ):

        self.adata = adata
        self.df = self.adata.obs.copy()
        self.time_key = time_key
        self.use_key = use_key

        X_ref = self.df.groupby(self.time_key).apply(self._fetch).to_dict()
        self.X_ref = {}
        for key, val in X_ref.items():
            self.X_ref[key] = val.to(device)

        self.Loss = sdq.core.SinkhornDivergence()

    def _fetch(self, df):
        return torch.Tensor(self.adata[df.index].obsm[self.use_key])

    @property
    def n_steps(self):
        return len(self.X_hat)

    def loss(self, X, X_hat):
        return self.Loss(X, X_hat).item()

    def __call__(self, X_hat: torch.Tensor):
        
        """
        Examples:
        ---------
        temp_dist = TemporalDistances(clonal_adata)
        d = temp_dist(X_hat=X_hat)
        """

        self.X_hat = X_hat

        self.Distances = {}
        for key, X in tqdm(self.X_ref.items()):
            self.Distances[key] = [
                self.loss(X, X_hat[i]) for i in tqdm(range(self.n_steps))
            ]

        return self.Distances


