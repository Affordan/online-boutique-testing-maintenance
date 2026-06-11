import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

# =====================================================
# CONFIG
# =====================================================

WINDOW_SIZE = 12          # 24*5秒=2分钟

BATCH_SIZE = 64

EPOCHS = 20

LR = 1e-3

LATENT_DIM = 8

D_MODEL = 32

NHEAD = 4

NUM_LAYERS = 2

BETA = 3.0

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)

FEATURE_COLS = [
    "cpu_usage",
    "memory_usage_mb",
    "request_rate",
    "error_rate",
    "avg_latency_ms"
]

# =====================================================
# OUTPUT FOLDER
# =====================================================

os.makedirs("results", exist_ok=True)

os.makedirs("results/models", exist_ok=True)

os.makedirs("results/csv", exist_ok=True)

os.makedirs(
    "results/normal_figures",
    exist_ok=True
)

os.makedirs(
    "results/fault_figures",
    exist_ok=True
)

# =====================================================
# WINDOW
# =====================================================

def create_windows(data, window_size):

    windows = []

    for i in range(
        len(data) - window_size + 1
    ):
        windows.append(
            data[i:i + window_size]
        )

    return np.array(windows)

# =====================================================
# DA-VAE
# =====================================================

class DAVAE(nn.Module):

    def __init__(
        self,
        input_dim
    ):

        super().__init__()

        self.input_dim = input_dim

        self.embedding = nn.Linear(
            input_dim,
            D_MODEL
        )

        encoder_layer = \
            nn.TransformerEncoderLayer(
                d_model=D_MODEL,
                nhead=NHEAD,
                batch_first=True
            )

        self.transformer = \
            nn.TransformerEncoder(
                encoder_layer,
                num_layers=NUM_LAYERS
            )

        self.fc_mu = nn.Linear(
            D_MODEL,
            LATENT_DIM
        )

        self.fc_logvar = nn.Linear(
            D_MODEL,
            LATENT_DIM
        )

        self.decoder = nn.Sequential(

            nn.Linear(
                LATENT_DIM,
                64
            ),

            nn.ReLU(),

            nn.Linear(
                64,
                WINDOW_SIZE * input_dim
            )
        )

    def encode(self, x):

        h = self.embedding(x)

        h = self.transformer(h)

        h = h.mean(dim=1)

        mu = self.fc_mu(h)

        logvar = self.fc_logvar(h)

        return mu, logvar

    def reparameterize(
        self,
        mu,
        logvar
    ):

        std = torch.exp(
            0.5 * logvar
        )

        eps = torch.randn_like(std)

        return mu + eps * std

    def decode(self, z):

        out = self.decoder(z)

        out = out.view(
            -1,
            WINDOW_SIZE,
            self.input_dim
        )

        return out

    def forward(self, x):

        mu, logvar = self.encode(x)

        z = self.reparameterize(
            mu,
            logvar
        )

        recon = self.decode(z)

        return recon, mu, logvar

# =====================================================
# LOSS
# =====================================================

def davae_loss(
    recon,
    x,
    mu,
    logvar
):

    recon_loss = F.mse_loss(
        recon,
        x
    )

    kl_loss = -0.5 * torch.mean(
        1
        + logvar
        - mu.pow(2)
        - logvar.exp()
    )

    loss = (
        recon_loss
        + BETA * kl_loss
    )

    return loss

# =====================================================
# TRAIN ONE SERVICE
# =====================================================

summary_list = []

def process_service(
    normal_df,
    fault_df,
    service
):

    print("\n================")
    print(service)
    print("================")

    train_df = normal_df[
        normal_df["service"] == service
    ].copy()

    test_df = fault_df[
        fault_df["service"] == service
    ].copy()

    train_df = train_df.sort_values(
        "timestamp"
    )

    test_df = test_df.sort_values(
        "timestamp"
    )

    if len(train_df) < WINDOW_SIZE:
        print("Too few samples.")
        return

    scaler = StandardScaler()

    train_scaled = scaler.fit_transform(
        train_df[FEATURE_COLS]
    )

    test_scaled = scaler.transform(
        test_df[FEATURE_COLS]
    )

    X_train = create_windows(
        train_scaled,
        WINDOW_SIZE
    )

    X_test = create_windows(
        test_scaled,
        WINDOW_SIZE
    )

    train_tensor = torch.tensor(
        X_train,
        dtype=torch.float32
    )

    train_loader = DataLoader(

        TensorDataset(
            train_tensor
        ),

        batch_size=BATCH_SIZE,

        shuffle=True
    )

    model = DAVAE(
        len(FEATURE_COLS)
    ).to(DEVICE)

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LR
    )

    # ============================
    # TRAIN
    # ============================

    model.train()

    for epoch in range(EPOCHS):

        total_loss = 0

        for batch in train_loader:

            x = batch[0].to(DEVICE)

            optimizer.zero_grad()

            recon, mu, logvar = model(x)

            loss = davae_loss(
                recon,
                x,
                mu,
                logvar
            )

            loss.backward()

            optimizer.step()

            total_loss += loss.item()

        if epoch % 10 == 0:

            print(
                f"Epoch {epoch} "
                f"Loss={total_loss:.4f}"
            )

    torch.save(

        model.state_dict(),

        f"results/models/"
        f"davae_{service}.pth"
    )

    # ============================
    # TRAIN SCORE
    # ============================

    model.eval()

    with torch.no_grad():

        train_tensor = train_tensor.to(
            DEVICE
        )

        recon, _, _ = model(
            train_tensor
        )

        train_score = (

            (
                train_tensor
                - recon
            ) ** 2

        ).mean(
            dim=(1, 2)
        )

        train_score = \
            train_score.cpu().numpy()

    threshold = np.percentile(
        train_score,
        95
    )

    print(
        "Threshold:",
        threshold
    )

    # ============================
    # NORMAL FIGURE
    # ============================

    plt.figure(
        figsize=(15,5)
    )

    plt.plot(train_score)

    plt.axhline(
        threshold,
        color="red",
        linestyle="--"
    )

    plt.title(
        f"{service} Normal"
    )

    plt.tight_layout()

    plt.savefig(
        f"results/normal_figures/"
        f"{service}_normal.png",
        dpi=300
    )

    plt.close()

    # ============================
    # TEST
    # ============================

    test_tensor = torch.tensor(
        X_test,
        dtype=torch.float32
    ).to(DEVICE)

    with torch.no_grad():

        recon, _, _ = model(
            test_tensor
        )

        test_score = (

            (
                test_tensor
                - recon
            ) ** 2

        ).mean(
            dim=(1,2)
        )

        test_score = \
            test_score.cpu().numpy()

    prediction = (
        test_score > threshold
    ).astype(int)

    # ============================
    # CSV
    # ============================

    result_df = test_df.iloc[
        WINDOW_SIZE-1:
    ].copy()

    result_df[
        "anomaly_score"
    ] = test_score

    result_df[
        "prediction"
    ] = prediction

    result_df.to_csv(

        f"results/csv/"
        f"result_{service}.csv",

        index=False
    )

    anomaly_count = int(
        prediction.sum()
    )

    # ============================
    # FAULT FIGURE
    # ============================

    plt.figure(
        figsize=(15,5)
    )

    plt.plot(
        test_score,
        linewidth=1
    )

    plt.axhline(
        threshold,
        color="red",
        linestyle="--"
    )

    idx = np.where(
        prediction == 1
    )[0]

    plt.scatter(
        idx,
        test_score[idx],
        s=15
    )

    plt.title(
        f"{service} Fault"
    )

    plt.tight_layout()

    plt.savefig(
        f"results/fault_figures/"
        f"{service}_fault.png",
        dpi=300
    )

    plt.close()

    summary_list.append({

        "service":
            service,

        "threshold":
            threshold,

        "total_windows":
            len(test_score),

        "anomaly_count":
            anomaly_count,

        "anomaly_ratio":
            anomaly_count
            / len(test_score)
    })

# =====================================================
# MAIN
# =====================================================

normal_df = pd.read_csv(
    "normal_metrics.csv"
)

fault_df = pd.read_csv(
    "fault_metrics.csv"
)

services = sorted(
    normal_df["service"].unique()
)

print("\nServices:")

for s in services:

    print(s)

for service in services:

    process_service(
        normal_df,
        fault_df,
        service
    )

summary_df = pd.DataFrame(
    summary_list
)

summary_df.to_csv(
    "results/summary.csv",
    index=False
)

print("\nALL DONE")