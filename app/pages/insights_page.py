import reflex as rx
from app.state import State
from app.components.base_layout import base_layout


def marketing_recommendations_card() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            rx.cond(
                State.ai_insights.contains("error"),
                "Error Generating Insights",
                "Marketing Recommendations",
            ),
            class_name="text-xl font-bold text-gray-800 mb-4",
        ),
        rx.el.p(
            State.ai_insights.get("marketing_recommendations", ""),
            class_name=rx.cond(
                State.ai_insights.contains("error"),
                "text-red-600 leading-relaxed",
                "text-gray-600 leading-relaxed",
            ),
        ),
        class_name=rx.cond(
            State.ai_insights.contains("error"),
            "p-6 bg-red-50 rounded-2xl border border-red-200 shadow-lg",
            "p-6 bg-white rounded-2xl border border-gray-200 shadow-lg",
        ),
    )


def persona_card(persona: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.h4(
            f"Cluster {persona['cluster_id']}: {persona['name']}",
            class_name="text-lg font-bold text-sky-600 mb-2",
        ),
        rx.el.p(
            persona["description"], class_name="text-gray-600 leading-relaxed mb-4"
        ),
        rx.el.h5("Key Traits", class_name="font-semibold text-gray-700 mb-2"),
        rx.el.ul(
            rx.foreach(
                persona["key_traits"],
                lambda trait: rx.el.li(
                    rx.icon("star", class_name="h-4 w-4 text-yellow-500 mr-2 shrink-0"),
                    trait,
                    class_name="flex items-start text-sm text-gray-600",
                ),
            ),
            class_name="space-y-2",
        ),
        class_name="p-6 bg-white rounded-2xl border border-gray-200 shadow-lg",
    )


def insights_page() -> rx.Component:
    """The AI insights page."""
    return base_layout(
        rx.el.div(
            rx.el.h1(
                "AI-Powered Insights",
                class_name="text-3xl font-bold text-gray-900 mb-8",
            ),
            rx.cond(
                State.cluster_profiles.keys().length() == 0,
                rx.el.div(
                    rx.el.p(
                        "Cluster profiles not generated. Please complete the profiles step first.",
                        class_name="text-red-600",
                    ),
                    rx.el.button(
                        "Go to Profiles",
                        on_click=rx.redirect("/profiles"),
                        class_name="mt-4 px-4 py-2 bg-sky-600 text-white rounded-lg",
                    ),
                    class_name="text-center p-8 bg-white rounded-xl shadow-md",
                ),
                rx.el.div(
                    rx.el.button(
                        "Generate AI Insights",
                        on_click=State.generate_ai_insights,
                        is_loading=State.is_generating_insights,
                        class_name="w-full mb-8 px-6 py-3 bg-sky-600 text-white font-semibold rounded-xl shadow-md hover:bg-sky-700 disabled:opacity-50 flex items-center justify-center gap-2",
                    ),
                    rx.cond(
                        State.is_generating_insights,
                        rx.el.div(
                            rx.spinner(class_name="h-12 w-12 text-sky-600"),
                            rx.el.p(
                                "AI is analyzing your clusters...",
                                class_name="mt-4 text-lg font-medium text-gray-700",
                            ),
                            class_name="flex flex-col items-center justify-center p-16 bg-white/50 rounded-2xl shadow-lg",
                        ),
                        rx.cond(
                            State.ai_insights["personas"].length() > 0,
                            rx.el.div(
                                marketing_recommendations_card(),
                                rx.el.div(
                                    rx.el.h3(
                                        "Cluster Personas",
                                        class_name="text-xl font-bold text-gray-800 my-6",
                                    ),
                                    rx.el.div(
                                        rx.foreach(
                                            State.ai_insights["personas"], persona_card
                                        ),
                                        class_name="grid md:grid-cols-2 lg:grid-cols-3 gap-8",
                                    ),
                                ),
                                class_name="space-y-8",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    "Click the button above to generate insights using Google Generative AI.",
                                    class_name="text-center text-gray-600",
                                ),
                                class_name="p-8 bg-white rounded-xl shadow-md",
                            ),
                        ),
                    ),
                ),
            ),
            class_name="p-4 sm:p-6 lg:p-8",
        )
    )