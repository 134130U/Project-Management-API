import dash
from dash import dcc, html, Input, Output, State, ALL, callback, no_update, ctx
import dash_bootstrap_components as dbc
from frontend.services.projects import ProjectService
import base64
from frontend.pages.dashboard import project_detail_modal
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
                        dbc.Label("Progress (%)"),
                        dbc.Input(id="project-progress", type="number", value=0, min=0, max=100),
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
    
    dcc.Store(id="selected-project-id", data=None),
    dcc.Store(id="projects-store", data=[]),
    dcc.Download(id="download-component-projects"),
    html.Div(id="modal-container"),
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
    Output("projects-store", "data"),
    Input("submit-project", "n_clicks"),
    Input("projects-store", "data"),
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
    State("project-progress", "value"),
    State("upload-data", "contents"),
    State("upload-data", "filename"),
)
def update_projects_table(n_clicks, projects_data, session_data, name, status, description, 
                          priority, start_date, end_date, budget, spent, 
                          team, stakeholders, tags, progress, file_contents, filename):
    if not session_data or 'access_token' not in session_data:
        return "Please log in.", "", []
    
    token = session_data['access_token']
    
    # Check if we should use existing data or fetch new
    triggered_id = ctx.triggered_id
    
    if triggered_id == "submit-project":
        if not name or not start_date or not end_date or not budget:
             return no_update, "⚠️ Please fill in Name, Dates, and Budget.", no_update

        file_content = None
        content_type = None
        if file_contents:
            content_type, content_string = file_contents.split(',')
            file_content = base64.b64decode(content_string)
        
        ProjectService.create_project(
            token, name, status, description, 
            priority=priority, start_date=start_date, end_date=end_date,
            budget=budget, spent=spent, team=team, stakeholders=stakeholders, tags=tags,
            progress=progress,
            file_content=file_content, filename=filename, content_type=content_type
        )
        # Fetch new data after create
        response = ProjectService.get_projects(token)
        if response.status_code == 200:
            projects = response.json()
        else:
            return "Error loading projects.", "", []
    elif triggered_id == "projects-store":
        # Data was updated from modal
        projects = projects_data
    else:
        # Initial load or session change
        response = ProjectService.get_projects(token)
        if response.status_code == 200:
            projects = response.json()
        else:
            return "Error loading projects.", "", []

    if projects is not None:
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
                    files_info.append(html.A([
                        html.Span("📎", style={"marginRight": "4px"}),
                        html.Span(f["filename"])
                    ], id={"type": "download-link-projects", "index": f["id"]},
                       href="#",
                       style={"fontSize": "11px", "display": "block", "textDecoration": "none"}))
            
            budget_val = p.get("budget", 0)
            spent_val = p.get("spent", 0)
            progress_val = p.get("progress", 0)
            
            rows.append(html.Tr([
                html.Td(p["name"]),
                html.Td(dbc.Badge(p["status"], color="info")),
                html.Td(p.get("priority", "Medium")),
                html.Td(f"${budget_val:,}"),
                html.Td(f"${spent_val:,}"),
                html.Td(dbc.Progress(value=progress_val, label=f"{progress_val}%")),
                html.Td(files_info),
                html.Td(dbc.Button("View", id={"type": "view-btn", "index": p["id"]}, size="sm", color="info"))
            ]))

        table_body = [html.Tbody(rows)]
        return dbc.Table(table_header + table_body, bordered=True, hover=True, striped=True), "", projects
    
    return "Error loading projects.", "", []

# Attachments download handler
@callback(
    Output("download-component-projects", "data"),
    Input({"type": "download-link-projects", "index": ALL}, "n_clicks"),
    State("session-store", "data"),
    prevent_initial_call=True,
)
def download_file_projects(n_clicks, session):
    if not any(n_clicks) or not session:
        return no_update
    token = session.get("access_token")
    file_id = ctx.triggered_id["index"]
    resp = ProjectService.get_file_download_url(token, file_id)
    if resp.status_code == 200:
        url = resp.json().get("url")
        return dcc.send_string(f"Download URL: {url}", f"file_{file_id}_link.txt")
    return no_update

@callback(
    Output("selected-project-id", "data"),
    Input({"type": "view-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def select_project(n_clicks):
    if any(n_clicks):
        return ctx.triggered_id["index"]
    return None

@callback(
    Output("modal-container", "children"),
    Input("selected-project-id", "data"),
    Input("session-store", "data"),
    prevent_initial_call=True,
)
def show_modal(pid, session):
    if not pid or not session:
        return []
    token = session.get("access_token")
    resp = ProjectService.get_projects(token)
    if resp.status_code == 200:
        projects = resp.json()
        project = next((p for p in projects if p["id"] == pid), None)
        if project:
            return project_detail_modal(project)
    return []

# Detail update callbacks for interactivity
@callback(
    Output("projects-store", "data", allow_duplicate=True),
    Output("update-error", "children"),
    Input("update-project-btn", "n_clicks"),
    Input("post-update-btn", "n_clicks"),
    State("detail-project-id", "children"),
    State("detail-status", "value"),
    State("detail-progress", "value"),
    State("update-title", "value"),
    State("update-description", "value"),
    State("update-upload", "contents"),
    State("update-upload", "filename"),
    State("session-store", "data"),
    State("projects-store", "data"),
    prevent_initial_call=True,
)
def update_project_and_post_updates_projects(n_upd, n_post, pid, status, progress, u_title, u_desc, u_file, u_filename, session, projects):
    if not pid or not session:
        return no_update, ""
    
    token = session.get("access_token")
    triggered = ctx.triggered_id
    
    if triggered == "update-project-btn":
        data = {"status": status, "progress": int(progress) if progress is not None else 0}
        resp = ProjectService.update_project(token, pid, data)
        if resp.status_code != 200:
            return no_update, f"⚠️ Failed to update project: {resp.text}"
    
    if triggered == "post-update-btn":
        if not u_title:
            return no_update, "⚠️ Title is required."
        
        # Create Update
        upd_resp = ProjectService.create_update(token, pid, u_title, u_desc)
        if upd_resp.status_code == 200:
             if u_file:
                # Upload File if present
                upd_id = upd_resp.json().get("id")
                content_type, content_string = u_file.split(',')
                file_content = base64.b64decode(content_string)
                ProjectService.upload_file(token, upd_id, file_content, u_filename, content_type)
        else:
            return no_update, f"⚠️ Failed to post update: {upd_resp.text}"
            
    # Refresh projects store
    resp = ProjectService.get_projects(token)
    if resp.status_code == 200:
        new_projects = resp.json()
        error_msg = ""
        if triggered == "update-project-btn":
            error_msg = "✅ Updated!"
        elif triggered == "post-update-btn":
            error_msg = "✅ Update Posted!"
        return new_projects, error_msg
    
    return projects, ""

@callback(
    Output("updates-history", "children"),
    Input("detail-project-id", "children"),
    Input("projects-store", "data"),
    State("session-store", "data"),
)
def load_updates_projects(pid, projects, session):
    if not pid or not session:
        return "Select a project to see updates."
    
    token = session.get("access_token")
    resp = ProjectService.get_updates(token, pid)
    if resp.status_code == 200:
        updates = resp.json()
        if not updates:
            return html.Div("No updates yet.", style={"color": "#6B7394", "fontSize": "14px"})
            
        items = []
        for u in sorted(updates, key=lambda x: x['created_at'], reverse=True):
            update_files = []
            if u.get("files"):
                for f in u["files"]:
                    update_files.append(html.Div([
                        html.A([
                            html.I(className="fas fa-paperclip me-1"),
                            f.get("filename")
                        ], id={"type": "download-link", "index": f.get("id")}, 
                           href="#", className="text-decoration-none small")
                    ], className="mt-1"))

            items.append(html.Div([
                html.Div([
                    html.Strong(u.get("title", "Update"), style={"fontSize": "14px"}),
                    html.Small(u.get("created_at")[:16].replace("T", " "), 
                               style={"float": "right", "color": "#6B7394"})
                ]),
                html.P(u.get("description", ""), style={"fontSize": "13px", "margin": "5px 0"}),
                html.Div(update_files),
                html.Hr(style={"margin": "10px 0"})
            ]))
        return items
    return "Error loading updates."

@callback(
    Output("update-upload-filename", "children"),
    Input("update-upload", "filename")
)
def show_update_filename_projects(filename):
    if filename:
        return f"Selected: {filename}"
    return ""

@callback(
    Output("download-component-projects", "data", allow_duplicate=True),
    Input({"type": "download-link", "index": ALL}, "n_clicks"),
    State("session-store", "data"),
    prevent_initial_call=True,
)
def download_file_modal_projects(n_clicks, session):
    if not any(n_clicks) or not session:
        return no_update
    token = session.get("access_token")
    file_id = ctx.triggered_id["index"]
    resp = ProjectService.get_file_download_url(token, file_id)
    if resp.status_code == 200:
        url = resp.json().get("url")
        return dcc.send_string(f"Download URL: {url}", f"file_{file_id}_link.txt")
    return no_update
