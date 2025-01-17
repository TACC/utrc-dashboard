import dash
from dash import dcc, html

dash.register_page(__name__)

# Login screen
layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Div(
            [
                html.H3("Log In", className="c-form__title auth-form__title"),
                html.P(
                    "Please log in to view and download additional data",
                    className="c-form__desc auth-form__desc",
                ),
                html.Div(
                    [
                        html.Label("Username", htmlFor="uname-box"),
                        dcc.Input(
                            type="text", id="uname-box", className="auth-form__field"
                        ),
                    ],
                    className="c-form__field has-required",
                ),
                html.Div(
                    [
                        html.Label("Password", htmlFor="pwd-box"),
                        dcc.Input(
                            type="password", id="pwd-box", className="auth-form__field"
                        ),
                    ],
                    className="c-form__field has-required",
                ),
                html.Footer(
                    [
                        html.Button(
                            children="Login",
                            n_clicks=0,
                            type="submit",
                            id="login-button",
                            className="c-button c-form__button button--medium",
                        ),
                        html.Div(children="", id="output-state"),
                    ],
                    className="c-form__buttons",
                ),
            ],
            className="c-form c-form--login",
        ),
        html.Br(),
    ]
)
