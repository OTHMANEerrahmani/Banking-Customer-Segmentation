import reflex as rx
from app.components.sidebar import sidebar
from app.state import State


def base_layout(child: rx.Component, *args, **kwargs) -> rx.Component:
    """The base layout for all pages."""
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.button(
                rx.icon(
                    tag=rx.cond(State.sidebar_open, "x", "menu"), class_name="h-6 w-6"
                ),
                on_click=lambda: State.set_sidebar_open(~State.sidebar_open),
                class_name="fixed top-4 right-4 z-50 p-2 rounded-full bg-white/50 backdrop-blur-sm shadow-md hover:bg-gray-100 transition-colors lg:hidden",
            ),
            child,
            class_name="transition-all duration-300 lg:ml-64",
        ),
        *args,
        class_name="font-['Open_Sans'] bg-gray-50 min-h-screen text-gray-800",
        **kwargs,
    )