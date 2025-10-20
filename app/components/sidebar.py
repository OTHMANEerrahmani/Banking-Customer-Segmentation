import reflex as rx
from app.state import State


def nav_item(text: str, icon: str, url: str) -> rx.Component:
    """A navigation item with an icon and text."""
    return rx.el.a(
        rx.el.li(
            rx.icon(
                icon,
                class_name="w-6 h-6 mr-3 text-gray-400 group-hover:text-sky-500 transition-colors",
            ),
            rx.el.span(
                text,
                class_name="text-gray-700 group-hover:text-sky-600 font-medium transition-colors",
            ),
            class_name="flex items-center p-3 rounded-lg hover:bg-sky-50 cursor-pointer group",
        ),
        href=url,
    )


def sidebar() -> rx.Component:
    """The main sidebar for navigation."""
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.icon("area-chart", class_name="h-8 w-8 text-sky-500"),
                rx.el.h2(
                    "Client Segmentation",
                    class_name="text-xl font-bold text-gray-800 ml-2",
                ),
                class_name="flex items-center p-4 border-b border-gray-200",
            ),
            rx.el.nav(
                rx.el.ul(
                    nav_item("Home", "home", "/"),
                    nav_item("Data Cleaning", "droplet", "/data_cleaning"),
                    nav_item("PCA Analysis", "bar-chart-2", "/pca_analysis"),
                    nav_item("Clustering", "git-merge", "/clustering"),
                    nav_item("Customer Profiles", "users", "/profiles"),
                    nav_item("Insights", "lightbulb", "/insights"),
                    class_name="space-y-2",
                ),
                class_name="p-4",
            ),
        ),
        rx.el.div(
            rx.el.p("© 2024 Banking Analytics", class_name="text-xs text-gray-500"),
            class_name="p-4 border-t border-gray-200 mt-auto",
        ),
        class_name=rx.cond(
            State.sidebar_open,
            "fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200 flex flex-col transform translate-x-0 transition-transform duration-300 ease-in-out z-40 shadow-lg lg:translate-x-0",
            "fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200 flex flex-col transform -translate-x-full transition-transform duration-300 ease-in-out z-40 shadow-lg lg:translate-x-0",
        ),
    )