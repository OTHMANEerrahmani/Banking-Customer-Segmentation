import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import plotly.express as px
import logging


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """
    Cleans the dataframe by handling missing values, outliers, and encoding.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    df_cleaned = df.copy()
    for col in df_cleaned.columns:
        if df_cleaned[col].isnull().sum() > 0:
            if pd.api.types.is_numeric_dtype(df_cleaned[col]):
                median_val = df_cleaned[col].median()
                df_cleaned[col] = df_cleaned[col].fillna(median_val)
            else:
                mode_val = df_cleaned[col].mode()[0]
                df_cleaned[col] = df_cleaned[col].fillna(mode_val)
    for col in df_cleaned.select_dtypes(include=np.number).columns:
        df_cleaned[col] = df_cleaned[col].apply(lambda x: max(x, 0))
    numeric_cols = df_cleaned.select_dtypes(include=np.number).columns
    initial_rows = len(df_cleaned)
    for col in numeric_cols:
        Q1 = df_cleaned[col].quantile(0.25)
        Q3 = df_cleaned[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df_cleaned = df_cleaned[
            (df_cleaned[col] >= lower_bound) & (df_cleaned[col] <= upper_bound)
        ]
    outliers_removed = initial_rows - len(df_cleaned)
    scaler = StandardScaler()
    df_cleaned[numeric_cols] = scaler.fit_transform(df_cleaned[numeric_cols])
    categorical_cols = df_cleaned.select_dtypes(include=["object", "category"]).columns
    for col in categorical_cols:
        le = LabelEncoder()
        df_cleaned[col] = le.fit_transform(df_cleaned[col])
    logging.info("Data cleaning completed successfully.")
    return (df_cleaned, outliers_removed)


def get_statistics(
    df: pd.DataFrame, outliers_removed: int = 0
) -> tuple[dict, pd.DataFrame]:
    """
    Computes summary statistics for a dataframe.
    """
    if not isinstance(df, pd.DataFrame):
        return (
            {"rows": 0, "cols": 0, "missing_values": 0, "outliers": 0, "dtypes": {}},
            pd.DataFrame(),
        )
    dtype_counts = df.dtypes.apply(lambda x: x.name).value_counts()
    stats = {
        "rows": len(df),
        "cols": len(df.columns),
        "missing_values": int(df.isnull().sum().sum()),
        "outliers": outliers_removed,
        "dtypes": {k: int(v) for k, v in dtype_counts.items()},
    }
    return (stats, df)


def create_correlation_heatmap(df: pd.DataFrame):
    """
    Creates a correlation heatmap using Plotly.
    """
    if not isinstance(df, pd.DataFrame) or df.select_dtypes(include=np.number).empty:
        return px.imshow(
            pd.DataFrame(), title="Not enough numeric data for correlation heatmap"
        )
    corr = df.select_dtypes(include=np.number).corr()
    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Feature Correlation Heatmap",
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Open Sans", "color": "#4A5568"},
        title_font_size=20,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_xaxes(tickangle=45)
    return fig