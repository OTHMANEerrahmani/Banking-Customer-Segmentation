import pandas as pd
from sklearn.decomposition import PCA
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import logging


def perform_pca(df: pd.DataFrame) -> dict:
    """
    Performs PCA on the cleaned dataframe.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    pca = PCA(random_state=42)
    pca_transformed = pca.fit_transform(df)
    explained_variance = pca.explained_variance_ratio_
    cumulative_variance = np.cumsum(explained_variance)
    optimal_n_components = np.argmax(cumulative_variance >= 0.8) + 1
    scree_plot = px.bar(
        x=range(1, len(explained_variance) + 1),
        y=explained_variance,
        labels={"x": "Principal Component", "y": "Explained Variance"},
        title="Scree Plot",
    )
    scree_plot.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Open Sans", "color": "#4A5568"},
    )
    cumulative_plot = go.Figure()
    cumulative_plot.add_trace(
        go.Scatter(
            x=np.arange(1, len(cumulative_variance) + 1),
            y=cumulative_variance,
            mode="lines+markers",
            name="Cumulative Variance",
        )
    )
    cumulative_plot.add_hline(
        y=0.8,
        line_dash="dot",
        annotation_text="80% Threshold",
        annotation_position="bottom right",
    )
    cumulative_plot.update_layout(
        title="Cumulative Explained Variance",
        xaxis_title="Number of Components",
        yaxis_title="Cumulative Variance",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Open Sans", "color": "#4A5568"},
    )
    loadings = pd.DataFrame(
        pca.components_.T,
        columns=[f"PC{i + 1}" for i in range(len(df.columns))],
        index=df.columns,
    )
    logging.info(f"PCA completed. Optimal components: {optimal_n_components}")
    return {
        "transformed_data": pca_transformed,
        "explained_variance": explained_variance,
        "cumulative_variance": cumulative_variance,
        "components": pca.components_,
        "optimal_n_components": int(optimal_n_components),
        "loadings": loadings,
        "scree_plot": scree_plot,
        "cumulative_variance_plot": cumulative_plot,
    }