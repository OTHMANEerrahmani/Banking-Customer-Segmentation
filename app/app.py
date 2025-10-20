import reflex as rx
from app.pages.home import home_page
from app.pages.data_cleaning import data_cleaning_page
from app.state import State
from app.pages.pca_analysis import pca_analysis_page


def index() -> rx.Component:
    return home_page()


def data_cleaning() -> rx.Component:
    return data_cleaning_page()


def pca_analysis() -> rx.Component:
    return pca_analysis_page()


from app.pages.clustering_page import clustering_page


def clustering() -> rx.Component:
    return clustering_page()


from app.pages.profiles_page import profiles_page
from app.pages.insights_page import insights_page


def profiles() -> rx.Component:
    return profiles_page()


def insights() -> rx.Component:
    return insights_page()


app = rx.App(
    theme=rx.theme(
        appearance="light", accent_color="sky", gray_color="gray", radius="large"
    ),
    head_components=[
        rx.el.link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700;800&display=swap",
        )
    ],
)
app.add_page(index, route="/")
app.add_page(data_cleaning, route="/data_cleaning")
app.add_page(pca_analysis, route="/pca_analysis")
app.add_page(clustering, route="/clustering")
app.add_page(profiles, route="/profiles")
app.add_page(insights, route="/insights")