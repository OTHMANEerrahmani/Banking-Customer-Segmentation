import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, adjusted_rand_score
import plotly.express as px
import plotly.graph_objects as go
from scipy.cluster.hierarchy import dendrogram, linkage
import logging


def perform_kmeans(data: pd.DataFrame, n_clusters: int) -> dict:
    """Performs KMeans clustering."""
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(data)
    score = silhouette_score(data, labels)
    return {
        "labels": labels,
        "centroids": kmeans.cluster_centers_,
        "silhouette_score": score,
        "cluster_sizes": pd.Series(labels).value_counts().to_dict(),
    }


def perform_hierarchical(data: pd.DataFrame, n_clusters: int) -> dict:
    """Performs Hierarchical clustering."""
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage="ward")
    labels = model.fit_predict(data)
    score = silhouette_score(data, labels)
    linked = linkage(data, "ward")
    dendro_fig = create_dendrogram(linked)
    return {
        "labels": labels,
        "dendrogram_fig": dendro_fig,
        "silhouette_score": score,
        "cluster_sizes": pd.Series(labels).value_counts().to_dict(),
    }


def create_cluster_scatter(data: pd.DataFrame, labels: np.ndarray) -> go.Figure:
    """Creates a scatter plot of clusters."""
    df = pd.DataFrame(data, columns=[f"PC{i + 1}" for i in range(data.shape[1])])
    df["cluster"] = labels.astype(str)
    fig = px.scatter(
        df,
        x="PC1",
        y="PC2",
        color="cluster",
        title="Clusters on Principal Components",
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Open Sans", "color": "#4A5568"},
        legend_title_text="Cluster",
    )
    return fig


def compute_cluster_profiles(df: pd.DataFrame, labels: np.ndarray) -> dict:
    """Computes descriptive statistics for each cluster."""
    df_labeled = df.copy()
    df_labeled["cluster"] = labels
    profiles = {}
    numeric_cols = df.select_dtypes(include=np.number).columns
    global_means = df_labeled[numeric_cols].mean()
    for i in sorted(df_labeled["cluster"].unique()):
        cluster_df = df_labeled[df_labeled["cluster"] == i]
        profile = {
            "size": len(cluster_df),
            "percentage": f"{len(cluster_df) / len(df_labeled) * 100:.2f}%",
            "feature_means": cluster_df[numeric_cols].mean().to_dict(),
            "distinguishing_features": identify_distinguishing_features(
                cluster_df, global_means, numeric_cols
            ),
        }
        profiles[str(i)] = profile
    summary_df = pd.DataFrame({i: p["feature_means"] for i, p in profiles.items()})
    summary_df.loc["size"] = {i: p["size"] for i, p in profiles.items()}
    profiles["summary_df"] = summary_df.to_dict()
    profiles["feature_names"] = numeric_cols.tolist()
    return profiles


def identify_distinguishing_features(
    cluster_df: pd.DataFrame, global_means: pd.Series, numeric_cols: list
) -> list:
    """Identifies top 3 features that most distinguish a cluster from the global average."""
    cluster_means = cluster_df[numeric_cols].mean()
    deviation = ((cluster_means - global_means) / global_means).abs()
    top_features = deviation.nlargest(3).index.tolist()
    return top_features


def create_dendrogram(linked_matrix) -> go.Figure:
    """Creates a dendrogram from a linkage matrix."""
    dendro = dendrogram(linked_matrix, no_plot=True)
    icoord = np.array(dendro["icoord"])
    dcoord = np.array(dendro["dcoord"])
    fig = go.Figure()
    for i in range(len(icoord)):
        fig.add_trace(
            go.Scatter(x=dcoord[i], y=icoord[i], mode="lines", line=dict(color="gray"))
        )
    fig.update_layout(
        title_text="Hierarchical Clustering Dendrogram",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        yaxis=dict(title="Distance"),
        xaxis=dict(title="Data Points"),
    )
    return fig