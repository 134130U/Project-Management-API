"""
ProjectOS — Dash Project Management System
==========================================
Run locally:
    pip install dash dash-bootstrap-components plotly pandas
    python app.py
Then open http://127.0.0.1:8050
"""

import dash
from dash import dcc, html, dash_table, Input, Output, State, ctx, MATCH, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import json
import copy

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
    return {"color": COLORS["muted"], "fontSize": "12px",
            "fontWeight": "600", "marginBottom": "5px", "display": "block"}


def form_input_style():
    return {"background": COLORS["bg"],
            "border": f"1px solid {COLORS['border']}",
            "color": COLORS["text"], "borderRadius": "8px",
            "fontSize": "14px", "width": "100%"}

# ─────────────────────────────────────────
# INITIAL DATA
# ─────────────────────────────────────────
INITIAL_PROJECTS = [
    {
        "id": 1,
        "name": "Platform Redesign",
        "description": "Full redesign of the main customer-facing platform.",
        "status": "In Progress",
        "priority": "High",
        "budget": 120000,
        "spent": 74000,
        "start_date": "2026-01-10",
        "end_date": "2026-06-30",
        "progress": 58,
        "team": ["Alice M.", "Bob K.", "Carol N.", "David L."],
        "stakeholders": ["CEO", "CTO", "Marketing"],
        "tags": ["Design", "Frontend"],
        "deliverables": [
            {"id": 1, "title": "UX Research Report", "done": True},
            {"id": 2, "title": "Wireframes v2",      "done": True},
            {"id": 3, "title": "Design System",       "done": False},
            {"id": 4, "title": "Frontend Implementation", "done": False},
        ],
    },
    {
        "id": 2,
        "name": "AI Analytics Engine",
        "description": "Build an ML-powered analytics engine for real-time insights.",
        "status": "Planning",
        "priority": "Critical",
        "budget": 250000,
        "spent": 18000,
        "start_date": "2026-03-01",
        "end_date": "2026-12-15",
        "progress": 12,
        "team": ["Eve R.", "Frank S.", "Grace T."],
        "stakeholders": ["CTO", "Data Team", "Investors"],
        "tags": ["AI/ML", "Backend", "Data"],
        "deliverables": [
            {"id": 1, "title": "Architecture Blueprint", "done": True},
            {"id": 2, "title": "Data Pipeline v1",       "done": False},
            {"id": 3, "title": "ML Model Training",      "done": False},
            {"id": 4, "title": "Dashboard Integration",  "done": False},
        ],
    },
    {
        "id": 3,
        "name": "Mobile App Launch",
        "description": "Native mobile apps for iOS and Android with full feature parity.",
        "status": "Completed",
        "priority": "Medium",
        "budget": 80000,
        "spent": 78500,
        "start_date": "2025-09-01",
        "end_date": "2026-02-28",
        "progress": 100,
        "team": ["Henry W.", "Iris C.", "Jake B.", "Kate D.", "Leo F."],
        "stakeholders": ["Product", "Marketing", "CEO"],
        "tags": ["Mobile", "iOS", "Android"],
        "deliverables": [
            {"id": 1, "title": "iOS App",           "done": True},
            {"id": 2, "title": "Android App",       "done": True},
            {"id": 3, "title": "App Store Launch",  "done": True},
            {"id": 4, "title": "Push Notifications","done": True},
        ],
    },
    {
        "id": 4,
        "name": "Security Audit & Hardening",
        "description": "Comprehensive security review and infrastructure hardening.",
        "status": "At Risk",
        "priority": "Critical",
        "budget": 45000,
        "spent": 38000,
        "start_date": "2026-01-15",
        "end_date": "2026-03-31",
        "progress": 70,
        "team": ["Mia J.", "Noah P."],
        "stakeholders": ["CISO", "CTO", "Legal"],
        "tags": ["Security", "Infrastructure"],
        "deliverables": [
            {"id": 1, "title": "Vulnerability Assessment", "done": True},
            {"id": 2, "title": "Penetration Testing",      "done": True},
            {"id": 3, "title": "Remediation Plan",         "done": False},
            {"id": 4, "title": "Compliance Report",        "done": False},
        ],
    },
]

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def days_left(end_date_str):
    end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    return (end - date.today()).days


def budget_pct(project):
    return round(project["spent"] / project["budget"] * 100, 1) if project["budget"] else 0


def progress_bar(value, color=None):
    pct = min(100, max(0, value))
    if color is None:
        color = COLORS["success"] if pct >= 100 else COLORS["danger"] if pct < 30 else COLORS["accent"]
    return html.Div([
        html.Div(style={
            "width": f"{pct}%", "height": "100%",
            "background": color, "borderRadius": "99px",
            "transition": "width 0.4s ease",
        })
    ], style={
        "background": COLORS["border"], "borderRadius": "99px",
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
        "flexShrink": "0", "border": f"2px solid {COLORS['surface']}",
    })


def stat_card(label, value, sub, color, icon):
    return dbc.Col(html.Div([
        html.Div([
            html.Div([
                html.Div(label, style={"color": COLORS["muted"], "fontSize": "12px",
                                       "marginBottom": "6px", "fontWeight": "500"}),
                html.Div(value, style={"color": color, "fontSize": "28px",
                                       "fontWeight": "800", "lineHeight": "1"}),
                html.Div(sub, style={"color": COLORS["muted"], "fontSize": "12px",
                                     "marginTop": "6px"}),
            ]),
            html.Div(icon, style={"fontSize": "28px", "opacity": "0.6"}),
        ], style={"display": "flex", "justifyContent": "space-between",
                  "alignItems": "flex-start"}),
    ], style={
        "background": COLORS["card"],
        "border": f"1px solid {COLORS['border']}",
        "borderRadius": "14px", "padding": "18px 22px",
    }), md=3)


def project_card(project):
    dl = days_left(project["end_date"])
    dl_color = COLORS["danger"] if dl < 0 else COLORS["warning"] if dl < 14 else COLORS["muted"]
    dl_text = (f"{abs(dl)}d overdue" if dl < 0 else
               "Due today" if dl == 0 else f"{dl}d left")
    bpct = budget_pct(project)
    b_color = (COLORS["danger"] if bpct > 90 else
               COLORS["warning"] if bpct > 70 else COLORS["success"])

    done_deliverables = sum(1 for d in project["deliverables"] if d["done"])

    return dbc.Col(
        html.Div([
            # Top row
            html.Div([
                html.Div([
                    html.Div(project["name"], style={
                        "fontWeight": "700", "fontSize": "16px",
                        "color": COLORS["text"], "marginBottom": "4px",
                    }),
                    html.Div(project["description"], style={
                        "fontSize": "12px", "color": COLORS["muted"],
                        "lineHeight": "1.4",
                        "overflow": "hidden",
                        "display": "-webkit-box",
                        "-webkit-line-clamp": "2",
                        "-webkit-box-orient": "vertical",
                    }),
                ], style={"flex": "1", "marginRight": "10px"}),
                html.Div([
                    badge(project["status"], STATUS_COLORS.get(project["status"], COLORS["muted"])),
                    html.Br(),
                    html.Span(style={"height": "4px", "display": "block"}),
                    badge(project["priority"], PRIORITY_COLORS.get(project["priority"], COLORS["muted"])),
                ], style={"flexShrink": "0", "textAlign": "right"}),
            ], style={"display": "flex", "marginBottom": "10px"}),

            # Tags
            html.Div([
                html.Span(t, style={
                    "background": COLORS["border"], "color": COLORS["muted"],
                    "borderRadius": "6px", "padding": "2px 8px",
                    "fontSize": "11px", "marginRight": "4px",
                }) for t in project["tags"]
            ], style={"marginBottom": "14px"}),

            # Progress
            html.Div([
                html.Div([
                    html.Span("Progress", style={"color": COLORS["muted"], "fontSize": "12px"}),
                    html.Span(f"{project['progress']}%", style={
                        "color": COLORS["text"], "fontSize": "12px", "fontWeight": "700"
                    }),
                ], style={"display": "flex", "justifyContent": "space-between",
                          "marginBottom": "4px"}),
                progress_bar(project["progress"]),
            ], style={"marginBottom": "10px"}),

            # Budget
            html.Div([
                html.Div([
                    html.Span("Budget", style={"color": COLORS["muted"], "fontSize": "12px"}),
                    html.Span(f"${project['spent']:,} / ${project['budget']:,}",
                              style={"color": b_color, "fontSize": "12px", "fontWeight": "600"}),
                ], style={"display": "flex", "justifyContent": "space-between",
                          "marginBottom": "4px"}),
                progress_bar(bpct, b_color),
            ], style={"marginBottom": "10px"}),

            # Deliverables quick stat
            html.Div([
                html.Span(f"📦 {done_deliverables}/{len(project['deliverables'])} deliverables",
                          style={"fontSize": "12px", "color": COLORS["muted"]}),
            ], style={"marginBottom": "12px"}),

            # Footer
            html.Div([
                html.Div([
                    *[html.Div(avatar_initials(m), style={"marginLeft": f"{-8 if i>0 else 0}px"})
                      for i, m in enumerate(project["team"][:4])],
                    *([] if len(project["team"]) <= 4 else [
                        html.Div(f"+{len(project['team'])-4}", style={
                            "marginLeft": "-8px", "width": "26px", "height": "26px",
                            "borderRadius": "50%", "background": COLORS["border"],
                            "color": COLORS["muted"], "fontSize": "10px",
                            "display": "flex", "alignItems": "center",
                            "justifyContent": "center", "border": f"2px solid {COLORS['surface']}",
                            "fontWeight": "700",
                        })
                    ]),
                ], style={"display": "flex", "alignItems": "center"}),
                html.Span(dl_text, style={
                    "color": dl_color, "fontSize": "12px", "fontWeight": "600"
                }),
            ], style={"display": "flex", "justifyContent": "space-between",
                      "alignItems": "center"}),

            # Hidden project id for callback
            html.Div(project["id"], id={"type": "card-id", "index": project["id"]},
                     style={"display": "none"}),
        ], id={"type": "project-card", "index": project["id"]},
           n_clicks=0,
           style={
               "background": COLORS["card"],
               "border": f"1px solid {COLORS['border']}",
               "borderRadius": "14px", "padding": "20px 22px",
               "cursor": "pointer",
               "boxShadow": "0 2px 12px #00000040",
               "transition": "border-color 0.2s, transform 0.15s",
               "height": "100%",
           }),
        md=4, style={"marginBottom": "16px"},
    )


def project_detail_modal(project):
    dl = days_left(project["end_date"])
    dl_color = COLORS["danger"] if dl < 0 else COLORS["warning"] if dl < 14 else COLORS["success"]
    dl_text = f"{abs(dl)}d overdue" if dl < 0 else f"{dl}d remaining"
    bpct = budget_pct(project)
    b_color = COLORS["danger"] if bpct > 90 else COLORS["warning"] if bpct > 70 else COLORS["success"]
    done_count = sum(1 for d in project["deliverables"] if d["done"])

    deliverable_items = []
    for d in project["deliverables"]:
        deliverable_items.append(
            html.Div([
                dbc.Checkbox(
                    id={"type": "deliverable-check", "index": d["id"]},
                    value=d["done"],
                    label=d["title"],
                    style={"color": COLORS["muted"] if d["done"] else COLORS["text"]},
                ),
            ], style={
                "padding": "8px 0",
                "borderBottom": f"1px solid {COLORS['border']}",
                "color": COLORS["muted"] if d["done"] else COLORS["text"],
                "textDecoration": "line-through" if d["done"] else "none",
            })
        )

    return dbc.Modal([
        dbc.ModalHeader([
            html.Div([
                html.H4(project["name"], style={
                    "color": COLORS["text"], "fontWeight": "800", "margin": "0 0 8px 0"
                }),
                html.Div([
                    badge(project["status"], STATUS_COLORS.get(project["status"], COLORS["muted"])),
                    html.Span(" ", style={"marginRight": "6px"}),
                    badge(project["priority"], PRIORITY_COLORS.get(project["priority"], COLORS["muted"])),
                ]),
            ])
        ], style={"background": COLORS["surface"], "borderBottom": f"1px solid {COLORS['border']}",
                  "color": COLORS["text"]}),

        dbc.ModalBody([
            html.P(project["description"], style={
                "color": COLORS["muted"], "fontSize": "14px",
                "lineHeight": "1.6", "marginBottom": "20px",
            }),

            # Date / deadline row
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("Start Date", style={"color": COLORS["muted"], "fontSize": "12px",
                                                   "marginBottom": "4px"}),
                    html.Div(project["start_date"], style={"fontWeight": "700", "color": COLORS["text"]}),
                ], style={"background": COLORS["bg"], "borderRadius": "10px",
                          "padding": "12px 14px", "border": f"1px solid {COLORS['border']}"})),
                dbc.Col(html.Div([
                    html.Div("End Date", style={"color": COLORS["muted"], "fontSize": "12px",
                                                 "marginBottom": "4px"}),
                    html.Div(project["end_date"], style={"fontWeight": "700", "color": COLORS["text"]}),
                ], style={"background": COLORS["bg"], "borderRadius": "10px",
                          "padding": "12px 14px", "border": f"1px solid {COLORS['border']}"})),
                dbc.Col(html.Div([
                    html.Div("Deadline", style={"color": COLORS["muted"], "fontSize": "12px",
                                                 "marginBottom": "4px"}),
                    html.Div(dl_text, style={"fontWeight": "700", "color": dl_color}),
                ], style={"background": COLORS["bg"], "borderRadius": "10px",
                          "padding": "12px 14px", "border": f"1px solid {COLORS['border']}"})),
            ], style={"marginBottom": "16px"}),

            # Budget
            html.Div([
                html.H6("💰 Budget", style={"color": COLORS["text"], "fontWeight": "700",
                                            "marginBottom": "12px"}),
                html.Div([
                    html.Span("Budget Used", style={"color": COLORS["muted"], "fontSize": "12px"}),
                    html.Span(f"{bpct}%", style={"color": b_color, "fontSize": "12px",
                                                  "fontWeight": "700"}),
                ], style={"display": "flex", "justifyContent": "space-between",
                          "marginBottom": "4px"}),
                progress_bar(bpct, b_color),
                html.Div([
                    html.Span(f"Spent: ${project['spent']:,}",
                              style={"color": COLORS["muted"], "fontSize": "11px"}),
                    html.Span(f"Total: ${project['budget']:,}",
                              style={"color": COLORS["muted"], "fontSize": "11px"}),
                ], style={"display": "flex", "justifyContent": "space-between",
                          "marginTop": "4px"}),
            ], style={"background": COLORS["bg"], "borderRadius": "12px",
                      "padding": "16px 18px", "border": f"1px solid {COLORS['border']}",
                      "marginBottom": "16px"}),

            # Progress
            html.Div([
                html.H6("📈 Progress", style={"color": COLORS["text"], "fontWeight": "700",
                                               "marginBottom": "12px"}),
                html.Div([
                    html.Span("Overall completion",
                              style={"color": COLORS["muted"], "fontSize": "13px"}),
                    html.Span(f"{project['progress']}%",
                              style={"color": COLORS["text"], "fontWeight": "700"}),
                ], style={"display": "flex", "justifyContent": "space-between",
                          "marginBottom": "6px"}),
                progress_bar(project["progress"]),
            ], style={"background": COLORS["bg"], "borderRadius": "12px",
                      "padding": "16px 18px", "border": f"1px solid {COLORS['border']}",
                      "marginBottom": "16px"}),

            # Deliverables
            html.Div([
                html.H6("📦 Deliverables", style={"color": COLORS["text"], "fontWeight": "700",
                                                   "marginBottom": "12px"}),
                *deliverable_items,
                html.Div(f"{done_count} / {len(project['deliverables'])} completed",
                         style={"color": COLORS["muted"], "fontSize": "12px",
                                "marginTop": "8px"}),
            ], style={"background": COLORS["bg"], "borderRadius": "12px",
                      "padding": "16px 18px", "border": f"1px solid {COLORS['border']}",
                      "marginBottom": "16px"}),

            # Team
            html.Div([
                html.H6(f"👥 Team ({len(project['team'])})",
                        style={"color": COLORS["text"], "fontWeight": "700",
                               "marginBottom": "12px"}),
                html.Div([
                    html.Div([
                        avatar_initials(m, 26),
                        html.Span(m, style={"color": COLORS["text"], "fontSize": "13px"}),
                    ], style={
                        "display": "flex", "alignItems": "center", "gap": "8px",
                        "background": COLORS["bg"], "border": f"1px solid {COLORS['border']}",
                        "borderRadius": "20px", "padding": "4px 12px 4px 4px",
                        "marginRight": "8px", "marginBottom": "8px",
                        "display": "inline-flex",
                    })
                    for m in project["team"]
                ], style={"display": "flex", "flexWrap": "wrap"}),
            ], style={"background": COLORS["bg"], "borderRadius": "12px",
                      "padding": "16px 18px", "border": f"1px solid {COLORS['border']}",
                      "marginBottom": "16px"}),

            # Stakeholders
            html.Div([
                html.H6("🏢 Stakeholders", style={"color": COLORS["text"], "fontWeight": "700",
                                                   "marginBottom": "12px"}),
                html.Div([
                    html.Span(s, style={
                        "background": "#1E3A6E", "color": COLORS["accent"],
                        "border": f"1px solid {COLORS['accent']}44",
                        "borderRadius": "8px", "padding": "4px 12px",
                        "fontSize": "13px", "marginRight": "8px", "marginBottom": "8px",
                        "display": "inline-block",
                    }) for s in project["stakeholders"]
                ]),
            ], style={"background": COLORS["bg"], "borderRadius": "12px",
                      "padding": "16px 18px", "border": f"1px solid {COLORS['border']}"}),

        ], style={"background": COLORS["surface"], "color": COLORS["text"]}),

        dbc.ModalFooter(
            dbc.Button("Close", id="close-modal", color="secondary"),
            style={"background": COLORS["surface"],
                   "borderTop": f"1px solid {COLORS['border']}"}
        ),
    ], id="project-modal", is_open=True, size="lg",
       style={"fontFamily": "'DM Sans', sans-serif"})


def budget_chart(projects):
    names = [p["name"] for p in projects]
    budgets = [p["budget"] for p in projects]
    spent = [p["spent"] for p in projects]

    fig = go.Figure()
    fig.add_bar(name="Budget", x=names, y=budgets,
                marker_color=COLORS["border"], marker_line_width=0)
    fig.add_bar(name="Spent", x=names, y=spent,
                marker_color=[
                    COLORS["danger"] if budget_pct(p) > 90
                    else COLORS["warning"] if budget_pct(p) > 70
                    else COLORS["success"]
                    for p in projects
                ],
                marker_line_width=0)
    fig.update_layout(
        barmode="overlay",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=COLORS["text"],
        font_family="DM Sans",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=10, b=10, l=0, r=0),
        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor=COLORS["border"],
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
        marker_colors=[STATUS_COLORS.get(s, COLORS["muted"])
                       for s in status_counts.keys()],
        textfont_color=COLORS["text"],
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=COLORS["text"],
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

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

app.layout = html.Div([
    # Store
    dcc.Store(id="projects-store", data=INITIAL_PROJECTS),
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
                    "letterSpacing": "-0.02em", "color": COLORS["text"],
                }),
            ], style={"display": "flex", "alignItems": "center", "gap": "12px"}),

            html.Div([
                dbc.Input(id="search-input", placeholder="Search projects, team, tags…",
                          type="text", debounce=True,
                          style={
                              "background": COLORS["card"],
                              "border": f"1px solid {COLORS['border']}",
                              "color": COLORS["text"], "borderRadius": "9px",
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
        "borderBottom": f"1px solid {COLORS['border']}",
        "background": COLORS["bg"] + "f8",
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
                    "color": COLORS["text"], "fontWeight": "700",
                    "fontSize": "14px", "marginBottom": "12px",
                }),
                dcc.Graph(id="budget-chart", config={"displayModeBar": False}),
            ], style={"background": COLORS["card"], "borderRadius": "14px",
                      "padding": "16px 18px",
                      "border": f"1px solid {COLORS['border']}"}), md=8),

            dbc.Col(html.Div([
                html.Div("Status Distribution", style={
                    "color": COLORS["text"], "fontWeight": "700",
                    "fontSize": "14px", "marginBottom": "12px",
                }),
                dcc.Graph(id="status-donut", config={"displayModeBar": False}),
            ], style={"background": COLORS["card"], "borderRadius": "14px",
                      "padding": "16px 18px",
                      "border": f"1px solid {COLORS['border']}"}), md=4),
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
                "color": COLORS["text"], "fontWeight": "800"
            }), style={"background": COLORS["surface"],
                       "borderBottom": f"1px solid {COLORS['border']}"}),
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
                ]),
                html.Div(id="new-project-error", style={"color": COLORS["danger"],
                                                          "fontSize": "13px"}),
            ], style={"background": COLORS["surface"]}),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-new-modal",
                           style={"background": COLORS["card"],
                                  "border": f"1px solid {COLORS['border']}",
                                  "color": COLORS["text"]}),
                dbc.Button("Create Project", id="create-project-btn", color="primary",
                           style={"background": "linear-gradient(135deg, #4F8EF7, #9B7CF7)",
                                  "border": "none", "fontWeight": "600"}),
            ], style={"background": COLORS["surface"],
                      "borderTop": f"1px solid {COLORS['border']}"}),
        ], id="new-project-modal", is_open=False, size="lg",
           style={"fontFamily": "'DM Sans', sans-serif"}),

    ], style={"maxWidth": "1200px", "margin": "0 auto", "padding": "28px 32px"}),

], style={
    "background": COLORS["bg"], "minHeight": "100vh",
    "fontFamily": "'DM Sans', 'Segoe UI', sans-serif",
    "color": COLORS["text"],
})





# ─────────────────────────────────────────
# CALLBACKS
# ─────────────────────────────────────────

# Active filter state stored in URL hash (workaround: use a store)
app.layout.children.insert(0, dcc.Store(id="active-filter", data="All"))


@app.callback(
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


@app.callback(
    Output("filter-buttons", "children"),
    Input("active-filter", "data"),
)
def render_filter_buttons(active):
    filters = ["All", "In Progress", "Planning", "At Risk", "Completed", "On Hold"]
    return [
        dbc.Button(f, id={"type": "filter-btn", "index": f},
                   n_clicks=0,
                   style={
                       "background": COLORS["accent"] if active == f else COLORS["card"],
                       "color": "#fff" if active == f else COLORS["muted"],
                       "border": f"1px solid {COLORS['accent'] if active == f else COLORS['border']}",
                       "borderRadius": "8px", "fontSize": "13px",
                       "fontWeight": "600", "padding": "6px 14px",
                   })
        for f in filters
    ]


@app.callback(
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
    total_budget = sum(p["budget"] for p in projects)
    total_spent = sum(p["spent"] for p in projects)
    at_risk = sum(1 for p in projects if p["status"] == "At Risk")
    completed = sum(1 for p in projects if p["status"] == "Completed")

    stats = dbc.Row([
        stat_card("Total Projects", str(len(projects)),
                  f"{sum(1 for p in projects if p['status']=='In Progress')} in progress",
                  COLORS["accent"], "📁"),
        stat_card("Total Budget", f"${total_budget/1000:.0f}k",
                  f"${total_spent/1000:.0f}k spent",
                  COLORS["success"], "💰"),
        stat_card("At Risk", str(at_risk), "Needs attention", COLORS["danger"], "⚠️"),
        stat_card("Completed", str(completed), "All time", COLORS["purple"], "✅"),
    ]).children

    # Filter
    filtered = [p for p in projects
                if (active_filter == "All" or p["status"] == active_filter)
                and (not search or
                     search.lower() in p["name"].lower() or
                     any(search.lower() in t.lower() for t in p["tags"]) or
                     any(search.lower() in m.lower() for m in p["team"]))]

    cards = [project_card(p) for p in filtered]
    if not cards:
        cards = [dbc.Col(html.Div("No projects found.", style={
            "color": COLORS["muted"], "textAlign": "center",
            "padding": "60px 0", "fontSize": "16px",
        }), md=12)]

    return stats, budget_chart(projects), status_donut(projects), cards


@app.callback(
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


@app.callback(
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


@app.callback(
    Output("modal-container", "children", allow_duplicate=True),
    Input("close-modal", "n_clicks"),
    prevent_initial_call=True,
)
def close_modal(n):
    return []


@app.callback(
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


@app.callback(
    Output("projects-store", "data"),
    Output("new-project-error", "children"),
    Output("new-project-modal", "is_open", allow_duplicate=True),
    Input("create-project-btn", "n_clicks"),
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
    State("projects-store", "data"),
    prevent_initial_call=True,
)
def create_project(n, name, description, status, priority,
                   start_date, end_date, budget, spent,
                   team, stakeholders, tags, projects):
    if not n:
        return projects, "", False

    if not name or not start_date or not end_date or not budget:
        return projects, "⚠️ Please fill in Name, Dates, and Budget.", True

    team_list = [t.strip() for t in (team or "").split(",") if t.strip()]
    stakeholder_list = [s.strip() for s in (stakeholders or "").split(",") if s.strip()]
    tags_list = [t.strip() for t in (tags or "").split(",") if t.strip()]

    new_id = max((p["id"] for p in projects), default=0) + 1
    new_project = {
        "id": new_id,
        "name": name,
        "description": description or "",
        "status": status or "Planning",
        "priority": priority or "Medium",
        "budget": int(budget),
        "spent": int(spent or 0),
        "start_date": start_date,
        "end_date": end_date,
        "progress": 0,
        "team": team_list,
        "stakeholders": stakeholder_list,
        "tags": tags_list,
        "deliverables": [],
    }
    return [new_project] + projects, "", False


# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
