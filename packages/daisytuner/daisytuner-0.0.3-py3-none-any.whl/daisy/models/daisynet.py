from __future__ import annotations

import torch
import numpy as np
import pytorch_lightning as pl

from pathlib import Path
from typing import Tuple

from torchmetrics import PearsonCorrCoef

from daisy import MapNest
from daisy.models.encoding import Encoding
from daisy.models.backbone import Backbone
from daisy.models.norm_coeffs import *


class DaisyNet(pl.LightningModule):
    def __init__(
        self,
        node_features: int,
        edge_features: int,
        arch_features: int,
        counters: int,
        num_targets: int,
        hostname: str = None,
        arch: str = None,
        hidden_channels: int = 256,
        num_layers: int = 8,
    ):
        super().__init__()

        self._hostname = hostname
        self._arch = arch
        self._dims = hidden_channels

        heads = 4
        assert hidden_channels % heads == 0
        self.backbone = Backbone(
            node_features=node_features,
            edge_features=edge_features,
            hidden_channels=int(hidden_channels / heads),
            heads=heads,
            num_layers=num_layers,
        )
        self.counter_encoder = torch.nn.Sequential(
            torch.nn.Linear(in_features=counters, out_features=hidden_channels),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(in_features=hidden_channels, out_features=hidden_channels),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(in_features=hidden_channels, out_features=hidden_channels),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(in_features=hidden_channels, out_features=hidden_channels),
        )
        self.arch_encoder = torch.nn.Sequential(
            torch.nn.Linear(in_features=arch_features, out_features=hidden_channels),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(in_features=hidden_channels, out_features=hidden_channels),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(in_features=hidden_channels, out_features=hidden_channels),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(in_features=hidden_channels, out_features=hidden_channels),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(in_features=hidden_channels, out_features=hidden_channels),
        )
        self.neck = torch.nn.Sequential(
            torch.nn.Linear(
                in_features=3 * hidden_channels, out_features=hidden_channels
            ),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(in_features=hidden_channels, out_features=hidden_channels),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(in_features=hidden_channels, out_features=hidden_channels),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(in_features=hidden_channels, out_features=hidden_channels),
            torch.nn.LeakyReLU(),
        )
        self.neck.append(
            torch.nn.Linear(in_features=hidden_channels, out_features=hidden_channels)
        )

        self.head = torch.nn.Linear(
            in_features=hidden_channels, out_features=num_targets
        )

        self.loss = torch.nn.L1Loss()
        self.pearson = PearsonCorrCoef(num_outputs=num_targets)

        eps = 1e-6
        self._archs_mean = torch.tensor(ARCHS_MEAN, dtype=torch.float32)
        self._archs_std = torch.tensor(ARCHS_STD, dtype=torch.float32) + eps
        self._counters_mean = torch.tensor(COUNTERS_MEAN, dtype=torch.float32)
        self._counters_std = torch.tensor(COUNTERS_STD, dtype=torch.float32) + eps
        self._target_mean = torch.tensor(TARGETS_MEAN, dtype=torch.float32)
        self._target_std = torch.tensor(TARGETS_STD, dtype=torch.float32) + eps
        # self._targets_min = torch.tensor(TARGETS_MIN, dtype=torch.float32)
        # self._targets_max = torch.tensor(TARGETS_MAX, dtype=torch.float32)

    @torch.inference_mode()
    def predict(self, map_nest: MapNest) -> Tuple[np.ndarray]:
        encoding = Encoding(map_nest=map_nest, hostname=self._hostname, arch=self._arch)
        encoding.encode()

        data = encoding.torch()
        data.to(self.device)

        preds, embedding, node_embeddings = self(data)
        preds = preds.cpu().numpy().squeeze()
        embedding = embedding.cpu().numpy().squeeze()
        node_embeddings = node_embeddings.cpu().numpy().squeeze()
        return preds, embedding, node_embeddings

    @torch.inference_mode()
    def embedding(self, map_nest: MapNest) -> np.ndarray:
        encoding = Encoding(map_nest=map_nest, hostname=self._hostname, arch=self._arch)
        encoding.encode()

        data = encoding.torch().to(self.device)
        (
            _,
            embedding,
            node_embeddings,
            static_embedding,
            dynamic_embedding,
            arch_embedding,
        ) = self(data)

        embedding = embedding.cpu().numpy().squeeze()
        node_embeddings = node_embeddings.cpu().numpy().squeeze()
        static_embedding = static_embedding.cpu().numpy().squeeze()
        dynamic_embedding = dynamic_embedding.cpu().numpy().squeeze()
        arch_embedding = arch_embedding.cpu().numpy().squeeze()

        return (
            embedding,
            node_embeddings,
            static_embedding,
            dynamic_embedding,
            arch_embedding,
        )

    def forward(self, data):
        # Derive static representation
        static_embedding, node_embeddings = self.backbone(
            data.x, data.edge_index, data.edge_attr, data.batch
        )

        # Add global runtime information
        if hasattr(data, "arch") and hasattr(data, "counters"):
            archs = (data.arch - self._archs_mean) / self._archs_std
            counters = (data.counters - self._counters_mean) / self._counters_std

            arch_embedding = self.arch_encoder(archs)
            dynamic_embedding = self.counter_encoder(counters)
        else:
            # Static-only embedding
            arch_embedding = torch.zeros_like(static_embedding).to(
                static_embedding.device
            )
            dynamic_embedding = torch.zeros_like(static_embedding).to(
                static_embedding.device
            )

        # Derive runtime-augmented representation
        embedding = torch.hstack([static_embedding, arch_embedding, dynamic_embedding])
        embedding = self.neck(embedding)

        # Predict runtime metrics
        preds = self.head(embedding)

        return (
            preds,
            embedding,
            node_embeddings,
            static_embedding,
            dynamic_embedding,
            arch_embedding,
        )

    def training_step(self, data, batch_idx):
        batch_size = data.ptr.size(dim=0) - 1
        targets = (data.y - self._target_mean) / self._target_std

        preds, _, _, _ = self(data)
        l = self.loss(preds, targets)

        self.log(
            "train_loss",
            l,
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )
        pearson = self.pearson(preds, targets)
        self.log(
            "train_pearson",
            pearson.mean(),
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )
        self.log(
            "train_pearson_l2_bandwidth",
            pearson[12],
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )
        self.log(
            "train_pearson_l3_bandwidth",
            pearson[10],
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )
        self.log(
            "train_pearson_mem_bandwidth",
            pearson[8],
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )

        return l

    def validation_step(self, data, batch_idx):
        batch_size = data.ptr.size(dim=0) - 1
        targets = (data.y - self._target_mean) / self._target_std

        preds, _, _, _ = self(data)
        l = self.loss(preds, targets)

        self.log(
            "val_loss",
            l,
            prog_bar=True,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )

        pearson = self.pearson(preds, targets)
        self.log(
            "val_pearson",
            pearson.mean(),
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )
        self.log(
            "val_pearson_l2_bandwidth",
            pearson[12],
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )
        self.log(
            "val_pearson_l3_bandwidth",
            pearson[10],
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )
        self.log(
            "val_pearson_mem_bandwidth",
            pearson[8],
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )

    def test_step(self, data, batch_idx):
        batch_size = data.ptr.size(dim=0) - 1
        targets = (data.y - self._target_mean) / self._target_std

        preds, _, _, _ = self(data)
        l = self.loss(preds, targets)

        self.log(
            "test_loss",
            l,
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )

        pearson = self.pearson(preds, targets)
        self.log(
            "test_pearson",
            pearson.mean(),
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )
        self.log(
            "test_pearson_l2_bandwidth",
            pearson[12],
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )
        self.log(
            "test_pearson_l3_bandwidth",
            pearson[10],
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )
        self.log(
            "test_pearson_mem_bandwidth",
            pearson[8],
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(params=self.parameters(), lr=1e-3)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=45, gamma=0.1)
        return {
            "optimizer": optimizer,
            "lr_scheduler": scheduler,
            "monitor": "val_loss",
        }

    @classmethod
    def create(
        cls, model_path: Path = None, hostname: str = None, arch: str = None
    ) -> DaisyNet:
        if model_path is None:
            model_path = Path(__file__).parent.parent / "daisynet_v3.ckpt"

        checkpoint = torch.load(model_path, map_location=torch.device("cpu"))
        model = DaisyNet(
            hostname=hostname,
            arch=arch,
            node_features=555,
            edge_features=2,
            arch_features=11,
            counters=80,
            num_targets=17,
        )
        model.load_state_dict(checkpoint["state_dict"])
        model.to("cpu")
        model.eval()

        return model
