import pandas as pd
import numpy as np
import plotly_express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import dash_table
import pathlib

# load the data
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("./data").resolve()
df = pd.read_excel(DATA_PATH.joinpath("HR RAW DATA.xlsx"))
# date time conversions
df["HIRING_MONTH"] = df["HIRING_DATE"].dt.month_name()
df["LAST_WORKING_MONTH"] = df["LAST_WORKING_DATE"].dt.month_name()
df["HIRING_YEAR"] = df["HIRING_DATE"].dt.year
df["LAST_WORKING_YEAR"] = df["LAST_WORKING_DATE"].dt.year
df["YEAR"] = df["HIRING_DATE"].dt.year
# KPIs Statistics-------------------------------------------------------
total_employee_count = df["EMPLOYEE_ID"].count()
total_female_employees = df[df["GENDER"] == "Female"].GENDER.count()
total_male_employees = df[df["GENDER"] == "Male"].GENDER.count()
percentage_female_of_total = (
    round(df[df["GENDER"] == "Female"].GENDER.count() / df["EMPLOYEE_ID"].count(), 1)
    * 100
)
Saudization_rate = (
    round(
        df[df["NATIONALITY"] == "Saudi"].NATIONALITY.count() / total_employee_count, 1
    )
    * 100
)
# calculate the tenure for each employee and , sum them up and divide by total count ---
df["tenure"] = df["LAST_WORKING_DATE"] - df["HIRING_DATE"]
average_employee_tenure_days = round(
    df["tenure"].dt.days.sum() / total_employee_count, 1
)
average_employee_annual_tenure = round(average_employee_tenure_days / 365, 1)
# KPIs--------------------------------------------------------------------
# annual Saudization Rate
# annual Saudization Rate
filtered_saudi = df[(df["NATIONALITY"] == "Saudi")]
df_saudization = (
    filtered_saudi.groupby(["YEAR"])["NATIONALITY"].size().reset_index(name="count")
)
# plot in a line chart

fig3 = px.line(
    x=df_saudization["YEAR"],
    y=df_saudization["count"],
    title="Total Employement of Saudis",
)
fig3.update_layout(
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    hovermode="x unified",
    xaxis_title="YEAR",
    yaxis_title="SAUDIS",
    title=dict(x=0.5),
)
fig3.layout.template = "plotly_dark"
fig3.update_traces(line=dict(color="cyan"), marker=dict(size=8, symbol="diamond"))
fig3.update_traces(mode="lines")

# set the layout for the application----------------------------------------------
app = dash.Dash(
    external_stylesheets=[dbc.themes.CYBORG, dbc.icons.BOOTSTRAP, "assets/style.css"],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
    suppress_callback_exceptions=True,
)
server = app.server
app.layout = dbc.Container(
    [
        dbc.Row([html.H3("HUMAN RESOURCES DASHBOARD", className="text-center mb-4")]),
        dbc.Row(
            [
                html.Marquee(
                    f"Total Employees Since 2020: {total_employee_count} --TOTAL FEMALE EMPLOYEES: {total_female_employees}--PERCENTAGE OF FEMALE EMPLOYEES : {percentage_female_of_total}%--SAUDIZATION:{Saudization_rate}%---AVERAGE ANNUAL TENURE: {average_employee_annual_tenure} YEARS"
                )
            ],
            style={"color": "cyan"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="selected_year",
                            multi=False,
                            value=2020,
                            options=[
                                {"label": x, "value": x}
                                for x in sorted(df["YEAR"].unique())
                            ],
                            clearable=False,
                            style={"color": "#000000"},
                        )
                    ],
                    width=2,
                    xs=12,
                    sm=12,
                    md=12,
                    lg=5,
                    xl=2,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [dcc.Loading(dcc.Graph(id="gender", figure={}), type="cube")],
                    width=6,
                    xs=12,
                    sm=12,
                    md=12,
                    lg=5,
                    xl=5,
                ),
                dbc.Col(
                    [
                        dcc.Loading(
                            dcc.Graph(id="employee_count", figure={}), type="cube"
                        )
                    ],
                    width=6,
                    xs=12,
                    sm=12,
                    md=12,
                    lg=5,
                    xl=5,
                ),
            ]
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Loading(
                            dcc.Graph(id="saudization", figure=fig3), type="cube"
                        )
                    ],
                    width=6,
                    xs=12,
                    sm=12,
                    md=12,
                    lg=12,
                    xl=12,
                ),
            ]
        ),
    ],
    fluid=True,
)

# define the app callback function :
@app.callback(
    [
        Output("gender", "figure"),
        Output("employee_count", "figure"),
    ],
    Input("selected_year", "value"),
)
def update_graph(year):
    filtered_df = df[df["YEAR"] == year]
    df_gender = (
        filtered_df.groupby(["GENDER", "NATIONALITY"])
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )
    colors = {"Male": "#00FFFF", "Female": "#FFFF00"}
    fig1 = go.Figure(
        data=go.Bar(
            x=df_gender["NATIONALITY"],
            y=df_gender["count"],
            marker_color=[colors[g] for g in df_gender["GENDER"]],
        )
    )
    fig1.update_layout(
        barmode="group",
        title=f"Gender Count By Nationality in {year}",
        xaxis_title="Nationality",
        yaxis_title="Gender Count",
        legend=dict(
            title="Gender",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            traceorder="normal",
        ),
    )
    fig1.update_traces(marker_line_width=0)
    fig1.layout.template = "plotly_dark"
    df_nationals = (
        filtered_df.groupby(["NATIONALITY"])
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )

    fig2 = px.bar(
        df_nationals,
        x=df_nationals["count"],
        y=df_nationals["NATIONALITY"],
        title=f"Employee count per Nationality in {year}",
    )
    fig2.update_traces(marker_color="cyan")
    fig2.layout.template = "plotly_dark"
    fig2.update_layout(
        title=dict(x=0.5),
        yaxis=dict(
            showticklabels=True,
            autorange="reversed",
        ),
    )

    return fig1, fig2


if __name__ == "__main__":
    app.run_server(debug=True, port=8000)
