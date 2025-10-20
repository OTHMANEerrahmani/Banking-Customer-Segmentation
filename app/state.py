import reflex as rx
import pandas as pd
from typing import Any, Literal, Optional, TypedDict
import plotly.graph_objects as go
import io
import asyncio
import logging
import os
from pydantic import BaseModel
from app.utils.cleaning_utils import (
    clean_data,
    get_statistics,
    create_correlation_heatmap,
)

logging.basicConfig(level=logging.INFO)
WorkflowStage = Literal["Upload", "Cleaning", "PCA", "Clustering", "Insights"]


class Stats(BaseModel):
    rows: int = 0
    cols: int = 0
    missing_values: int = 0
    outliers: int = 0
    dtypes: dict[str, int] = {}


class ProfileData(TypedDict):
    size: int
    percentage: str
    feature_means: dict[str, float]
    distinguishing_features: list[str]


class AIPersona(TypedDict):
    cluster_id: str
    name: str
    description: str
    key_traits: list[str]


class AIInsights(TypedDict):
    marketing_recommendations: str
    personas: list[AIPersona]
    error: Optional[str]


class State(rx.State):
    """The main application state."""

    current_stage: WorkflowStage = "Upload"
    is_processing: bool = False
    sidebar_open: bool = True
    uploaded_file_name: str = ""
    raw_data: pd.DataFrame | None = None
    cleaned_data: pd.DataFrame | None = None
    original_stats: Stats = Stats()
    cleaned_stats: Stats = Stats()
    correlation_heatmap: go.Figure | None = go.Figure()
    preview_page: int = 1
    rows_per_page: int = 10
    pca_results: dict | None = None
    scree_plot: go.Figure = go.Figure()
    cumulative_variance_plot: go.Figure = go.Figure()
    clustering_algorithm: str = "kmeans"
    n_clusters: int = 4
    clustering_results: dict | None = None
    cluster_scatter_fig: go.Figure = go.Figure()
    dendrogram_fig: go.Figure = go.Figure()
    cluster_profiles: dict[str, ProfileData | dict] = {}
    ai_insights: AIInsights = {"marketing_recommendations": "", "personas": []}
    is_generating_insights: bool = False

    @rx.var
    def has_dendrogram_data(self) -> bool:
        return self.dendrogram_fig is not None and len(self.dendrogram_fig.data) > 0

    @rx.var
    def filtered_cluster_keys(self) -> list[str]:
        return [
            k
            for k in self.cluster_profiles.keys()
            if k not in ["summary_df", "feature_names"]
        ]

    @rx.var
    def workflow_stages(self) -> list[dict[str, str | bool]]:
        stages = ["Upload", "Cleaning", "PCA", "Clustering", "Insights"]
        current_index = stages.index(self.current_stage)
        return [
            {
                "name": stage,
                "completed": i < current_index,
                "current": i == current_index,
            }
            for i, stage in enumerate(stages)
        ]

    @rx.var
    def raw_data_preview(self) -> list[dict[str, float | int | str]]:
        if self.raw_data is not None and (not self.raw_data.empty):
            start = (self.preview_page - 1) * self.rows_per_page
            end = start + self.rows_per_page
            return self.raw_data.iloc[start:end].to_dict("records")
        return []

    @rx.var
    def raw_data_columns(self) -> list[str]:
        if self.raw_data is not None:
            return self.raw_data.columns.tolist()
        return []

    @rx.var
    def total_preview_pages(self) -> int:
        if self.raw_data is not None:
            return (len(self.raw_data) + self.rows_per_page - 1) // self.rows_per_page
        return 1

    @rx.event
    def set_sidebar_open(self, open: bool):
        self.sidebar_open = open

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            yield rx.toast.error("No file selected.")
            return
        self.is_processing = True
        yield
        try:
            upload_file = files[0]
            if not (
                upload_file.filename.endswith(".csv")
                or upload_file.filename.endswith(".xlsx")
            ):
                self.is_processing = False
                yield rx.toast.error(
                    "Invalid file type. Please upload a CSV or XLSX file."
                )
                return
            if upload_file.size > 50 * 1024 * 1024:
                self.is_processing = False
                yield rx.toast.error("File size exceeds 50MB limit.")
                return
            self.uploaded_file_name = upload_file.filename
            file_content = await upload_file.read()
            if self.uploaded_file_name.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(file_content))
            else:
                df = pd.read_excel(io.BytesIO(file_content))
            self.raw_data = df
            self.preview_page = 1
            yield State.run_data_cleaning
        except Exception as e:
            logging.exception(f"File upload failed: {e}")
            self.is_processing = False
            yield rx.toast.error(f"File processing failed: {e}")

    @rx.event(background=True)
    async def run_data_cleaning(self):
        async with self:
            if self.raw_data is None:
                self.is_processing = False
                yield rx.toast.error("No data available to clean.")
                return
            self.is_processing = True
            raw_data_copy = self.raw_data.copy()
        try:
            original_stats, _ = get_statistics(raw_data_copy)
            cleaned_df, outliers_removed = clean_data(raw_data_copy)
            cleaned_stats_data, _ = get_statistics(cleaned_df, outliers_removed)
            heatmap_fig = create_correlation_heatmap(cleaned_df)
            async with self:
                self.original_stats = Stats(**original_stats)
                self.cleaned_stats = Stats(**cleaned_stats_data)
                self.cleaned_data = cleaned_df
                self.correlation_heatmap = heatmap_fig
                self.current_stage = "Cleaning"
                self.is_processing = False
            yield rx.toast.success("Data cleaning complete!")
        except Exception as e:
            logging.exception(f"Data cleaning error: {e}")
            async with self:
                self.is_processing = False
            yield rx.toast.error(f"An error occurred during cleaning: {e}")

    @rx.event
    def next_preview_page(self):
        if self.preview_page < self.total_preview_pages:
            self.preview_page += 1

    @rx.event
    def prev_preview_page(self):
        if self.preview_page > 1:
            self.preview_page -= 1

    @rx.event
    def go_to_page(self, page_name: str):
        if page_name == "data_cleaning" and self.raw_data is None:
            return rx.toast.info("Please upload a file first.")
        return rx.redirect(f"/{page_name}")

    @rx.event
    def proceed_to_pca(self):
        self.current_stage = "PCA"
        return rx.redirect("/pca_analysis")

    @rx.event(background=True)
    async def run_pca(self):
        from app.utils.pca_utils import perform_pca

        async with self:
            if self.cleaned_data is None:
                yield rx.toast.error("No cleaned data to perform PCA.")
                return
            self.is_processing = True
            cleaned_data_copy = self.cleaned_data.copy()
        try:
            pca_results = perform_pca(cleaned_data_copy)
            async with self:
                self.pca_results = pca_results
                self.scree_plot = pca_results["scree_plot"]
                self.cumulative_variance_plot = pca_results["cumulative_variance_plot"]
                self.current_stage = "PCA"
                self.is_processing = False
            yield rx.toast.success("PCA completed successfully!")
        except Exception as e:
            logging.exception(f"PCA error: {e}")
            async with self:
                self.is_processing = False
            yield rx.toast.error(f"An error occurred during PCA: {e}")

    @rx.event
    def proceed_to_clustering(self):
        self.current_stage = "Clustering"
        return rx.redirect("/clustering")

    @rx.event
    def set_clustering_algorithm(self, algorithm: str):
        self.clustering_algorithm = algorithm

    @rx.event
    def set_n_clusters(self, n: int):
        self.n_clusters = int(n)

    @rx.event(background=True)
    async def run_clustering(self):
        from app.utils.clustering_utils import (
            perform_kmeans,
            perform_hierarchical,
            create_cluster_scatter,
        )

        async with self:
            if self.pca_results is None or "transformed_data" not in self.pca_results:
                yield rx.toast.error("PCA data not found. Please run PCA first.")
                return
            self.is_processing = True
            pca_data = self.pca_results["transformed_data"]
            algo = self.clustering_algorithm
            n_clusters = self.n_clusters
        try:
            if algo == "kmeans":
                results = perform_kmeans(pca_data, n_clusters)
            else:
                results = perform_hierarchical(pca_data, n_clusters)
            scatter_fig = create_cluster_scatter(pca_data, results["labels"])
            async with self:
                self.clustering_results = results
                self.cluster_scatter_fig = scatter_fig
                if algo == "hierarchical":
                    self.dendrogram_fig = results["dendrogram_fig"]
                else:
                    self.dendrogram_fig = go.Figure()
                self.current_stage = "Clustering"
                self.is_processing = False
            yield rx.toast.success("Clustering complete!")
        except Exception as e:
            logging.exception(f"Clustering error: {e}")
            async with self:
                self.is_processing = False
            yield rx.toast.error(f"Clustering failed: {e}")

    @rx.event
    def proceed_to_profiles(self):
        self.current_stage = "Insights"
        return rx.redirect("/profiles")

    @rx.event(background=True)
    async def generate_cluster_profiles(self):
        from app.utils.clustering_utils import compute_cluster_profiles

        async with self:
            if self.cleaned_data is None or self.clustering_results is None:
                yield rx.toast.error("Missing data for profile generation.")
                return
            self.is_processing = True
            cleaned_df = self.cleaned_data.copy()
            labels = self.clustering_results["labels"]
        try:
            profiles = compute_cluster_profiles(cleaned_df, labels)
            async with self:
                self.cluster_profiles = profiles
                self.is_processing = False
            yield rx.toast.success("Cluster profiles generated!")
        except Exception as e:
            logging.exception(f"Profile generation error: {e}")
            async with self:
                self.is_processing = False
            yield rx.toast.error(f"Profile generation failed: {e}")

    @rx.event
    def proceed_to_insights(self):
        return rx.redirect("/insights")

    @rx.event(background=True)
    async def generate_ai_insights(self):
        from app.utils.google_ai_utils import generate_cluster_insights, check_api_key

        if not check_api_key():
            yield rx.toast.error("GOOGLE_API_KEY not set. Cannot generate insights.")
            return
        async with self:
            self.is_generating_insights = True
            self.ai_insights = {"marketing_recommendations": "", "personas": []}
            if not self.cluster_profiles:
                yield rx.toast.error("Please generate cluster profiles first.")
                self.is_generating_insights = False
                return
            profiles_data = self.cluster_profiles
        try:
            insights = await asyncio.to_thread(generate_cluster_insights, profiles_data)
            async with self:
                self.ai_insights = insights
                self.is_generating_insights = False
            yield rx.toast.success("AI insights generated!")
        except Exception as e:
            logging.exception(f"AI insight generation error: {e}")
            async with self:
                self.is_generating_insights = False
                self.ai_insights["error"] = f"AI insight generation failed: {e}"
            yield rx.toast.error(f"AI insight generation failed: {e}")

    @rx.event
    def export_clustered_data(self) -> rx.event.EventSpec:
        if self.cleaned_data is None or self.clustering_results is None:
            return rx.toast.error("No data to export.")
        df = self.cleaned_data.copy()
        df["cluster"] = self.clustering_results["labels"]
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return rx.download(data=buffer.read(), filename="clustered_customer_data.csv")

    @rx.event
    def export_cluster_profiles(self) -> rx.event.EventSpec:
        if not self.cluster_profiles or "summary_df" not in self.cluster_profiles:
            return rx.toast.error("No profiles to export.")
        summary_df = pd.DataFrame(self.cluster_profiles["summary_df"])
        buffer = io.BytesIO()
        summary_df.to_csv(buffer, index=True)
        buffer.seek(0)
        return rx.download(data=buffer.read(), filename="cluster_profiles_summary.csv")