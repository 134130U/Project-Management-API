import dash
from dash import html, dcc, Output, Input, State, callback, no_update
import dash_bootstrap_components as dbc
from frontend.services.projects import ProjectService
import base64

dash.register_page(__name__, path='/projects')

layout = html.Div([
    html.H1("Projects List"),
    dbc.Button("Create New Project", id="open-create-modal", color="success", className="mb-3"),
    
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Create New Project")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Project Name *"),
                        dbc.Input(id="project-name", type="text", placeholder="Enter project name"),
                    ], md=12, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Description"),
                        dbc.Textarea(id="project-description", placeholder="Enter project description"),
                    ], md=12, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Status"),
                        dbc.Select(
                            id="project-status",
                            options=[
                                {"label": s, "value": s} for s in
                                ["Planning", "In Progress", "At Risk", "On Hold", "Completed"]
                            ],
                            value="Planning"
                        ),
                    ], md=6, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Priority"),
                        dbc.Select(
                            id="project-priority",
                            options=[
                                {"label": p, "value": p} for p in
                                ["Critical", "High", "Medium", "Low"]
                            ],
                            value="Medium"
                        ),
                    ], md=6, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Start Date *"),
                        dbc.Input(id="project-start-date", type="date"),
                    ], md=6, className="mb-3"),
                    dbc.Col([
                        dbc.Label("End Date *"),
                        dbc.Input(id="project-end-date", type="date"),
                    ], md=6, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Total Budget ($) *"),
                        dbc.Input(id="project-budget", type="number", placeholder="e.g. 100000"),
                    ], md=6, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Amount Spent ($)"),
                        dbc.Input(id="project-spent", type="number", value=0),
                    ], md=6, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Team Members"),
                        dbc.Input(id="project-team", placeholder="Alice M., Bob K."),
                    ], md=12, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Stakeholders"),
                        dbc.Input(id="project-stakeholders", placeholder="CEO, CTO"),
                    ], md=12, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Tags"),
                        dbc.Input(id="project-tags", placeholder="Backend, Design"),
                    ], md=12, className="mb-3"),
                    dbc.Col([
                        dbc.Label("File Attachment"),
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                'Drag and Drop or ',
                                html.A('Select Files')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center'
                            },
                            multiple=False
                        ),
                        html.Div(id='output-file-name'),
                    ], md=12, className="mb-3"),
                ])
            ])
        ]),
        dbc.ModalFooter([
            html.Div(id="project-create-error", style={"color": "red", "marginRight": "auto"}),
            dbc.Button("Create", id="submit-project", color="primary", n_clicks=0)
        ]),
    ], id="create-project-modal", is_open=False, size="lg"),

    html.Div(id="projects-table-container")
])

@callback(
    Output("create-project-modal", "is_open"),
    [Input("open-create-modal", "n_clicks"), Input("submit-project", "n_clicks")],
    [State("create-project-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@callback(
    Output('output-file-name', 'children'),
    Input('upload-data', 'filename'),
)
def update_filename(filename):
    if filename:
        return html.Small(f"Selected: {filename}")
    return ""

@callback(
    Output("projects-table-container", "children"),
    Output("project-create-error", "children"),
    Input("submit-project", "n_clicks"),
    Input("session-store", "data"),
    State("project-name", "value"),
    State("project-status", "value"),
    State("project-description", "value"),
    State("project-priority", "value"),
    State("project-start-date", "value"),
    State("project-end-date", "value"),
    State("project-budget", "value"),
    State("project-spent", "value"),
    State("project-team", "value"),
    State("project-stakeholders", "value"),
    State("project-tags", "value"),
    State("upload-data", "contents"),
    State("upload-data", "filename"),
)
def update_projects_table(n_clicks, session_data, name, status, description, 
                          priority, start_date, end_date, budget, spent, 
                          team, stakeholders, tags, file_contents, filename):
    if not session_data or 'token' not in session_data:
        return "Please log in.", ""
    
    token = session_data['token']
    error_msg = ""

    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[0] == 'submit-project':
        if not name or not start_date or not end_date or not budget:
             return no_update, "⚠️ Please fill in Name, Dates, and Budget."

        file_content = None
        content_type = None
        if file_contents:
            content_type, content_string = file_contents.split(',')
            file_content = base64.b64decode(content_string)
        
        ProjectService.create_project(
            token, name, status, description, 
            priority=priority, start_date=start_date, end_date=end_date,
            budget=budget, spent=spent, team=team, stakeholders=stakeholders, tags=tags,
            file_content=file_content, filename=filename, content_type=content_type
        )

    response = ProjectService.get_projects(token)
    if response.status_code == 200:
        projects = response.json()
        
        table_header = [
            html.Thead(html.Tr([
                html.Th("Project Name"),
                html.Th("Status"),
                html.Th("Priority"),
                html.Th("Budget"),
                html.Th("Spent"),
                html.Th("Progress"),
                html.Th("Attachments"),
                html.Th("Actions")
            ]))
        ]

        rows = []
        for p in projects:
            files_info = []
            if 'files' in p and p['files']:
                for f in p['files']:
                    files_info.append(html.Div(f["filename"]))
            
            budget_val = p.get("budget", 0)
            spent_val = p.get("spent", 0)
            progress = round(spent_val / budget_val * 100, 1) if budget_val else 0
            
            rows.append(html.Tr([
                html.Td(p["name"]),
                html.Td(dbc.Badge(p["status"], color="info")),
                html.Td(p.get("priority", "Medium")),
                html.Td(f"${budget_val:,}"),
                html.Td(f"${spent_val:,}"),
                html.Td(dbc.Progress(value=progress, label=f"{progress}%")),
                html.Td(files_info),
                html.Td(dbc.Button("View", size="sm", color="info"))
            ]))

        table_body = [html.Tbody(rows)]
        return dbc.Table(table_header + table_body, bordered=True, hover=True, striped=True), ""
    
    return "Error loading projects.", ""
