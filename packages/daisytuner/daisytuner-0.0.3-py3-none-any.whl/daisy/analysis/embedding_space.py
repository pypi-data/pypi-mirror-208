from __future__ import annotations

import dace
import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

from typing import List, Tuple, Dict, Union, Sequence

from tqdm import tqdm
from pathlib import Path
from typing import Union

from sklearn.neighbors import NearestNeighbors
from sklearn.manifold import TSNE

from daisy.map_nest import MapNest


class EmbeddingSpace:

    __create_key = object()

    def __init__(self, create_key: object, model) -> None:
        assert (
            create_key == EmbeddingSpace.__create_key
        ), "EmbeddingSpace objects must be created using EmbeddingSpace.create"

        self._model = model

        self._space = {}
        self._reverse_lookup = {}
        self._map_nests = {}
        self._metadata = pd.DataFrame()
        self._map_desc = pd.DataFrame(
            {
                "map_levels": pd.Series(dtype="int"),
                "outermost_dims": pd.Series(dtype="int"),
                "tuning_available": pd.Series(dtype="bool"),
            }
        )

        self._reset()

    def _reset(self) -> None:
        self._2d_projection = None
        self._nns = None

    def __len__(self) -> int:
        return len(self._space)

    def instances(self) -> List[str]:
        return list(self._space.keys())

    def embedding(self, uuid: str) -> np.ndarray:
        return self._space[uuid]

    def metadata(self, uuid: str) -> pd.DataFrame:
        return self._metadata.loc[uuid]

    def tuning_available(self) -> pd.DataFrame:
        return self._map_desc[self._map_desc["tuning_available"] != 0]

    def homogeneity(self, metric: str, k: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        homos = []
        for uuid, embedding in tqdm(self._space.items()):
            dists, nns = self._nns.kneighbors(
                X=embedding[None, :], n_neighbors=k, return_distance=True
            )
            nns = nns[0]

            vals = [self._metadata.loc[uuid, metric]]
            for i, nn in enumerate(nns):
                n_uuid = self._uuids[nn]
                vals.append(self._metadata.loc[n_uuid, metric])

            if len(vals) == 1:
                continue

            vals = np.array(vals)
            if vals.mean() == 0:
                continue

            homos.append(vals.std() / vals.mean())

        return np.array(homos)

    def nearest_neighbors(
        self, query: MapNest, k: int = 5
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        embedding, *_ = self._model.embedding(map_nest=query)
        dists, nns = self._nns.kneighbors(
            X=embedding[None, :], n_neighbors=k, return_distance=True
        )
        dists = dists[0]
        nns = nns[0]

        neighbors = pd.DataFrame(
            columns=["distance"] + self._metadata.columns.to_list()
        )
        for i, nn in enumerate(nns):
            uuid = self._uuids[nn]
            dist = dists[i]

            cols = [dist] + self._metadata.loc[uuid].values.tolist()
            neighbors.loc[uuid] = cols

        neighbors = neighbors.sort_values(by="distance")

        return neighbors

    def show(
        self, color_by: str = "memory_bandwidth", render_only: bool = False
    ) -> None:
        fig = go.Figure()
        data = self._map_desc
        discretized = pd.DataFrame()
        for col in [color_by]:
            temp = pd.qcut(self._metadata[col], q=7, duplicates="drop")
            num_categories = len(temp.unique())
            if num_categories < 2:
                discretized.loc[:, col] = 0
                continue

            bin_labels = [i for i in range(1, num_categories + 1)]
            discretized[col] = pd.qcut(
                self._metadata[col], q=7, duplicates="drop", labels=bin_labels
            )

        data = data.merge(
            right=discretized, how="inner", left_index=True, right_index=True
        )
        data = data.merge(
            right=self._2d_projection, how="inner", left_index=True, right_index=True
        )

        if color_by == "tuning_available":
            non_clustered = data[data.loc[:, "tuning_available"] == 0]
            fig.add_trace(
                go.Scatter(
                    x=non_clustered.loc[:, "x"].values,
                    y=non_clustered.loc[:, "y"].values,
                    mode="markers",
                    marker=go.scatter.Marker(opacity=0.7, color="LightGray"),
                    hovertext=non_clustered.index.to_list(),
                ),
            )

            clustered = data[data["tuning_available"] != 0]
            fig.add_trace(
                go.Scatter(
                    x=clustered.loc[:, "x"].values,
                    y=clustered.loc[:, "y"].values,
                    mode="markers",
                    marker=go.scatter.Marker(
                        color=clustered.loc[:, "tuning_available"].values,
                        opacity=0.9,
                        colorscale=px.colors.qualitative.Plotly,
                    ),
                    hovertext=clustered.index.to_list(),
                ),
            )
        else:
            if color_by in self._map_desc.columns:
                colorscale = px.colors.qualitative.Plotly
            else:
                colorscale = px.colors.sequential.Magma

            fig.add_trace(
                go.Scatter(
                    x=data.loc[:, "x"].values,
                    y=data.loc[:, "y"].values,
                    mode="markers",
                    marker=go.scatter.Marker(
                        color=data.loc[:, color_by].values,
                        opacity=0.9,
                        colorscale=colorscale,
                        colorbar=dict(thickness=10, orientation="h"),
                    ),
                    hovertext=data.index.to_list(),
                ),
            )

        fig.update_layout(
            showlegend=False,
            autosize=False,
            # width=300,
            # height=300,
            paper_bgcolor="rgba(255,255,255,1)",
            plot_bgcolor="rgba(255,255,255,1)",
            margin=dict(l=0, r=0, b=0, t=0),
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        if not render_only:
            fig.show()
            fig.write_image("temp.pdf")

        return fig

    def _add(
        self,
        uuid: str,
        map_nest: MapNest,
        embedding: np.ndarray,
        metadata: pd.DataFrame,
        map_desc: pd.DataFrame,
    ) -> None:
        assert uuid not in self._space
        self._space[uuid] = embedding
        self._map_nests[uuid] = map_nest

        if self._metadata.empty:
            self._metadata = pd.DataFrame(columns=metadata.columns)
        self._metadata.loc[uuid] = metadata.iloc[0]

        self._map_desc.loc[uuid] = [
            int(map_desc.iloc[0]["map_levels"]),
            int(map_desc.iloc[0]["outermost_dims"]),
            bool(map_desc.iloc[0]["tuning_available"]),
        ]

        reverse_key = embedding.tobytes()
        if reverse_key not in self._space:
            self._reverse_lookup[reverse_key] = []
        self._reverse_lookup[reverse_key].append(uuid)

        self._reset()

    def _fit(self) -> None:
        with tqdm(total=3) as pbar:
            pbar.set_description("Generating embedding matrix")

            self._uuids = list(self._space.keys())
            self._embeddings_matrix = []
            for uuid in self._uuids:
                self._embeddings_matrix.append(self._space[uuid])
            self._embeddings_matrix = np.vstack(self._embeddings_matrix)

            pbar.update(1)
            pbar.set_description("Nearest Neighbors Estimation")

            self._nns = NearestNeighbors()
            self._nns.fit(self._embeddings_matrix)

            pbar.update(1)
            pbar.set_description("tSNE 2D Projection")

            self._2d_projection = pd.DataFrame(columns=["x", "y"])
            tsne = TSNE(
                n_components=2,
                perplexity=10,
                n_iter=1000,
                init="pca",
                learning_rate="auto",
            )
            projections = tsne.fit_transform(self._embeddings_matrix)
            for i in range(len(self._uuids)):
                self._2d_projection.loc[self._uuids[i]] = [
                    projections[i, 0],
                    projections[i, 1],
                ]

            pbar.update(1)

    @classmethod
    def from_dataset(
        cls,
        map_nests: Union[Sequence[MapNest], Dict[str, MapNest]],
        model,
        hostname: str = None,
        arch: str = None,
    ) -> EmbeddingSpace:
        # Assign default names
        map_nests_ = {}
        if not isinstance(map_nests, dict):
            for map_nest in map_nests:
                map_nests_[map_nest.hash] = map_nest
        else:
            map_nests_ = map_nests

        space = EmbeddingSpace(create_key=cls.__create_key, model=model)
        for name, map_nest in tqdm(map_nests_.items()):
            tuning_dir = Path(map_nest.cutout.build_folder) / "daisy" / "tuning"
            tuning_available = tuning_dir.is_dir()

            map_desc = pd.DataFrame(
                {
                    "map_levels": pd.Series(dtype="int"),
                    "outermost_dims": pd.Series(dtype="int"),
                    "tuning_available": pd.Series(dtype="bool"),
                }
            )
            map_desc.loc[name] = [
                map_nest.levels,
                len(map_nest.outermost_map.map.params),
                tuning_available,
            ]

            try:
                embedding, *_ = model.embedding(map_nest=map_nest)
                assert not np.isnan(embedding).any()
            except:
                continue

            # Performance Metrics
            from daisy.analysis.profiling import Profiling

            analysis = Profiling(map_nest=map_nest, hostname=hostname, arch=arch)
            try:
                analysis.analyze(cache_only=True)
                metadata = analysis.performance_metrics()
            except:
                continue

            # SOAP Analysis
            from daisy.analysis.soap_analysis import SOAPAnalysis

            try:
                analysis = SOAPAnalysis(map_nest=map_nest)
                report = analysis.analyze(
                    num_processors=36, cache_size=50 * 1024 * 1024, cache_only=True
                )
                Q = report["Q_eval"] * report["bytes_per_element"]
                metadata.loc[:, "data_locality"] = Q / (
                    metadata.loc[:, "memory_data_volume_0"] * 1.0e6
                )
            except:
                pass

            space._add(
                uuid=name,
                map_nest=map_nest,
                embedding=embedding,
                metadata=metadata,
                map_desc=map_desc,
            )

        space._fit()
        return space
