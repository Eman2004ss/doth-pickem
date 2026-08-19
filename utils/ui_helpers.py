from nicegui import ui


def apply_dark_mode_with_home_button():

    ui.dark_mode().enable()

    ui.button(
        "Home",
        icon="home",
        on_click=lambda: ui.navigate.to("/home")
    ).style(
        """
        position: fixed;
        top: 18px;
        right: 18px;
        z-index: 9999;
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 10px;
        padding: 8px 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.45);
        """
    )


def dark_page_container():

    apply_dark_mode_with_home_button()

    return ui.column().style(
        """
        background-color: #050505;
        color: white;
        min-height: 100vh;
        width: 100%;
        padding: 16px;
        box-sizing: border-box;
        """
    )