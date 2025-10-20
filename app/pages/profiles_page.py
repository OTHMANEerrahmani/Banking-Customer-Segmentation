import reflex as rx
from app.state import State
from app.components.base_layout import base_layout
from app.pages.home import progress_indicator
import plotly.graph_objects as go


def profile_card(cluster_id: str, profile: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            f"Cluster {cluster_id}", class_name="text-xl font-bold text-sky-600 mb-4"
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p("Size", class_name="font-medium text-gray-500"),
                rx.el.p(profile["size"].to_string(), class_name="text-2xl font-bold"),
            ),
            rx.el.div(
                rx.el.p("Percentage", class_name="font-medium text-gray-500"),
                rx.el.p(profile["percentage"], class_name="text-2xl font-bold"),
            ),
            class_name="grid grid-cols-2 gap-4 mb-4",
        ),
        rx.el.div(
            rx.el.h4(
                "Top Distinguishing Features",
                class_name="text-lg font-semibold text-gray-800 mb-2",
            ),
            rx.el.ul(
                rx.foreach(
                    profile["distinguishing_features"],
                    lambda feature: rx.el.li(
                        rx.icon("star", class_name="h-4 w-4 text-yellow-500 mr-2"),
                        feature,
                        class_name="flex items-center p-2 bg-gray-100 rounded-md text-sm",
                    ),
                ),
                class_name="space-y-2",
            ),
            class_name="mb-4",
        ),
        rx.el.h4(
            "Feature Averages", class_name="text-lg font-semibold text-gray-800 mb-2"
        ),
        rx.el.div(
            rx.foreach(
                profile["feature_means"].keys(),
                lambda key: rx.el.div(
                    rx.el.p(key, class_name="font-medium"),
                    rx.el.p(profile["feature_means"][key].to_string()),
                    class_name="flex justify-between text-sm p-1 bg-gray-50 even:bg-gray-100 rounded",
                ),
            ),
            class_name="max-h-48 overflow-y-auto pr-2",
        ),
        class_name="p-6 bg-white rounded-2xl border border-gray-200 shadow-lg",
    )


def profiles_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.h1(
                "Customer Profiles", class_name="text-3xl font-bold text-gray-900 mb-8"
            ),
            progress_indicator(),
            rx.cond(
                State.clustering_results.is_none(),
                rx.el.div(
                    rx.el.p(
                        "Clustering not performed yet. Please complete the clustering step.",
                        class_name="text-red-600",
                    ),
                    rx.el.button(
                        "Go to Clustering",
                        on_click=rx.redirect("/clustering"),
                        class_name="mt-4 px-4 py-2 bg-sky-600 text-white rounded-lg",
                    ),
                    class_name="text-center p-8 bg-white rounded-xl shadow-md",
                ),
                rx.el.div(
                    rx.cond(
                        State.cluster_profiles.keys().length() == 0,
                        rx.el.div(
                            rx.el.button(
                                "Generate Cluster Profiles",
                                on_click=State.generate_cluster_profiles,
                                is_loading=State.is_processing,
                                class_name="px-6 py-3 bg-sky-600 text-white font-semibold rounded-xl shadow-md hover:bg-sky-700 flex items-center gap-2",
                            ),
                            class_name="text-center",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.foreach(
                                    State.filtered_cluster_keys,
                                    lambda cluster_id: profile_card(
                                        cluster_id, State.cluster_profiles[cluster_id]
                                    ),
                                ),
                                class_name="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-8",
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Export Clustered Data (CSV)",
                                    on_click=State.export_clustered_data,
                                    class_name="px-4 py-2 bg-green-600 text-white rounded-lg",
                                ),
                                rx.el.button(
                                    "Export Profiles Summary (CSV)",
                                    on_click=State.export_cluster_profiles,
                                    class_name="px-4 py-2 bg-green-600 text-white rounded-lg",
                                ),
                                rx.el.button(
                                    "Proceed to AI Insights",
                                    on_click=State.proceed_to_insights,
                                    class_name="px-6 py-3 bg-sky-600 text-white font-semibold rounded-xl shadow-md hover:bg-sky-700",
                                ),
                                class_name="flex justify-between items-center mt-8",
                            ),
                        ),
                    )
                ),
            ),
            class_name="p-4 sm:p-6 lg:p-8",
        )
    )