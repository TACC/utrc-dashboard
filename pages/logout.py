import dash
from dash import Input, Output, callback, dcc, html, no_update
from flask_login import current_user, logout_user

dash.register_page(__name__)


layout = html.Div(
    [
        html.H3("Log Out", className="c-form__title auth-form__title"),
        html.P(
            "Click the button to log out",
            className="c-form__desc auth-form__desc",
        ),
        html.Footer(
            [
                dcc.Link(
                    html.Button(
                        children="Log out",
                        n_clicks=0,
                        type="submit",
                        id="logout-button",
                    ),
                    id="logout-link",
                    href="/login",
                    className="c-button c-form__button button--medium",
                )
            ],
            className="c-form__buttons auth-form__footer",
        ),
    ],
    className="c-form c-form--login",
)


@callback(
    Output("logout-link", "href"),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True,
)
def search(n_clicks):
    if current_user.is_authenticated:
        logout_user()
        return "/login"
    else:
        return no_update
