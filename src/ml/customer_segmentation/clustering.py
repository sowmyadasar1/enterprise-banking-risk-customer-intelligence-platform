"""Clustering: K-Means, Hierarchical, DBSCAN with evaluation."""
import numpy as np
import pandas as pd
import joblib
import os
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from . import config
import warnings
warnings.filterwarnings('ignore')


def evaluate_kmeans(X_scaled):
    """Evaluate K-Means over a range of K values."""
    print("\n" + "="*70)
    print("  STEP 3: CLUSTERING — K-MEANS EVALUATION")
    print("="*70)

    results = []
    inertias = []
    for k in config.K_RANGE:
        km = KMeans(n_clusters=k, random_state=config.RANDOM_STATE, n_init=10, max_iter=300)
        labels = km.fit_predict(X_scaled)
        sil = silhouette_score(X_scaled, labels)
        db = davies_bouldin_score(X_scaled, labels)
        ch = calinski_harabasz_score(X_scaled, labels)
        inertias.append(km.inertia_)
        results.append({'k': k, 'silhouette': sil, 'davies_bouldin': db,
                        'calinski_harabasz': ch, 'inertia': km.inertia_})
        print(f"  K={k}: Silhouette={sil:.4f}  DB={db:.4f}  CH={ch:.1f}")

    results_df = pd.DataFrame(results)

    # Elbow plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    axes[0].plot(list(config.K_RANGE), inertias, 'bo-')
    axes[0].set_xlabel('Number of Clusters (K)')
    axes[0].set_ylabel('Inertia')
    axes[0].set_title('Elbow Method')

    axes[1].plot(list(config.K_RANGE), results_df['silhouette'], 'rs-')
    axes[1].set_xlabel('Number of Clusters (K)')
    axes[1].set_ylabel('Silhouette Score')
    axes[1].set_title('Silhouette Score by K')

    axes[2].plot(list(config.K_RANGE), results_df['davies_bouldin'], 'g^-')
    axes[2].set_xlabel('Number of Clusters (K)')
    axes[2].set_ylabel('Davies-Bouldin Index')
    axes[2].set_title('Davies-Bouldin Index by K')

    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'kmeans_evaluation.png'), dpi=150)
    plt.close()

    return results_df


def evaluate_hierarchical(X_scaled, best_k):
    """Evaluate Agglomerative Clustering with the best K."""
    print("\n  [Hierarchical Clustering]")
    hc = AgglomerativeClustering(n_clusters=best_k)
    labels = hc.fit_predict(X_scaled)
    sil = silhouette_score(X_scaled, labels)
    db = davies_bouldin_score(X_scaled, labels)
    ch = calinski_harabasz_score(X_scaled, labels)
    print(f"    K={best_k}: Silhouette={sil:.4f}  DB={db:.4f}  CH={ch:.1f}")
    return {'method': 'Hierarchical', 'k': best_k, 'silhouette': sil,
            'davies_bouldin': db, 'calinski_harabasz': ch, 'labels': labels}


def evaluate_dbscan(X_scaled):
    """Evaluate DBSCAN over parameter grid."""
    print("\n  [DBSCAN]")
    best_sil = -1
    best_result = None
    for eps in config.DBSCAN_EPS_RANGE:
        for ms in config.DBSCAN_MIN_SAMPLES:
            db = DBSCAN(eps=eps, min_samples=ms)
            labels = db.fit_predict(X_scaled)
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            noise = sum(labels == -1)
            
            # DBSCAN must segment at least 50% of the customers to be considered viable
            if n_clusters >= 2 and noise < len(X_scaled) * 0.5:
                mask = labels != -1
                if sum(mask) > n_clusters:
                    sil = silhouette_score(X_scaled[mask], labels[mask])
                    if sil > best_sil:
                        best_sil = sil
                        best_result = {
                            'method': 'DBSCAN', 'eps': eps, 'min_samples': ms,
                            'k': n_clusters, 'silhouette': sil, 'noise_points': noise,
                            'labels': labels
                        }
                    print(f"    eps={eps} ms={ms}: {n_clusters} clusters, {noise} noise, Sil={sil:.4f}")
            else:
                print(f"    eps={eps} ms={ms}: {n_clusters} clusters (insufficient), {noise} noise")

    if best_result:
        print(f"    Best DBSCAN: eps={best_result['eps']} ms={best_result['min_samples']} "
              f"Sil={best_result['silhouette']:.4f}")
    else:
        print("    DBSCAN could not find valid clusters.")
    return best_result


def run_clustering(X_scaled):
    """Run all clustering methods and select the best."""
    print("\n" + "="*70)
    print("  STEP 3: CLUSTERING")
    print("="*70)

    # 1. K-Means evaluation
    kmeans_results = evaluate_kmeans(X_scaled)
    best_k = int(kmeans_results.loc[kmeans_results['silhouette'].idxmax(), 'k'])
    print(f"\n  Best K-Means K: {best_k} (Silhouette={kmeans_results['silhouette'].max():.4f})")

    # Train final K-Means
    final_kmeans = KMeans(n_clusters=best_k, random_state=config.RANDOM_STATE, n_init=10)
    kmeans_labels = final_kmeans.fit_predict(X_scaled)
    kmeans_sil = silhouette_score(X_scaled, kmeans_labels)
    kmeans_db = davies_bouldin_score(X_scaled, kmeans_labels)
    kmeans_ch = calinski_harabasz_score(X_scaled, kmeans_labels)

    # 2. Hierarchical
    hc_result = evaluate_hierarchical(X_scaled, best_k)

    # 3. DBSCAN
    dbscan_result = evaluate_dbscan(X_scaled)

    # Compare and select best
    print("\n  === CLUSTERING COMPARISON ===")
    comparison = [
        {'method': 'K-Means', 'k': best_k, 'silhouette': kmeans_sil,
         'davies_bouldin': kmeans_db, 'calinski_harabasz': kmeans_ch},
        {'method': 'Hierarchical', 'k': hc_result['k'], 'silhouette': hc_result['silhouette'],
         'davies_bouldin': hc_result['davies_bouldin'], 'calinski_harabasz': hc_result['calinski_harabasz']},
    ]
    if dbscan_result:
        comparison.append({
            'method': 'DBSCAN', 'k': dbscan_result['k'], 'silhouette': dbscan_result['silhouette'],
            'davies_bouldin': 0, 'calinski_harabasz': 0
        })

    comp_df = pd.DataFrame(comparison).sort_values('silhouette', ascending=False)
    print(comp_df.to_string(index=False))

    best_method = comp_df.iloc[0]['method']
    print(f"\n  >>> BEST CLUSTERING: {best_method} (Silhouette={comp_df.iloc[0]['silhouette']:.4f})")

    # Use K-Means labels as default (most stable)
    if best_method == 'K-Means' or best_method == 'Hierarchical':
        final_labels = kmeans_labels
        # Save model
        joblib.dump(final_kmeans, os.path.join(config.MODELS_DIR, 'kmeans_model.joblib'))
    else:
        final_labels = dbscan_result['labels'] if dbscan_result else kmeans_labels
        joblib.dump(final_kmeans, os.path.join(config.MODELS_DIR, 'kmeans_model.joblib'))

    return final_labels, best_k, comp_df, kmeans_results
