"""Dimensionality Reduction: PCA for visualization."""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import joblib
import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from . import config


def run_pca(X_scaled, labels, n_components_2d=2, n_components_3d=3):
    """Run PCA for 2D and 3D visualization of clusters."""
    print("\n" + "=" * 70)
    print("  STEP 4: DIMENSIONALITY REDUCTION (PCA)")
    print("=" * 70)

    # Full PCA for variance analysis
    pca_full = PCA(random_state=config.RANDOM_STATE)
    pca_full.fit(X_scaled)

    cumvar = np.cumsum(pca_full.explained_variance_ratio_)
    n_95 = np.argmax(cumvar >= 0.95) + 1
    print(f"  Components for 95% variance: {n_95}")
    print(f"  Top 5 components explain: {cumvar[4]*100:.1f}%")

    # Variance explained plot
    plt.figure(figsize=(10, 5))
    plt.bar(
        range(1, min(21, len(cumvar) + 1)),
        pca_full.explained_variance_ratio_[:20],
        alpha=0.7,
        label="Individual",
    )
    plt.step(
        range(1, min(21, len(cumvar) + 1)),
        cumvar[:20],
        where="mid",
        label="Cumulative",
        color="red",
    )
    plt.xlabel("Principal Component")
    plt.ylabel("Variance Explained")
    plt.title("PCA Variance Explained")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, "pca_variance.png"), dpi=150)
    plt.close()

    # 2D PCA
    pca_2d = PCA(n_components=n_components_2d, random_state=config.RANDOM_STATE)
    X_2d = pca_2d.fit_transform(X_scaled)
    print(
        f"  2D PCA variance retained: {sum(pca_2d.explained_variance_ratio_)*100:.1f}%"
    )

    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(
        X_2d[:, 0], X_2d[:, 1], c=labels, cmap="Set1", alpha=0.6, s=10
    )
    plt.colorbar(scatter, label="Cluster")
    plt.xlabel(f"PC1 ({pca_2d.explained_variance_ratio_[0]*100:.1f}%)")
    plt.ylabel(f"PC2 ({pca_2d.explained_variance_ratio_[1]*100:.1f}%)")
    plt.title("Customer Segments — PCA 2D Projection")
    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, "pca_2d_clusters.png"), dpi=150)
    plt.close()

    # 3D PCA
    pca_3d = PCA(n_components=n_components_3d, random_state=config.RANDOM_STATE)
    X_3d = pca_3d.fit_transform(X_scaled)
    print(
        f"  3D PCA variance retained: {sum(pca_3d.explained_variance_ratio_)*100:.1f}%"
    )

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")
    scatter = ax.scatter(
        X_3d[:, 0], X_3d[:, 1], X_3d[:, 2], c=labels, cmap="Set1", alpha=0.5, s=8
    )
    ax.set_xlabel(f"PC1 ({pca_3d.explained_variance_ratio_[0]*100:.1f}%)")
    ax.set_ylabel(f"PC2 ({pca_3d.explained_variance_ratio_[1]*100:.1f}%)")
    ax.set_zlabel(f"PC3 ({pca_3d.explained_variance_ratio_[2]*100:.1f}%)")
    ax.set_title("Customer Segments — PCA 3D Projection")
    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, "pca_3d_clusters.png"), dpi=150)
    plt.close()

    joblib.dump(pca_2d, os.path.join(config.MODELS_DIR, "pca_2d.joblib"))
    print("  Saved: PCA visualizations")

    return X_2d, X_3d, pca_2d
