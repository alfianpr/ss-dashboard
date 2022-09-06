from turtle import width
import pandas as pd
import plotly.express as px
#from IPython.display import HTML
from datetime import date
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

app = dash.Dash()

#Get data
today = date.today()
df = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vRhcAWkWXIjp2XVAsnTLw13QGg6Ot9D_HBf_FMCA42qIWf034T8oKOgV6cTBJS29tfJRPHPyQ4DQJ6s/pub?gid=1978524058&single=true&output=csv")

def phase(start, finish, phase):
    df_phase = df[["Project Name", start, finish]]
    #df_phase = df_phase.loc[df['Project Name'] == project_name]
    df_phase = df_phase.dropna(subset=["Project Name"])
    df_phase["Phase"] = phase
    df_phase.rename(columns = {"Project Name":"Project", start:"Start", finish:"Finish"}, inplace=True)
    #df_phase["Start"] = df_phase["Start"].fillna(today)
    #df_phase["Finish"] = df_phase["Finish"].fillna(today)
    df_phase["Start"] = pd.to_datetime(df_phase["Start"])
    df_phase["Finish"] = pd.to_datetime(df_phase["Finish"])
    return df_phase


#Projects development phase
df_development = phase(start="Date Leads Acquired", finish="Delegation Date", phase="Development")
#Projects preparation phase
df_preparation = phase(start="Delegation Date", finish="Main Activity Start Date", phase="Preparation")
#Projects active phase
df_active = phase(start="Main Activity Start Date", finish="Main Activity End Date", phase="Active")
#Projects reporting phase
df_reporting = phase(start="Main Activity End Date", finish="Final Report Submitted Date", phase="Reporting")
#Projects closing phase
df_closing = phase(start="Final Report Submitted Date", finish="Project Archived Date", phase="Closing")
df_gantt = pd.concat(
                [df_development, df_preparation, df_active, df_reporting, df_closing], 
                ignore_index=True)

def gantt_detail(project_name):
    df_final = df_gantt.loc[df_gantt['Project'] == project_name]
    return df_final


colors = {}
colors['Development'] =  'rgb(225, 225, 51)'
colors['Preparation'] = 'rgb(76, 153, 0)'
colors['Active'] = 'rgb(204, 102, 0)'
colors['Reporting'] = 'rgb(0, 0, 204)'
colors['Closing'] = 'rgb(51, 0, 102)'

def fig_gantt():
    fig = px.timeline(df_gantt, color="Phase", color_discrete_map = colors,
                    x_start="Start", x_end="Finish", y="Project")

    fig.update_layout(shapes=[
        dict(
        type='line',
        yref='paper', y0=0, y1=1,
        xref='x', x0=today, x1=today
        )],
        autosize=True, height=900)
    return fig

#HTML(fig.to_html()) #Change to comment while using Dash
#fig.show()

#Layout
app.title = "SS Dashboard"
app.layout = html.Div(
                [
                    html.Div(
                        html.H1(id = 'H1', children = 'Prototype of SS Dashboard', style = {'textAlign':'center', 'marginTop':40,'marginBottom':40})
                    ), 
                    html.Div([html.H3(id = "H3_phase", children = "Phase of projects"), dcc.Graph(id = 'gantt', figure = fig_gantt())], id = "container_1"),
                    html.Div(
                        [html.H3(id = "H3_project_detail", children = "Project detail"),
                        html.Div([dcc.Dropdown(id='fig_dropdown',options=[{'label': x, 'value': x} for x in df_gantt["Project"]], value="ISWMP")], id = "left_container_2"),
                        html.Div(dcc.Graph(id = 'gantt_detail'), id = "right_container_2")], 
                        id = "container_2")
            ], id = "container"
        )


@app.callback(
    Output('gantt_detail', 'figure'),
    [Input('fig_dropdown', 'value')]
)

def fig_gantt_detail(value):
    fig = px.timeline(gantt_detail(project_name=value), color="Phase", color_discrete_map = colors,
                    x_start="Start", x_end="Finish", y="Project")

    fig.update_layout(shapes=[
        dict(
        type='line',
        yref='paper', y0=0, y1=1,
        xref='x', x0=today, x1=today
        )], plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)',
        autosize=True, height=200)
    return fig


if __name__ == '__main__': 
    app.run_server(debug=False)