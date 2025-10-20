import reflex as rx
from app.state import State
from app.components.base_layout import base_layout
from app.pages.home import progress_indicator


def stat_card(label: str, value: rx.Var, icon: str, color_class: str) -> rx.Component:
    """A card for displaying a single statistic."""
    return rx.el.div(
        rx.icon(icon, class_name=f"h-8 w-8 {color_class}"),
        rx.el.div(
            rx.el.p(label, class_name="text-sm font-medium text-gray-500"),
            rx.el.p(value.to_string(), class_name="text-2xl font-bold text-gray-800"),
            class_name="ml-4",
        ),
        class_name="flex items-center p-4 bg-white rounded-xl border border-gray-200 shadow-sm",
    )


def upload_component() -> rx.Component:
    """Component for uploading files."""
    return rx.el.div(
        rx.upload.root(
            rx.el.div(
                rx.el.div(
                    rx.icon("cloud_upload", class_name="h-12 w-12 text-gray-400"),
                    rx.el.p(
                        "Drag & Drop or Click to Upload",
                        class_name="font-semibold text-gray-700 mt-2",
                    ),
                    rx.el.p(
                        "CSV or XLSX, up to 50MB", class_name="text-sm text-gray-500"
                    ),
                    class_name="text-center",
                ),
                class_name="flex items-center justify-center w-full h-full p-8 border-2 border-dashed border-gray-300 rounded-xl hover:bg-gray-50 transition-colors",
            ),
            id="upload-data",
            on_drop=State.handle_upload(rx.upload_files(upload_id="upload-data")),
            class_name="w-full cursor-pointer",
        ),
        rx.cond(
            State.uploaded_file_name != "",
            rx.el.div(
                rx.icon("file-check-2", class_name="h-5 w-5 text-green-500 mr-2"),
                rx.el.p(
                    f"Uploaded: {State.uploaded_file_name}",
                    class_name="text-sm font-medium text-gray-700",
                ),
                class_name="mt-4 flex items-center justify-center p-2 bg-green-50 rounded-lg",
            ),
            rx.fragment(),
        ),
        class_name="w-full",
    )


def data_preview_table() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Raw Data Preview", class_name="text-xl font-bold text-gray-800 mb-4"),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.foreach(
                            State.raw_data_columns,
                            lambda col: rx.el.th(
                                col,
                                class_name="px-4 py-2 text-left text-sm font-semibold text-gray-600 bg-gray-100",
                            ),
                        )
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        State.raw_data_preview,
                        lambda row: rx.el.tr(
                            rx.foreach(
                                State.raw_data_columns,
                                lambda col: rx.el.td(
                                    row[col].to_string(),
                                    class_name="px-4 py-2 border-b border-gray-200 text-sm text-gray-700",
                                ),
                            )
                        ),
                    ),
                    class_name="bg-white",
                ),
                class_name="w-full border-collapse",
            ),
            class_name="overflow-x-auto rounded-lg border border-gray-200",
        ),
        rx.el.div(
            rx.el.button(
                "Previous",
                on_click=State.prev_preview_page,
                disabled=State.preview_page <= 1,
                class_name="px-4 py-2 text-sm font-medium bg-white border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50",
            ),
            rx.el.p(
                f"Page {State.preview_page} of {State.total_preview_pages}",
                class_name="text-sm font-medium text-gray-700",
            ),
            rx.el.button(
                "Next",
                on_click=State.next_preview_page,
                disabled=State.preview_page >= State.total_preview_pages,
                class_name="px-4 py-2 text-sm font-medium bg-white border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50",
            ),
            class_name="flex items-center justify-between mt-4",
        ),
        class_name="w-full",
    )


def data_cleaning_page() -> rx.Component:
    """The data cleaning page."""
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Data Cleaning & Preprocessing",
                    class_name="text-3xl font-bold text-gray-900",
                ),
                progress_indicator(),
            ),
            rx.el.div(
                rx.cond(
                    State.is_processing,
                    rx.el.div(
                        rx.spinner(class_name="h-12 w-12 text-sky-600"),
                        rx.el.p(
                            "Processing data, please wait...",
                            class_name="mt-4 text-lg font-medium text-gray-700",
                        ),
                        class_name="flex flex-col items-center justify-center p-16 bg-white/50 rounded-2xl shadow-lg",
                    ),
                    rx.cond(
                        State.raw_data.is_none(),
                        upload_component(),
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.h3(
                                            "Before Cleaning",
                                            class_name="text-xl font-bold text-gray-800 mb-4",
                                        ),
                                        rx.el.div(
                                            stat_card(
                                                "Rows",
                                                State.original_stats.rows,
                                                "align-horizontal-distribute-start",
                                                "text-red-500",
                                            ),
                                            stat_card(
                                                "Columns",
                                                State.original_stats.cols,
                                                "align-horizontal-distribute-end",
                                                "text-red-500",
                                            ),
                                            stat_card(
                                                "Missing Values",
                                                State.original_stats.missing_values,
                                                "search-x",
                                                "text-red-500",
                                            ),
                                            class_name="grid grid-cols-1 md:grid-cols-3 gap-4",
                                        ),
                                    ),
                                    rx.el.div(
                                        rx.el.h3(
                                            "After Cleaning",
                                            class_name="text-xl font-bold text-gray-800 mb-4",
                                        ),
                                        rx.el.div(
                                            stat_card(
                                                "Rows",
                                                State.cleaned_stats.rows,
                                                "align-horizontal-distribute-start",
                                                "text-green-500",
                                            ),
                                            stat_card(
                                                "Columns",
                                                State.cleaned_stats.cols,
                                                "align-horizontal-distribute-end",
                                                "text-green-500",
                                            ),
                                            stat_card(
                                                "Outliers Removed",
                                                State.cleaned_stats.outliers,
                                                "trash-2",
                                                "text-green-500",
                                            ),
                                            class_name="grid grid-cols-1 md:grid-cols-3 gap-4",
                                        ),
                                    ),
                                    class_name="space-y-8",
                                ),
                                data_preview_table(),
                                rx.el.div(
                                    rx.el.h3(
                                        "Correlation Heatmap (Cleaned Data)",
                                        class_name="text-xl font-bold text-gray-800 mb-4",
                                    ),
                                    rx.plotly(
                                        data=State.correlation_heatmap,
                                        class_name="w-full h-[600px]",
                                    ),
                                    class_name="bg-white p-6 rounded-2xl border border-gray-200 shadow-lg",
                                ),
                                class_name="space-y-8",
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Proceed to PCA Analysis",
                                    rx.icon("arrow_right"),
                                    on_click=State.proceed_to_pca,
                                    disabled=State.cleaned_data.is_none(),
                                    class_name="px-6 py-3 bg-sky-600 text-white font-semibold rounded-xl shadow-md hover:bg-sky-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2",
                                ),
                                class_name="flex justify-end mt-8",
                            ),
                            class_name="w-full",
                        ),
                    ),
                ),
                class_name="mt-8 p-8 bg-white/30 backdrop-blur-sm rounded-2xl shadow-md border border-gray-200/50",
            ),
            class_name="p-4 sm:p-6 lg:p-8",
        )
    )