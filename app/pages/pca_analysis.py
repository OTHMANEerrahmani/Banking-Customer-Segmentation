import reflex as rx
from app.state import State
from app.components.base_layout import base_layout
from app.pages.home import progress_indicator


def pca_analysis_page() -> rx.Component:
    """The PCA analysis page."""
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1("PCA Analysis", class_name="text-3xl font-bold text-gray-900"),
                progress_indicator(),
                class_name="mb-8",
            ),
            rx.cond(
                State.cleaned_data.is_none(),
                rx.el.div(
                    rx.el.p(
                        "Cleaned data not found. Please complete the data cleaning step first.",
                        class_name="text-lg text-red-600",
                    ),
                    rx.el.button(
                        "Go to Data Cleaning",
                        on_click=rx.redirect("/data_cleaning"),
                        class_name="mt-4 px-4 py-2 bg-sky-600 text-white rounded-lg",
                    ),
                    class_name="text-center p-8 bg-white rounded-xl shadow-md",
                ),
                rx.el.div(
                    rx.cond(
                        State.is_processing & State.pca_results.is_none(),
                        rx.el.div(
                            rx.spinner(class_name="h-12 w-12 text-sky-600"),
                            rx.el.p(
                                "Running PCA, please wait...",
                                class_name="mt-4 text-lg font-medium text-gray-700",
                            ),
                            class_name="flex flex-col items-center justify-center p-16 bg-white/50 rounded-2xl shadow-lg",
                        ),
                        rx.cond(
                            State.pca_results.is_not_none(),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.h3(
                                            "Scree Plot",
                                            class_name="text-xl font-bold text-gray-800 mb-4",
                                        ),
                                        rx.plotly(
                                            data=State.scree_plot, class_name="w-full"
                                        ),
                                        class_name="p-6 bg-white rounded-2xl border border-gray-200 shadow-lg",
                                    ),
                                    rx.el.div(
                                        rx.el.h3(
                                            "Cumulative Variance",
                                            class_name="text-xl font-bold text-gray-800 mb-4",
                                        ),
                                        rx.plotly(
                                            data=State.cumulative_variance_plot,
                                            class_name="w-full",
                                        ),
                                        class_name="p-6 bg-white rounded-2xl border border-gray-200 shadow-lg",
                                    ),
                                    class_name="grid md:grid-cols-2 gap-8 mb-8",
                                ),
                                rx.el.div(
                                    rx.el.h3(
                                        "Component Summary",
                                        class_name="text-xl font-bold text-gray-800 mb-4",
                                    ),
                                    rx.el.p(
                                        f"Optimal components for >80% variance: {State.pca_results['optimal_n_components']}",
                                        class_name="text-lg font-medium text-gray-700",
                                    ),
                                    class_name="p-6 bg-white rounded-2xl border border-gray-200 shadow-lg mb-8 text-center",
                                ),
                                rx.el.div(
                                    rx.el.button(
                                        "Proceed to Clustering",
                                        rx.icon("arrow_right"),
                                        on_click=State.proceed_to_clustering,
                                        class_name="px-6 py-3 bg-sky-600 text-white font-semibold rounded-xl shadow-md hover:bg-sky-700 flex items-center gap-2",
                                    ),
                                    class_name="flex justify-end mt-8",
                                ),
                                class_name="w-full",
                            ),
                            rx.fragment(),
                        ),
                    ),
                    on_mount=State.run_pca,
                ),
            ),
            class_name="p-4 sm:p-6 lg:p-8",
        )
    )