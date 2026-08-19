from nicegui import ui, app
from services.user_service import login as user_login
def login_page():

    ui.dark_mode().enable()

    with ui.column().style(
        """
        background-color: #050505;
        color: white;
        min-height: 100vh;
        width: 100%;
        padding: 20px;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
        """
    ).classes(
        "w-full"
    ):

        ui.label(
            "Doth Thou Knoweth Ball"
        ).style(
            """
            color: white;
            font-size: 52px;
            font-weight: 900;
            font-family: Georgia, 'Times New Roman', serif;
            letter-spacing: 1px;
            text-align: center;
            margin-bottom: 28px;
            text-shadow: 0 0 14px rgba(37, 99, 235, 0.45);
            """
        )

        with ui.card().style(
            """
            background-color: #151515;
            color: white;
            border: 1px solid #333333;
            border-radius: 16px;
            padding: 28px;
            width: 380px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.55);
            """
        ):

            ui.label(
                "Login"
            ).classes(
                "text-h5"
            ).style(
                """
                color: white;
                font-weight: bold;
                margin-bottom: 12px;
                """
            )

            username = ui.input(
                label="Username"
            ).props(
                "outlined"
            ).style(
                """
                color: white;
                width: 100%;
                """
            )

            password = ui.input(
                label="Password",
                password=True
            ).props(
                "outlined"
            ).style(
                """
                color: white;
                width: 100%;
                """
            )

            def attempt_login():

                entered_username = (
                    username.value
                    or ""
                ).strip()

                entered_password = (
                    password.value
                    or ""
                )

                user = user_login(
                    entered_username,
                    entered_password
                )

                if not user:

                    ui.notify(
                        "Invalid username or password",
                        color="negative"
                    )

                    return

                app.storage.user[
                    "user_id"
                ] = user.id

                app.storage.user[
                    "username"
                ] = user.username

                app.storage.user[
                    "is_admin"
                ] = user.is_admin

                ui.notify(
                    f"Welcome {user.username}",
                    color="positive"
                )

                ui.navigate.to(
                    "/home"
                )

            ui.button(
                "Enter",
                on_click=attempt_login
            ).style(
                """
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                width: 100%;
                margin-top: 18px;
                border-radius: 10px;
                padding: 10px;
                """
            )
               