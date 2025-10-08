#!/usr/bin/env python
# coding: utf-8

# In[32]:


# ==========================================================
# Install dependencies
# ==========================================================


# ==========================================================
# Imports
# ==========================================================
from jupyter_dash import JupyterDash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np
import math, base64, random

# ==========================================================
# Hierarchy definition
# ==========================================================
children_map = {
    "Identity": ["Culture", "Purpose"],
    "Accountability": ["Business Context", "Strategy"],
    " Capability": ["Organization", "Talent"],
}

grandchildren_map = {
    "Culture": ["Mindset", "Climate"],
    "Purpose": ["Mission", "Vision"],
    "Business Context": ["Market", "Society"],
    "Strategy": ["Goals", "Challenges"],
    "Organization": ["Structure", "Processes"],
    "Talent": ["Leadership", "Employees"],
}

# ==========================================================
# Colors (you can adjust to match your exact palette)
# ==========================================================
colors = {
    "Identity": "#0D2240",
    "Accountability": "#007EA8",
    " Capability": "#3A9D23",

    "Culture": "#13293D",
    "Purpose": "#006494",
    "Business Context": "#0097A7",
    "Strategy": "#00ACC1",
    "Organization": "#81C784",
    "Talent": "#66BB6A",

    "Mindset": "#1B4353",
    "Climate": "#1E656D",
    "Mission": "#005073",
    "Vision": "#247BA0",
    "Market": "#4DD0E1",
    "Society": "#80DEEA",
    "Goals": "#00BCD4",
    "Challenges": "#B2EBF2",
    "Structure": "#A5D6A7",
    "Processes": "#C8E6C9",
    "Leadership": "#AED581",
    "Employees": "#C5E1A5",
}

placeholder_color = "#E0E0E0"

# ==========================================================
# Definitions (hover text for grandchildren)
# ==========================================================
definitions = {
    "Mindset": "The shared attitudes and assumptions within the organization.",
    "Climate": "The daily experience and tone of the workplace.",
    "Mission": "The core purpose of why the organization exists.",
    "Vision": "The aspirational future the organization strives toward.",
    "Market": "External economic and competitive environment.",
    "Society": "The social and regulatory context influencing the business.",
    "Goals": "The strategic outcomes the organization pursues.",
    "Challenges": "The key barriers or risks to achieving objectives.",
    "Structure": "The organization’s hierarchy and reporting relationships.",
    "Processes": "The systems, workflows, and procedures in place.",
    "Leadership": "The capabilities and mindset of top leaders.",
    "Employees": "The engagement, skill, and culture of the workforce."
}

# ==========================================================
# State tracking
# ==========================================================
active_cores = set()
active_children = set()
active_grandchildren = set()
# ==========================================================
# Figure builder
# ==========================================================
def build_figure():
    fig = go.Figure()

    # --------------------------
    # Ring geometry
    # --------------------------
    R_outer = 0.48
    hole_fraction = 0.35
    R_hole = R_outer * hole_fraction
    n_rings = 3
    band = (R_outer - R_hole) / n_rings

    # Radii
    R1, r1_in = R_hole + band, R_hole
    R2, r2_in = R_hole + 2 * band, R1
    R3, r3_in = R_outer, R2
    hole1, hole2, hole3 = r1_in / R1, r2_in / R2, r3_in / R3

    def domain_from_radius(R):
        return {"x": [0.5 - R, 0.5 + R], "y": [0.5 - R, 0.5 + R]}
    dom1, dom2, dom3 = map(domain_from_radius, (R1, R2, R3))

    core_labels = list(children_map.keys())
    core_colors = [colors[l] for l in core_labels]

    # --------------------------
    # Core ring
    # --------------------------
    fig.add_trace(go.Pie(
        labels=core_labels,
        values=[120] * 3,
        hole=hole1,
        marker=dict(colors=core_colors, line=dict(color="white", width=2)),
        textinfo="none",
        sort=False,
        direction="clockwise",
        rotation=90,
        name="Core",
        domain=dom1,
        hoverinfo="skip"
    ))

    # --------------------------
    # Children & grandchildren
    # --------------------------
    ring2_labels, ring2_colors, ring3_labels, ring3_colors = [], [], [], []
    for core in core_labels:
        for child in children_map[core]:
            if core in active_cores:
                ring2_labels.append(child)
                ring2_colors.append(colors[child])
            else:
                ring2_labels.append("")
                ring2_colors.append(placeholder_color)

            for gc in grandchildren_map[child]:
                if child in active_children:
                    ring3_labels.append(gc)
                    ring3_colors.append(colors[gc])
                else:
                    ring3_labels.append("")
                    ring3_colors.append(placeholder_color)

    # Child ring
    fig.add_trace(go.Pie(
        labels=ring2_labels,
        values=[60] * 6,
        hole=hole2,
        marker=dict(colors=ring2_colors, line=dict(color="white", width=1)),
        textinfo="none",
        sort=False,
        direction="clockwise",
        rotation=90,
        name="Children",
        domain=dom2,
        hoverinfo="skip"
    ))
    # --------------------------
    # Grandchildren ring (with hover labels)
    # --------------------------
    ring3_labels, ring3_colors, hovertemplates = [], [], []
    for core in core_labels:
        for child in children_map[core]:
            for gc in grandchildren_map[child]:
                if child in active_children:
                    # Active — show colored slice and definition
                    ring3_labels.append(gc)
                    ring3_colors.append(colors[gc])
                    hovertemplates.append(
                        f"<b>{gc}</b><br>{definitions.get(gc, '')}<extra></extra>"
                    )
                else:
                    # Inactive — show placeholder color, but still hover name
                    ring3_labels.append(gc)
                    ring3_colors.append(placeholder_color)
                    hovertemplates.append(f"<b>{gc}</b><extra></extra>")

    fig.add_trace(go.Pie(
        labels=ring3_labels,
        values=[30] * len(ring3_labels),
        hole=hole3,
        marker=dict(colors=ring3_colors, line=dict(color="white", width=1)),
        textinfo="none",
        sort=False,
        direction="clockwise",
        rotation=90,
        name="Grandchildren",
        domain=dom3,
        hoverinfo="none",
        hovertemplate=hovertemplates
    ))



    # --------------------------
    # Curved labels setup
    # --------------------------
    cx, cy, scale = 500.0, 500.0, 1000.0
    r_core_px = ((R1 + r1_in) / 2.0) * scale
    r_children_px = ((R2 + r2_in) / 2.0) * scale
    r_gc_px = ((R3 + r3_in) / 2.0) * scale

    def svg_arc_path(r, start_deg, end_deg):
        sr, er = math.radians(start_deg), math.radians(end_deg)
        x0, y0 = cx + r * math.cos(sr), cy - r * math.sin(sr)
        x1, y1 = cx + r * math.cos(er), cy - r * math.sin(er)
        delta = (start_deg - end_deg) % 360
        large_arc = 1 if delta > 180 else 0
        return f"M {x0:.2f},{y0:.2f} A {r:.2f},{r:.2f} 0 {large_arc} 1 {x1:.2f},{y1:.2f}"

    def arc_len(r, start, end):
        return r * abs((start - end) * math.pi / 180.0)

    def font_size_for(text, arclen, base=18, min_px=11, max_px=28):
        if not text:
            return 0
        est = arclen / (0.6 * len(text))
        return max(min_px, min(max_px, est, base))

    def shrink_span(start, end, factor=0.5):
        span = start - end
        return start - span * (1 - factor) / 2, end + span * (1 - factor) / 2

    # --------------------------
    # Label placement angles
    # --------------------------
    def assign_angles():
        CORE_OFFSET = 270
        CHILD_OFFSET = 2.5
        angles = {}
        for i, core in enumerate(core_labels):
            c_start, c_end = 90 - i * 120 + CORE_OFFSET, 90 - (i + 1) * 120 + CORE_OFFSET
            angles[core] = (c_start, c_end)
            children = children_map[core]
            span = (c_start - c_end) / len(children)
            for j, child in enumerate(children):
                ch_start = c_start - j * span + CHILD_OFFSET
                ch_end = c_start - (j + 1) * span + CHILD_OFFSET
                angles[child] = (ch_start, ch_end)
                gchildren = grandchildren_map[child]
                gspan = (ch_start - ch_end) / len(gchildren)
                for k, gc in enumerate(gchildren):
                    gc_start = ch_start - k * gspan
                    gc_end = ch_start - (k + 1) * gspan
                    angles[gc] = (gc_start, gc_end)
        return angles

    angles = assign_angles()
    svg_defs, svg_text = [], []

    for core in core_labels:
        start, end = angles[core]
        s, e = shrink_span(start, end, factor=0.7)
        path_id = f"core_{core}"
        svg_defs.append(f'<path id="{path_id}" d="{svg_arc_path(r_core_px, s, e)}" fill="none"/>')
        fs = font_size_for(core, arc_len(r_core_px, s, e), base=36) * 1.4
        svg_text.append(
            f'<text fill="white" font-family="Arial" font-size="{fs:.1f}" font-weight="700">'
            f'<textPath href="#{path_id}" startOffset="50%" text-anchor="middle">{core.upper()}</textPath></text>'
        )

    for child in ring2_labels:
        if not child:
            continue
        start, end = angles[child]
        s, e = shrink_span(start, end, factor=0.6)
        path_id = f"child_{child}"
        svg_defs.append(f'<path id="{path_id}" d="{svg_arc_path(r_children_px, s, e)}" fill="none"/>')
        fs = font_size_for(child, arc_len(r_children_px, s, e), base=20)
        svg_text.append(
            f'<text fill="white" font-family="Arial" font-size="{fs:.1f}" font-weight="600">'
            f'<textPath href="#{path_id}" startOffset="50%" text-anchor="middle">{child}</textPath></text>'
        )

    for gc in ring3_labels:
        if not gc:
            continue
        start, end = angles[gc]
        s, e = shrink_span(start, end, factor=0.6)
        path_id = f"gc_{gc}"
        svg_defs.append(f'<path id="{path_id}" d="{svg_arc_path(r_gc_px, s, e)}" fill="none"/>')
        fs = font_size_for(gc, arc_len(r_gc_px, s, e), base=16, max_px=20)
        svg_text.append(
            f'<text fill="white" font-family="Arial" font-size="{fs:.1f}" font-weight="500">'
            f'<textPath href="#{path_id}" startOffset="50%" text-anchor="middle">{gc}</textPath></text>'
        )

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" '
        'viewBox="0 0 1000 1000" style="pointer-events:none">'
        f'<defs>{"".join(svg_defs)}</defs><g>{"".join(svg_text)}</g></svg>'
    )
    svg_b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")

    # --------------------------
    # Layout images (SVG + center graphic)
    # --------------------------
    fig.update_layout(images=[
        dict(
            source=f"data:image/svg+xml;base64,{svg_b64}",
            xref="paper", yref="paper",
            x=0, y=1, sizex=1, sizey=1,
            xanchor="left", yanchor="top", layer="above"
        ),
        # ==========================
        # INSERT CENTER GRAPHIC HERE ↓↓↓
        # Replace with your PNG path
        # ==========================
        dict(
            source="assets/what_how_who.png",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=0.35, sizey=0.35,
            xanchor="center", yanchor="middle",
            layer="above"
        )
    ])

    fig.update_layout(margin=dict(t=40, l=40, r=40, b=40), showlegend=False)
    return fig


# ==========================================================
# DASH APP (JupyterDash)
# ==========================================================
app = JupyterDash(__name__)

app.layout = html.Div([
    html.H2("Interactive Org Success Profile", style={"textAlign": "center"}),
    dcc.Graph(id="donut", figure=build_figure(), style={"height": "90vh"})
])

@app.callback(
    Output("donut", "figure"),
    Input("donut", "clickData")
)
def update(clickData):
    global active_cores, active_children, active_grandchildren
    if not clickData:
        return build_figure()

    clicked = clickData["points"][0]["label"]

    # --- CASE 1: Core clicked ---
    if clicked in children_map:
        if clicked in active_cores:
            active_cores.remove(clicked)
            for c in children_map[clicked]:
                active_children.discard(c)
            # also clear grandchildren of that core
            for c in children_map[clicked]:
                for gc in grandchildren_map[c]:
                    active_grandchildren.discard(gc)
        else:
            active_cores.add(clicked)

    # --- CASE 2: Child clicked ---
    elif clicked in grandchildren_map:
        if clicked in active_children:
            # deactivate its grandchildren
            for gc in grandchildren_map[clicked]:
                active_grandchildren.discard(gc)
            active_children.remove(clicked)
        else:
            active_children.add(clicked)

    # --- CASE 3: Grandchild clicked ---
    else:
        parent_child = None
        for child, grandkids in grandchildren_map.items():
            if clicked in grandkids:
                parent_child = child
                break

        if parent_child:
            # ensure its parent child is active
            active_children.add(parent_child)
            # toggle this grandchild only
            if clicked in active_grandchildren:
                active_grandchildren.remove(clicked)
            else:
                # deactivate other grandchildren under the same parent
                for gc in grandchildren_map[parent_child]:
                    active_grandchildren.discard(gc)
                active_grandchildren.add(clicked)

    return build_figure()


# ==========================================================
# Run inline in Jupyter
# ==========================================================
if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8050)

server = app.server
