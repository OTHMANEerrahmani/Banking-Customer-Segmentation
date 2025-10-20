import reflex as rx
from app.state import State
from app.components.base_layout import base_layout
from app.pages.home import progress_indicator


def config_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Configuration", class_name="text-xl font-bold text-gray-800 mb-4"),
        rx.el.div(
            rx.el.label("Clustering Algorithm", class_name="font-medium text-gray-700"),
            rx.el.div(
                rx.el.button(
                    "KMeans",
                    on_click=lambda: State.set_clustering_algorithm("kmeans"),
                    class_name=rx.cond(
                        State.clustering_algorithm == "kmeans",
                        "px-4 py-2 text-sm font-semibold text-white bg-sky-600 rounded-l-lg border border-sky-600",
                        "px-4 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-100 rounded-l-lg border border-gray-300",
                    ),
                ),
                rx.el.button(
                    "Hierarchical",
                    on_click=lambda: State.set_clustering_algorithm("hierarchical"),
                    class_name=rx.cond(
                        State.clustering_algorithm == "hierarchical",
                        "px-4 py-2 text-sm font-semibold text-white bg-sky-600 rounded-r-lg border border-sky-600",
                        "px-4 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-100 rounded-r-lg border border-r-gray-300 border-t-gray-300 border-b-gray-300",
                    ),
                ),
                class_name="flex mt-1",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label("Number of Clusters", class_name="font-medium text-gray-700"),
            rx.el.input(
                type="number",
                on_change=State.set_n_clusters,
                min=2,
                max=10,
                class_name="mt-1 w-full p-2 border border-gray-300 rounded-lg focus:ring-sky-500 focus:border-sky-500",
                default_value=State.n_clusters.to_string(),
            ),
            class_name="mb-4",
        ),
        rx.el.button(
            "Run Clustering",
            on_click=State.run_clustering,
            is_loading=State.is_processing,
            class_name="w-full px-6 py-3 bg-sky-600 text-white font-semibold rounded-xl shadow-md hover:bg-sky-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2",
        ),
        class_name="p-6 bg-white rounded-2xl border border-gray-200 shadow-lg",
    )


def results_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Clustering Results", class_name="text-xl font-bold text-gray-800 mb-4"
        ),
        rx.plotly(data=State.cluster_scatter_fig, class_name="w-full h-[500px]"),
        rx.cond(
            (State.clustering_algorithm == "hierarchical") & State.has_dendrogram_data,
            rx.el.div(
                rx.el.h4(
                    "Dendrogram", class_name="text-lg font-bold text-gray-800 my-4"
                ),
                rx.plotly(data=State.dendrogram_fig, class_name="w-full h-[400px]"),
            ),
            rx.fragment(),
        ),
        class_name="p-6 bg-white rounded-2xl border border-gray-200 shadow-lg mt-8",
    )


def clustering_page() -> rx.Component:
    """The clustering page."""
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Clustering Analysis", class_name="text-3xl font-bold text-gray-900"
                ),
                progress_indicator(),
                class_name="mb-8",
            ),
            rx.cond(
                State.pca_results.is_none(),
                rx.el.div(
                    rx.el.p(
                        "PCA results not found. Please complete the PCA step first.",
                        class_name="text-lg text-red-600",
                    ),
                    rx.el.button(
                        "Go to PCA Analysis",
                        on_click=rx.redirect("/pca_analysis"),
                        class_name="mt-4 px-4 py-2 bg-sky-600 text-white rounded-lg",
                    ),
                    class_name="text-center p-8 bg-white rounded-xl shadow-md",
                ),
                rx.el.div(
                    config_section(),
                    rx.cond(
                        State.is_processing,
                        rx.el.div(
                            rx.spinner(class_name="h-12 w-12 text-sky-600"),
                            rx.el.p(
                                "Running clustering...",
                                class_name="mt-4 text-lg font-medium text-gray-700",
                            ),
                            class_name="flex flex-col items-center justify-center p-16 mt-8 bg-white/50 rounded-2xl shadow-lg",
                        ),
                        rx.cond(
                            State.clustering_results.is_not_none(),
                            results_section(),
                            rx.fragment(),
                        ),
                    ),
                    class_name="space-y-8",
                ),
            ),
            class_name="p-4 sm:p-6 lg:p-8",
        )
    )