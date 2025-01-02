import dash
from dash import html, dcc, callback, Output, Input, no_update
from flask_login import logout_user, current_user

dash.register_page(__name__)


layout = html.Div(
    [
        html.H3("Log Out", className="c-form__title form-title"),
        html.P(
            "Click the button to log out",
            className="c-form__desc form-desc",
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
                    className="c-button c-form__button medium-button",
                )
            ],
            className="c-form__buttons logout-footer",
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
