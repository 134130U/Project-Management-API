import dash
from dash import dcc, html, dash_table, Input, Output, State, ctx, MATCH, ALL, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import json
import copy

dash.register_page(__name__, path='/')

# ─────────────────────────────────────────
# THEME
# ─────────────────────────────────────────
COLORS = {
    "bg":       "#0D0F14",
    "surface":  "#161920",
    "card":     "#1C2030",
    "border":   "#252B3B",
    "accent":   "#4F8EF7",
    "success":  "#2DD4A0",
    "warning":  "#F7B955",
    "danger":   "#F75F5F",
    "purple":   "#9B7CF7",
    "text":     "#E8EAEF",
    "muted":    "#6B7394",
}

STATUS_COLORS = {
    "In Progress": COLORS["accent"],
    "Planning":    COLORS["purple"],
    "Completed":   COLORS["success"],
    "At Risk":     COLORS["danger"],
    "On Hold":     COLORS["warning"],
}

PRIORITY_COLORS = {
    "Critical": COLORS["danger"],
    "High":     COLORS["warning"],
    "Medium":   COLORS["accent"],
    "Low":      COLORS["muted"],
}

# ─────────────────────────────────────────
# STYLE HELPERS  (defined early so layout can use them)
# ─────────────────────────────────────────
def form_label_style():
    return {"fontSize": "12px",
            "fontWeight": "600", "marginBottom": "5px", "display": "block"}


def form_input_style():
    return {"fontSize": "14px", "width": "100%"}

# ─────────────────────────────────────────
# INITIAL DATA
# ─────────────────────────────────────────
# INITIAL_PROJECTS = []  # No longer used, dashboard uses backend data

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def days_left(end_date_str):
    if not end_date_str:
        return 0
    try:
        end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        return (end - date.today()).days
    except (ValueError, TypeError):
        return 0


def budget_pct(project):
    budget = project.get("budget", 0)
    spent = project.get("spent", 0)
    return round(spent / budget * 100, 1) if budget else 0


def progress_bar(value, color=None):
    pct = min(100, max(0, value))
    return html.Div([
        html.Div(style={
            "width": f"{pct}%", "height": "100%",
            "background": color or "#4F8EF7", "borderRadius": "99px",
            "transition": "width 0.4s ease",
        })
    ], style={
        "background": "#F0F2F5", "borderRadius": "99px",
        "height": "8px", "overflow": "hidden",
    })


def badge(label, color):
    return html.Span(label, style={
        "background": color + "22", "color": color,
        "border": f"1px solid {color}44",
        "borderRadius": "6px", "padding": "2px 10px",
        "fontSize": "12px", "fontWeight": "600",
        "letterSpacing": "0.03em", "whiteSpace": "nowrap",
    })


def avatar_initials(name, size=28):
    initials = "".join(p[0].upper() for p in name.split()[:2])
    hue = sum(ord(c) for c in name) % 360
    return html.Div(initials, style={
        "width": f"{size}px", "height": f"{size}px",
        "borderRadius": "50%",
        "background": f"hsl({hue}, 55%, 38%)",
        "color": "#fff", "fontSize": f"{int(size*0.38)}px",
        "display": "flex", "alignItems": "center",
        "justifyContent": "center", "fontWeight": "700",
        "flexShrink": "0", "border": "2px solid #fff",
    })


def stat_card(label, value, sub, color, icon):
    return dbc.Col(html.Div([
        html.Div([
            html.Div([
                html.Div(label, style={"color": "#6B7394", "fontSize": "12px",
                                       "marginBottom": "6px", "fontWeight": "500"}),
                html.Div(value, style={"color": color, "fontSize": "28px",
                                       "fontWeight": "800", "lineHeight": "1"}),
                html.Div(sub, style={"color": "#6B7394", "fontSize": "12px",
                                     "marginTop": "6px"}),
            ]),
            html.Div(icon, style={"fontSize": "28px", "opacity": "0.6"}),
        ], style={"display": "flex", "justifyContent": "space-between",
                  "alignItems": "flex-start"}),
    ], style={
        "background": "#fff",
        "border": "1px solid #E8EAEF",
        "borderRadius": "14px", "padding": "18px 22px",
    }), md=3)


def project_card(project):
    end_date = project.get("end_date")
    if end_date:
        dl = days_left(end_date)
        #dl_color = COLORS["danger"] if dl < 0 else COLORS["warning"] if dl < 14 else COLORS["muted"]
        dl_text = (f"{abs(dl)}d overdue" if dl < 0 else
                   "Due today" if dl == 0 else f"{dl}d left")
    else:
        dl_text = "No due date"
        #dl_color = COLORS["muted"]

    budget = project.get("budget", 0)
    spent = project.get("spent", 0)
    bpct = budget_pct(project)
    #        COLORS["warning"] if bpct > 70 else COLORS["success"])

    deliverables = project.get("deliverables", [])
    done_deliverables = sum(1 for d in deliverables if d.get("done"))

    status = project.get("status", "Planning")
    priority = project.get("priority", "Medium")
    
    # Files integration
    files = project.get("files", [])
    file_badges = [html.Div([
        html.Span("📎", style={"marginRight": "4px"}),
        html.Span(f["filename"], style={"fontSize": "11px"})
    ], style={"display": "flex", "alignItems": "center", "color": "#6B7394",
              "marginTop": "4px"}) for f in files]

    return dbc.Col(
        html.Div([
            # Top row
            html.Div([
                html.Div([
                    html.Div(project.get("name", "Unnamed Project"), style={
                        "fontWeight": "700", "fontSize": "16px",
                        "color": "#1C2030",
                        "marginBottom": "4px",
                    }),
                    html.Div(project.get("description", ""), style={
                        "fontSize": "12px", "color": "#6B7394",
                        "lineHeight": "1.4",
                        "overflow": "hidden",
                        "display": "-webkit-box",
                        "-webkit-line-clamp": "2",
                        "-webkit-box-orient": "vertical",
                    }),
                ], style={"flex": "1", "marginRight": "10px"}),
                html.Div([
                    badge(status, STATUS_COLORS.get(status, None)),
                    html.Br(),
                    html.Span(style={"height": "4px", "display": "block"}),
                    badge(priority, PRIORITY_COLORS.get(priority, COLORS["muted"])),
                ], style={"flexShrink": "0", "textAlign": "right"}),
            ], style={"display": "flex", "marginBottom": "10px"}),

            # Attachments
            html.Div(file_badges, style={"marginBottom": "10px"}) if file_badges else None,

            # Tags
            html.Div([
                html.Span(t, style={
                    "background": "#F0F2F5", "color": "#6B7394",
                    "borderRadius": "6px", "padding": "2px 8px",
                    "fontSize": "11px", "marginRight": "4px",
                }) for t in project.get("tags", [])
            ], style={"marginBottom": "14px"}),

            # Progress
            html.Div([
                html.Div([
                    html.Span("Progress", style={"color": "#6B7394",
                                                 "fontSize": "12px"}),
                    html.Span(f"{project.get('progress', 0)}%", style={
                        "color": "#1C2030",
                        "fontSize": "12px", "fontWeight": "700"
                    }),
                ], style={"display": "flex", "justifyContent": "space-between",
                          "marginBottom": "4px"}),
                progress_bar(project.get("progress", 0)),
            ], style={"marginBottom": "10px"}),

            # Budget
            html.Div([
                html.Div([
                    html.Span("Budget", style={"color": "#6B7394",
                                               "fontSize": "12px"}),
                    html.Span(f"${spent:,} / ${budget:,}",
                              style={"color": "#1C2030",
                                     "fontSize": "12px", "fontWeight": "600"}),
                ], style={"display": "flex", "justifyContent": "space-between",
                          "marginBottom": "4px"}),
                progress_bar(bpct),
            ], style={"marginBottom": "10px"}),

            # Deliverables quick stat
            html.Div([
                html.Span(f"📦 {done_deliverables}/{len(deliverables)} deliverables",
                          style={"fontSize": "12px", "color": "#6B7394"
                                 }),
            ], style={"marginBottom": "12px"}),

            # Footer
            html.Div([
                html.Div([
                    *[html.Div(avatar_initials(m), style={"marginLeft": f"{-8 if i>0 else 0}px"})
                      for i, m in enumerate(project.get("team", [])[:4])],
                    *([] if len(project.get("team", [])) <= 4 else [
                        html.Div(f"+{len(project.get('team', []))-4}", style={
                            "marginLeft": "-8px", "width": "26px", "height": "26px",
                            "borderRadius": "50%", "background": "#F0F2F5",
                            "color": "#6B7394",
                            "fontSize": "10px",
                            "display": "flex", "alignItems": "center",
                            "justifyContent": "center", "border": "2px solid #fff",
                            "fontWeight": "700",
                        })
                    ]),
                ], style={"display": "flex", "alignItems": "center"}),
                html.Span(dl_text, style={
                    "fontSize": "12px", "fontWeight": "600"
                }),
            ], style={"display": "flex", "justifyContent": "space-between",
                      "alignItems": "center"}),

            # Hidden project id for callback
            html.Div(project["id"], id={"type": "card-id", "index": project["id"]},
                     style={"display": "none"}),
        ], id={"type": "project-card", "index": project["id"]},
           n_clicks=0,
           style={
               "background": "#fff",
               "border": "1px solid #E8EAEF",
               "borderRadius": "14px", "padding": "20px 22px",
               "cursor": "pointer",
               "boxShadow": "0 2px 12px #00000008",
               "transition": "border-color 0.2s, transform 0.15s",
               "height": "100%",
           }),
        md=4, style={"marginBottom": "16px"},
    )


def project_detail_modal(project):
    end_date = project.get("end_date")
    dl = days_left(end_date)
    # dl_color = COLORS["danger"] if dl < 0 else COLORS["warning"] if dl < 14 else COLORS["success"]
    dl_text = f"{abs(dl)}d overdue" if dl < 0 else f"{dl}d remaining" if end_date else "No due date"
    
    budget = project.get("budget", 0)
    spent = project.get("spent", 0)
    bpct = budget_pct(project)
    # b_color = COLORS["danger"] if bpct > 90 else COLORS["warning"] if bpct > 70 else COLORS["success"]
    
    deliverables = project.get("deliverables", [])
    done_count = sum(1 for d in deliverables if d.get("done"))

    deliverable_items = []
    for d in deliverables:
        deliverable_items.append(
            html.Div([
                dbc.Checkbox(
                    id={"type": "deliverable-check", "index": d.get("id", 0)},
                    value=d.get("done", False),
                    label=d.get("title", "Untitled"),
                    # style={"color": COLORS["muted"] if d.get("done") else COLORS["text"]},
                ),
            ], style={
                "padding": "8px 0",
                # "borderBottom": f"1px solid {COLORS['border']}",
                # "color": COLORS["muted"] if d.get("done") else COLORS["text"],
                "textDecoration": "line-through" if d.get("done") else "none",
            })
        )

    return dbc.Modal([
        dbc.ModalHeader([
            html.Div([
                html.H4(project.get("name", "Unnamed Project"), style={
                    "color": "#1C2030",
                    "fontWeight": "800", "margin": "0 0 8px 0"
                }),
                html.Div([
                    badge(project.get("status", "Planning"), #STATUS_COLORS.get(project.get("status", "Planning"), COLORS["muted"])
                          ),
                    html.Span(" ", style={"marginRight": "6px"}),
                    badge(project.get("priority", "Medium"), #PRIORITY_COLORS.get(project.get("priority", "Medium"), COLORS["muted"])
                          ),
                ]),
            ])
        ]),

        dbc.ModalBody([
            html.P(project.get("description", ""), style={
                "color": "#6B7394",
                "fontSize": "14px",
                "lineHeight": "1.6", "marginBottom": "20px",
            }),

            # Date / deadline row
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("Start Date", style={"color": "#6B7394",
                                                  "fontSize": "12px",
                                                   "marginBottom": "4px"}),
                    html.Div(project.get("start_date", "N/A"), style={"fontWeight": "700", "color": "#1C2030"
                                                                      }),
                ], style={"background": "#F8F9FA",
                          "borderRadius": "10px",
                          "padding": "12px 14px", "border": "1px solid #E8EAEF"
                })),
                dbc.Col(html.Div([
                    html.Div("End Date", style={"color": "#6B7394",
                                                "fontSize": "12px","marginBottom": "4px"}),
                    html.Div(project.get("end_date", "N/A"), style={"fontWeight": "700", "color": "#1C2030"
                                                                    }),
                ], style={"background": "#F8F9FA",
                          "borderRadius": "10px",
                          "padding": "12px 14px", "border": "1px solid #E8EAEF"
                })),
                dbc.Col(html.Div([
                    html.Div("Deadline", style={"color": "#6B7394",
                                                "fontSize": "12px","marginBottom": "4px"}),
                    html.Div(dl_text, style={"fontWeight": "700", "color": "#1C2030"
                                             }),
                ], style={"background": "#F8F9FA",
                          "borderRadius": "10px",
                          "padding": "12px 14px", "border": "1px solid #E8EAEF"
                })),
            ], style={"marginBottom": "16px"}),

            # Budget
            html.Div([
                html.H6("💰 Budget", style={"color": "#1C2030",
                                           "fontWeight": "700","marginBottom": "12px"}),
                html.Div([
                    html.Span("Budget Used", style={"color": "#6B7394",
                                                    "fontSize": "12px"}),
                    html.Span(f"{bpct}%", style={"color": "#1C2030",
                                                 "fontSize": "12px",
                                                  "fontWeight": "700"}),
                ], style={"display": "flex", "justifyContent": "space-between",
                          "marginBottom": "4px"}),
                progress_bar(bpct),
                html.Div([
                    html.Span(f"Spent: ${spent:,}",
                              style={"color": "#6B7394",
                                     "fontSize": "11px"}),
                    html.Span(f"Total: ${budget:,}",
                              style={"color": "#6B7394",
                                     "fontSize": "11px"}),
                ], style={"display": "flex", "justifyContent": "space-between",
                          "marginTop": "4px"}),
            ], style={"background": "#F8F9FA",
                      "borderRadius": "12px",
                      "padding": "16px 18px", "border": "1px solid #E8EAEF",
                      "marginBottom": "16px"}),

            # Progress
            html.Div([
                html.H6("📈 Progress", style={"color": "#1C2030", "fontWeight": "700",
                                               "marginBottom": "12px"}),
                html.Div([
                    html.Span("Overall completion",
                              style={"color": "#6B7394",
                                     "fontSize": "13px"}),
                    html.Span(f"{project.get('progress', 0)}%",
                              style={"color": "#1C2030",
                                     "fontWeight": "700"}),
                ], style={"display": "flex", "justifyContent": "space-between",
                          "marginBottom": "6px"}),
                progress_bar(project.get("progress", 0)),
            ], style={"background": "#F8F9FA",
                      "borderRadius": "12px",
                      "padding": "16px 18px", "border": "1px solid #E8EAEF",
                      "marginBottom": "16px"}),

            # Deliverables
            html.Div([
                html.H6("📦 Deliverables", style={"color": "#1C2030",
                                                 "fontWeight": "700","marginBottom": "12px"}),
                *deliverable_items,
                html.Div(f"{done_count} / {len(project['deliverables'])} completed",
                         style={"color": "#6B7394",
                                "fontSize": "12px","marginTop": "8px"}),
            ], style={"background": "#F8F9FA",
                      "borderRadius": "12px",
                      "padding": "16px 18px", "border": "1px solid #E8EAEF",
                      "marginBottom": "16px"}),

            # Team
            html.Div([
                html.H6(f"👥 Team ({len(project['team'])})",
                        style={"color": "#1C2030",
                               "fontWeight": "700",
                               "marginBottom": "12px"}),
                html.Div([
                    html.Div([
                        avatar_initials(m, 26),
                        html.Span(m, style={"color": "#1C2030",
                                            "fontSize": "13px"}),
                    ], style={
                        "display": "flex", "alignItems": "center", "gap": "8px",
                        "background": "#F8F9FA", "border": "1px solid #E8EAEF",
                        "borderRadius": "20px", "padding": "4px 12px 4px 4px",
                        "marginRight": "8px", "marginBottom": "8px",
                        "display": "inline-flex",
                    })
                    for m in project["team"]
                ], style={"display": "flex", "flexWrap": "wrap"}),
            ], style={"background": "#F8F9FA",
                      "borderRadius": "12px",
                      "padding": "16px 18px", "border": "1px solid #E8EAEF",
                      "marginBottom": "16px"}),

            # Stakeholders
            html.Div([
                html.H6("🏢 Stakeholders", style={"color": "#1C2030",
                                                 "fontWeight": "700",
                                                   "marginBottom": "12px"}),
                html.Div([
                    html.Span(s, style={
                        "background": "#F0F2F5", "color": "#4F8EF7",
                        "border": "1px solid #4F8EF744",
                        "borderRadius": "8px", "padding": "4px 12px",
                        "fontSize": "13px", "marginRight": "8px", "marginBottom": "8px",
                        "display": "inline-block",
                    }) for s in project["stakeholders"]
                ]),
            ], style={"background": "#F8F9FA",
                      "borderRadius": "12px",
                      "padding": "16px 18px", "border": "1px solid #E8EAEF"
            }),
        ]),

        dbc.ModalFooter(
            dbc.Button("Close", id="close-modal", color="secondary"),
            # style={"background": COLORS["surface"],
            #        "borderTop": f"1px solid {COLORS['border']}"}
        ),
    ], id="project-modal", is_open=True, size="lg",
       style={"fontFamily": "'DM Sans', sans-serif"})


def budget_chart(projects):
    names = [p["name"] for p in projects]
    budgets = [p["budget"] for p in projects]
    spent = [p["spent"] for p in projects]

    fig = go.Figure()
    fig.add_bar(name="Budget", x=names, y=budgets,
                # marker_color=COLORS["border"],
                marker_line_width=0)
    fig.add_bar(name="Spent", x=names, y=spent,
                # marker_color=[
                #     COLORS["danger"] if budget_pct(p) > 90
                #     else COLORS["warning"] if budget_pct(p) > 70
                #     else COLORS["success"]
                #     for p in projects
                # ],
                marker_line_width=0)
    fig.update_layout(
        barmode="overlay",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        # font_color=COLORS["text"],
        font_family="DM Sans",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=10, b=10, l=0, r=0),
        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, #gridcolor=COLORS["border"],
                   tickformat="$,.0f"),
        height=240,
    )
    return fig


def status_donut(projects):
    status_counts = {}
    for p in projects:
        status_counts[p["status"]] = status_counts.get(p["status"], 0) + 1

    fig = go.Figure(go.Pie(
        labels=list(status_counts.keys()),
        values=list(status_counts.values()),
        hole=0.6,
        # marker_colors=[STATUS_COLORS.get(s, COLORS["muted"])
        #                for s in status_counts.keys()],
        # textfont_color=COLORS["text"],
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        # font_color=COLORS["text"],
        font_family="DM Sans",
        showlegend=True,
        legend=dict(orientation="h", y=-0.1, font=dict(size=11)),
        margin=dict(t=10, b=10, l=10, r=10),
        height=240,
    )
    return fig


# ─────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap",
]
#
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
#                 suppress_callback_exceptions=True)

layout = html.Div([
    # Store
    dcc.Store(id="projects-store", data=[]),
    dcc.Store(id="selected-project-id", data=None),

    # ── HEADER ──
    html.Div([
        html.Div([
            html.Div([
                html.Div("⚡", style={
                    "width": "32px", "height": "32px", "borderRadius": "9px",
                    "background": "linear-gradient(135deg, #4F8EF7, #9B7CF7)",
                    "display": "flex", "alignItems": "center",
                    "justifyContent": "center", "fontSize": "18px",
                }),
                html.Span("ProjectOS", style={
                    "fontWeight": "800", "fontSize": "20px",
                    "letterSpacing": "-0.02em", "color": "#1C2030",
                }),
            ], style={"display": "flex", "alignItems": "center", "gap": "12px"}),

            html.Div([
                dbc.Input(id="search-input", placeholder="Search projects, team, tags…",
                          type="text", debounce=True,
                          style={
                              # "background": COLORS["card"],
                              # "border": f"1px solid {COLORS['border']}",
                              # "color": COLORS["text"], "borderRadius": "9px",
                              "fontSize": "14px", "width": "260px",
                          }),
                dbc.Button("+ New Project", id="open-new-modal", color="primary",
                           style={
                               "background": "linear-gradient(135deg, #4F8EF7, #9B7CF7)",
                               "border": "none", "borderRadius": "9px",
                               "fontWeight": "600", "fontSize": "14px",
                           }),
            ], style={"display": "flex", "alignItems": "center", "gap": "12px"}),
        ], style={
            "maxWidth": "1200px", "margin": "0 auto",
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "center", "padding": "0 32px", "height": "62px",
        }),
    ], style={
        # "borderBottom": f"1px solid {COLORS['border']}",
        # "background": COLORS["bg"] + "f8",
        "position": "sticky", "top": "0", "zIndex": "100",
        "backdropFilter": "blur(12px)",
    }),

    # ── MAIN ──
    html.Div([

        # ── STAT CARDS ──
        dbc.Row(id="stat-cards", style={"marginBottom": "24px"}),

        # ── CHARTS ──
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Budget Overview", style={
                    "color": "#1C2030",
                    "fontWeight": "700",
                    "fontSize": "14px", "marginBottom": "12px",
                }),
                dcc.Graph(id="budget-chart", config={"displayModeBar": False}),
            ], style={"background": "#fff",
                      "borderRadius": "14px",
                      "padding": "16px 18px",
                      "border": "1px solid #E8EAEF"
            }), md=8),

            dbc.Col(html.Div([
                html.Div("Status Distribution", style={
                    "color": "#1C2030",
                    "fontWeight": "700",
                    "fontSize": "14px", "marginBottom": "12px",
                }),
                dcc.Graph(id="status-donut", config={"displayModeBar": False}),
            ], style={"background": "#fff",
                      "borderRadius": "14px",
                      "padding": "16px 18px",
                      "border": "1px solid #E8EAEF"
            }), md=4),
        ], style={"marginBottom": "24px"}),

        # ── FILTERS ──
        html.Div([
            html.Div(id="filter-buttons",
                     style={"display": "flex", "gap": "8px", "flexWrap": "wrap"}),
        ], style={"marginBottom": "20px"}),

        # ── PROJECT GRID ──
        dbc.Row(id="project-grid"),

        # ── MODAL CONTAINER ──
        html.Div(id="modal-container"),

        # ── NEW PROJECT MODAL ──
        dbc.Modal([
            dbc.ModalHeader(html.H5("New Project", style={
                "color": "#1C2030",
                "fontWeight": "800"
            })),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Project Name *", style=form_label_style()),
                        dbc.Input(id="new-name", placeholder="Enter project name",
                                  style=form_input_style()),
                    ], md=12, style={"marginBottom": "12px"}),
                    dbc.Col([
                        html.Label("Description", style=form_label_style()),
                        dbc.Textarea(id="new-description", placeholder="Project description",
                                     style={**form_input_style(), "minHeight": "70px"}),
                    ], md=12, style={"marginBottom": "12px"}),
                    dbc.Col([
                        html.Label("Status", style=form_label_style()),
                        dbc.Select(id="new-status", options=[
                            {"label": s, "value": s} for s in
                            ["Planning", "In Progress", "At Risk", "On Hold", "Completed"]
                        ], value="Planning", style=form_input_style()),
                    ], md=6, style={"marginBottom": "12px"}),
                    dbc.Col([
                        html.Label("Priority", style=form_label_style()),
                        dbc.Select(id="new-priority", options=[
                            {"label": p, "value": p} for p in
                            ["Critical", "High", "Medium", "Low"]
                        ], value="Medium", style=form_input_style()),
                    ], md=6, style={"marginBottom": "12px"}),
                    dbc.Col([
                        html.Label("Start Date *", style=form_label_style()),
                        dbc.Input(id="new-start-date", type="date",
                                  style=form_input_style()),
                    ], md=6, style={"marginBottom": "12px"}),
                    dbc.Col([
                        html.Label("End Date *", style=form_label_style()),
                        dbc.Input(id="new-end-date", type="date",
                                  style=form_input_style()),
                    ], md=6, style={"marginBottom": "12px"}),
                    dbc.Col([
                        html.Label("Total Budget ($) *", style=form_label_style()),
                        dbc.Input(id="new-budget", type="number", placeholder="e.g. 100000",
                                  style=form_input_style()),
                    ], md=6, style={"marginBottom": "12px"}),
                    dbc.Col([
                        html.Label("Amount Spent ($)", style=form_label_style()),
                        dbc.Input(id="new-spent", type="number", value=0,
                                  style=form_input_style()),
                    ], md=6, style={"marginBottom": "12px"}),
                    dbc.Col([
                        html.Label("Team Members (comma-separated)", style=form_label_style()),
                        dbc.Input(id="new-team", placeholder="Alice M., Bob K., Carol N.",
                                  style=form_input_style()),
                    ], md=12, style={"marginBottom": "12px"}),
                    dbc.Col([
                        html.Label("Stakeholders (comma-separated)", style=form_label_style()),
                        dbc.Input(id="new-stakeholders", placeholder="CEO, CTO, Product",
                                  style=form_input_style()),
                    ], md=12, style={"marginBottom": "12px"}),
                    dbc.Col([
                        html.Label("Tags (comma-separated)", style=form_label_style()),
                        dbc.Input(id="new-tags", placeholder="Backend, AI/ML, Design",
                                  style=form_input_style()),
                    ], md=12, style={"marginBottom": "12px"}),
                    dbc.Col([
                        html.Label("File Attachment", style=form_label_style()),
                        dcc.Upload(
                            id='new-upload-data',
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
                                'textAlign': 'center',
                                # 'color': COLORS["muted"]
                            },
                            multiple=False
                        ),
                        html.Div(id='new-output-file-name', style={"color": "#1C2030",
                                                                   "fontSize": "12px", "marginTop": "5px"}),
                    ], md=12, style={"marginBottom": "12px"}),
                ]),
                html.Div(id="new-project-error", style={"color": "#F75F5F",
                                                          "fontSize": "13px"}),
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-new-modal",
                           # style={"background": COLORS["card"],
                           #        "border": f"1px solid {COLORS['border']}",
                           #        "color": COLORS["text"]}
                           ),
                dbc.Button("Create Project", id="create-project-btn", color="primary",
                           style={"background": "linear-gradient(135deg, #4F8EF7, #9B7CF7)",
                                  "border": "none", "fontWeight": "600"}),
            ], style={#"background": COLORS["surface"],
                      # "borderTop": f"1px solid {COLORS['border']}"
            }),
        ], id="new-project-modal", is_open=False, size="lg",
           style={"fontFamily": "'DM Sans', sans-serif"}),

    ], style={"maxWidth": "1200px", "margin": "0 auto", "padding": "28px 32px"}),

], style={
    "minHeight": "100vh",
    "fontFamily": "'DM Sans', 'Segoe UI', sans-serif",
    "background": "#fff",
})





# ─────────────────────────────────────────
# CALLBACKS
# ─────────────────────────────────────────

# Active filter state stored in URL hash (workaround: use a store)
layout.children.insert(0, dcc.Store(id="active-filter", data="All"))


@callback(
    Output("projects-store", "data", allow_duplicate=True),
    Input("session-store", "data"),
    Input("create-project-btn", "n_clicks"),
    prevent_initial_call="initial_duplicate"
)
def load_projects(session_data, n_clicks):
    if not session_data or 'token' not in session_data:
        return []
    
    from frontend.services.projects import ProjectService
    token = session_data['token']
    response = ProjectService.get_projects(token)
    if response.status_code == 200:
        return response.json()
    return []


@callback(
    Output("active-filter", "data"),
    Input({"type": "filter-btn", "index": ALL}, "n_clicks"),
    State({"type": "filter-btn", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def update_filter(n_clicks, ids):
    triggered = ctx.triggered_id
    if triggered:
        return triggered["index"]
    return "All"


@callback(
    Output("filter-buttons", "children"),
    Input("active-filter", "data"),
)
def render_filter_buttons(active):
    filters = ["All", "In Progress", "Planning", "At Risk", "Completed", "On Hold"]
    return [
        dbc.Button(f, id={"type": "filter-btn", "index": f},
                   n_clicks=0,
                   style={
                       # "background": COLORS["accent"] if active == f else COLORS["card"],
                       # "color": "#fff" if active == f else COLORS["muted"],
                       # "border": f"1px solid {COLORS['accent'] if active == f else COLORS['border']}",
                       "borderRadius": "8px", "fontSize": "13px",
                       "fontWeight": "600", "padding": "6px 14px",
                   })
        for f in filters
    ]


@callback(
    Output("stat-cards", "children"),
    Output("budget-chart", "figure"),
    Output("status-donut", "figure"),
    Output("project-grid", "children"),
    Input("projects-store", "data"),
    Input("active-filter", "data"),
    Input("search-input", "value"),
)
def render_dashboard(projects, active_filter, search):
    # Stats
    total_budget = sum(p.get("budget", 0) for p in projects)
    total_spent = sum(p.get("spent", 0) for p in projects)
    at_risk = sum(1 for p in projects if p.get("status") == "At Risk")
    completed = sum(1 for p in projects if p.get("status") == "Completed")

    stats = dbc.Row([
        stat_card("Total Projects", str(len(projects)),
                  f"{sum(1 for p in projects if p.get('status')=='In Progress')} in progress",
                  "#4F8EF7", "📁"),
        stat_card("Total Budget", f"${total_budget/1000:.0f}k",
                  f"${total_spent/1000:.0f}k spent",
                  "#2DD4A0", "💰"),
        stat_card("At Risk", str(at_risk), "Needs attention",
                  "#F75F5F", "⚠️"),
        stat_card("Completed", str(completed), "All time",
                  "#9B7CF7", "✅"),
    ]).children

    # Filter
    filtered = [p for p in projects
                if (active_filter == "All" or p.get("status") == active_filter)
                and (not search or
                     search.lower() in p.get("name", "").lower() or
                     search.lower() in p.get("description", "").lower() or
                     any(search.lower() in str(t).lower() for t in p.get("tags", [])) or
                     any(search.lower() in str(m).lower() for m in p.get("team", [])))]

    cards = [project_card(p) for p in filtered]
    if not cards:
        cards = [dbc.Col(html.Div("No projects found.", style={
            "color": None,
            "textAlign": "center",
            "padding": "60px 0", "fontSize": "16px",
        }), md=12)]

    return stats, budget_chart(projects), status_donut(projects), cards


@callback(
    Output("selected-project-id", "data"),
    Input({"type": "project-card", "index": ALL}, "n_clicks"),
    State({"type": "project-card", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def select_project(n_clicks, ids):
    triggered = ctx.triggered_id
    if triggered and any(n for n in n_clicks if n):
        return triggered["index"]
    return None


@callback(
    Output("modal-container", "children"),
    Input("selected-project-id", "data"),
    State("projects-store", "data"),
    prevent_initial_call=True,
)
def show_modal(project_id, projects):
    if not project_id:
        return []
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return []
    return project_detail_modal(project)


@callback(
    Output("modal-container", "children", allow_duplicate=True),
    Input("close-modal", "n_clicks"),
    prevent_initial_call='initial_duplicate',
)
def close_modal(n):
    return []


@callback(
    Output("new-project-modal", "is_open"),
    Input("open-new-modal", "n_clicks"),
    Input("cancel-new-modal", "n_clicks"),
    Input("create-project-btn", "n_clicks"),
    State("new-project-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_new_modal(open_clicks, cancel_clicks, create_clicks, is_open):
    triggered = ctx.triggered_id
    if triggered in ("open-new-modal", "cancel-new-modal"):
        return not is_open
    return is_open


@callback(
    Output('new-output-file-name', 'children'),
    Input('new-upload-data', 'filename'),
)
def update_new_filename(filename):
    if filename:
        return f"Selected: {filename}"
    return ""


@callback(
    Output("new-project-error", "children"),
    Output("new-project-modal", "is_open", allow_duplicate=True),
    Input("create-project-btn", "n_clicks"),
    Input("session-store", "data"),
    State("new-name", "value"),
    State("new-description", "value"),
    State("new-status", "value"),
    State("new-priority", "value"),
    State("new-start-date", "value"),
    State("new-end-date", "value"),
    State("new-budget", "value"),
    State("new-spent", "value"),
    State("new-team", "value"),
    State("new-stakeholders", "value"),
    State("new-tags", "value"),
    State("new-upload-data", "contents"),
    State("new-upload-data", "filename"),
    prevent_initial_call='initial_duplicate',
)
def create_project(n, session_data, name, description, status, priority,
                   start_date, end_date, budget, spent,
                   team, stakeholders, tags, file_contents, filename):
    if not n:
        return "", False

    if not name or not start_date or not end_date or not budget:
        return "⚠️ Please fill in Name, Dates, and Budget.", True

    token = session_data.get("token") if session_data else None
    if not token:
        return "⚠️ Please log in to create a project.", True

    import base64
    from frontend.services.projects import ProjectService

    file_content = None
    content_type = None
    if file_contents:
        content_type, content_string = file_contents.split(',')
        file_content = base64.b64decode(content_string)

    # Project successfully sent to backend with all fields.
    
    response = ProjectService.create_project(
        token, name, status, description, 
        priority=priority, start_date=start_date, end_date=end_date,
        budget=budget, spent=spent, team=team, stakeholders=stakeholders, tags=tags,
        file_content=file_content, filename=filename, content_type=content_type
    )

    if response.status_code == 200:
        return "", False
    else:
        try:
            err = response.json().get("detail", "Failed to create project")
        except:
            err = "Failed to create project"
        return f"❌ {err}", True
