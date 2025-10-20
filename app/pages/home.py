import reflex as rx
from app.state import State
from app.components.base_layout import base_layout


def progress_indicator() -> rx.Component:
    """Visualizes the workflow progress."""
    return rx.el.div(
        rx.el.ol(
            rx.foreach(
                State.workflow_stages,
                lambda stage: rx.el.li(
                    rx.el.span(
                        rx.icon("check", class_name="h-5 w-5"),
                        class_name=rx.cond(
                            stage["completed"],
                            "flex items-center justify-center w-10 h-10 bg-sky-600 rounded-full",
                            "flex items-center justify-center w-10 h-10 bg-gray-300 rounded-full",
                        ),
                    ),
                    rx.el.div(
                        stage["name"],
                        class_name="mt-2 text-sm font-medium text-gray-600",
                    ),
                    class_name="relative flex flex-col items-center justify-start",
                ),
            ),
            class_name="flex items-start justify-between w-full text-sm font-medium text-center text-white",
        ),
        class_name="w-full max-w-4xl mx-auto my-12",
    )


def workflow_card(icon: str, title: str, description: str) -> rx.Component:
    """A card describing a step in the workflow."""
    return rx.el.div(
        rx.icon(icon, class_name="h-10 w-10 text-sky-500 mb-4"),
        rx.el.h3(title, class_name="text-lg font-bold text-gray-800 mb-2"),
        rx.el.p(description, class_name="text-sm text-gray-600"),
        class_name="bg-white p-6 rounded-2xl border border-gray-200 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300",
    )


def home_page() -> rx.Component:
    """The home page of the application."""
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Customer Segmentation Analysis",
                    class_name="text-4xl font-extrabold text-gray-900 tracking-tight",
                ),
                rx.el.p(
                    "An end-to-end platform for uploading, cleaning, and analyzing customer data to uncover valuable segments.",
                    class_name="mt-4 text-lg text-gray-600 max-w-3xl mx-auto",
                ),
                class_name="text-center p-8",
            ),
            progress_indicator(),
            rx.el.div(
                rx.el.button(
                    "Get Started",
                    rx.icon("arrow-right", class_name="ml-2"),
                    on_click=lambda: State.go_to_page("data_cleaning"),
                    class_name="px-8 py-4 bg-sky-600 text-white font-semibold rounded-xl shadow-lg hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-opacity-75 transform hover:scale-105 transition-all duration-300",
                ),
                class_name="text-center my-12",
            ),
            rx.el.div(
                workflow_card(
                    "cloud_upload",
                    "1. Upload Data",
                    "Securely upload your customer data in CSV or Excel format.",
                ),
                workflow_card(
                    "sparkles",
                    "2. Automated Cleaning",
                    "Our pipeline automatically handles missing values, outliers, and normalization.",
                ),
                workflow_card(
                    "bar-chart-2",
                    "3. PCA Analysis",
                    "Reduce dimensionality and discover the most important features driving variance.",
                ),
                workflow_card(
                    "git-merge",
                    "4. Clustering",
                    "Apply KMeans and Hierarchical clustering to group customers into meaningful segments.",
                ),
                workflow_card(
                    "lightbulb",
                    "5. AI-Powered Insights",
                    "Get automated explanations and marketing recommendations for each customer segment.",
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto",
            ),
            class_name="w-full p-4 sm:p-6 lg:p-8",
        )
    )