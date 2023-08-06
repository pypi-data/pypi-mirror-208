import torch

from torch_geometric.nn import DeepGCNLayer, TransformerConv, GlobalAttention


class Backbone(torch.nn.Module):
    def __init__(
        self,
        node_features: int,
        edge_features: int,
        hidden_channels: int,
        num_layers: int,
        heads: int,
    ) -> None:
        super().__init__()

        self.node_encoder = torch.nn.Linear(
            in_features=node_features, out_features=heads * hidden_channels, bias=True
        )
        self.edge_encoder = torch.nn.Linear(
            in_features=edge_features, out_features=heads * hidden_channels, bias=True
        )

        self.layers = torch.nn.Sequential()
        for i in range(1, num_layers + 1):
            conv = TransformerConv(
                in_channels=heads * hidden_channels,
                out_channels=hidden_channels,
                heads=heads,
                concat=True,
                dropout=0.0,
                edge_dim=heads * hidden_channels,
            )
            # norm = BatchNorm(heads * hidden_channels)
            act = torch.nn.LeakyReLU(inplace=True)

            layer = DeepGCNLayer(
                conv, act=act, block="res+", dropout=0.0, ckpt_grad=i % 3
            )
            self.layers.append(layer)

        self.pooling_layer = GlobalAttention(
            gate_nn=torch.nn.Sequential(
                torch.nn.Linear(
                    in_features=heads * hidden_channels,
                    out_features=heads * hidden_channels,
                ),
                # torch.nn.BatchNorm1d(heads * hidden_channels),
                torch.nn.LeakyReLU(),
                torch.nn.Linear(
                    in_features=heads * hidden_channels,
                    out_features=heads * hidden_channels,
                ),
                # torch.nn.BatchNorm1d(heads * hidden_channels),
                torch.nn.LeakyReLU(),
                torch.nn.Linear(
                    in_features=heads * hidden_channels,
                    out_features=heads * hidden_channels,
                ),
                # torch.nn.BatchNorm1d(heads * hidden_channels),
                torch.nn.LeakyReLU(),
                torch.nn.Linear(in_features=heads * hidden_channels, out_features=1),
            )
        )

    def forward(self, x, edge_index, edge_attr, batch):
        x = self.node_encoder(x)
        edge_attr = self.edge_encoder(edge_attr)

        x = self.layers[0].conv(x, edge_index, edge_attr)
        for layer in self.layers[1:]:
            x = layer(x, edge_index, edge_attr)

        y = self.pooling_layer(x, batch)
        return y, x
