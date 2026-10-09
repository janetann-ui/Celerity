import heapq

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# CELERITY - Emergency Response Route Optimizer
# Algorithm: Dijkstra's shortest path
# ============================================================

st.set_page_config(
    page_title="Celerity | Emergency Dispatch",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# Design tokens
# ------------------------------------------------------------
BG = "#0a0f18"
PANEL = "#101722"
PANEL_2 = "#141d2b"
BORDER = "#1f2b3d"
TEXT = "#e6edf5"
MUTED = "#8394a8"
FAINT = "#56667b"

ROAD = "#2a3a50"
ROUTE = "#34d399"
EXPLORED = "#38bdf8"
FRONTIER = "#fbbf24"
CURRENT = "#a78bfa"
START = "#3b82f6"
DEST = "#f43f5e"
NORMAL = "#4b5b72"
CLOSED = "#f97316"

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

html, body, .stApp, [class*="css"] {{
    font-family: 'IBM Plex Sans', -apple-system, 'Segoe UI', sans-serif;
}}
.stApp {{ background: {BG}; color: {TEXT}; }}
#MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
.block-container {{ max-width: 1400px; padding: 1.6rem 2rem 3rem 2rem; }}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {{
    background: {PANEL};
    border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] .block-container {{ padding-top: 1.4rem; }}
.brand {{ display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }}
.brand-mark {{
    width: 36px; height: 36px; border-radius: 9px;
    background: {DEST}; display: flex; align-items: center; justify-content: center;
    font-size: 19px;
}}
.brand-name {{ font-size: 1.25rem; font-weight: 700; color: {TEXT}; letter-spacing: -0.01em; }}
.brand-sub {{ color: {MUTED}; font-size: 0.78rem; margin: 2px 0 0 0; }}
.side-heading {{
    color: {TEXT}; font-size: 0.86rem; font-weight: 600;
    margin: 0 0 8px 0;
}}
.side-note {{ color: {MUTED}; font-size: 0.8rem; line-height: 1.5; }}

/* ---------- Page header ---------- */
.page-head {{
    display: flex; justify-content: space-between; align-items: flex-end;
    padding-bottom: 18px; margin-bottom: 20px; border-bottom: 1px solid {BORDER};
}}
.page-title {{ font-size: 1.85rem; font-weight: 700; letter-spacing: -0.02em; color: {TEXT}; margin: 0; line-height: 1.15; }}
.page-sub {{ color: {MUTED}; font-size: 0.92rem; margin-top: 6px; }}
.status {{
    display: inline-flex; align-items: center; gap: 8px;
    padding: 6px 12px; border-radius: 999px;
    border: 1px solid {BORDER}; background: {PANEL};
    color: {MUTED}; font-size: 0.8rem; font-weight: 500; white-space: nowrap;
}}
.dot {{ width: 8px; height: 8px; border-radius: 50%; background: {FAINT}; }}
.dot.live {{ background: {ROUTE}; box-shadow: 0 0 0 3px rgba(52,211,153,.18); }}
.dot.warn {{ background: {DEST}; }}

/* ---------- Incident strip ---------- */
.incident {{
    display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0;
    background: {PANEL}; border: 1px solid {BORDER}; border-radius: 12px;
    margin-bottom: 18px; overflow: hidden;
}}
.incident > div {{ padding: 16px 22px; border-right: 1px solid {BORDER}; }}
.incident > div:last-child {{ border-right: none; }}
.k {{ color: {MUTED}; font-size: 0.78rem; font-weight: 500; }}
.v {{ color: {TEXT}; font-size: 1.08rem; font-weight: 600; margin-top: 4px; }}
.v .tag {{
    display: inline-block; width: 9px; height: 9px; border-radius: 2px;
    margin-right: 9px; vertical-align: middle;
}}

/* ---------- Map frame + legend ---------- */
.map-bar {{
    display: flex; justify-content: space-between; align-items: center;
    background: {PANEL}; border: 1px solid {BORDER}; border-bottom: none;
    border-radius: 12px 12px 0 0; padding: 11px 18px;
}}
.map-title {{ font-size: 0.92rem; font-weight: 600; color: {TEXT}; }}
.legend {{ display: flex; gap: 18px; flex-wrap: wrap; }}
.legend span {{ color: {MUTED}; font-size: 0.78rem; display: inline-flex; align-items: center; gap: 7px; }}
.legend i {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
iframe[title="streamlit.components.v1.html"] {{
    border: 1px solid {BORDER}; border-radius: 0 0 12px 12px; background: {BG};
}}

/* ---------- Result ---------- */
.result-head {{ margin: 30px 0 14px 0; }}
.result-title {{ font-size: 1.2rem; font-weight: 650; color: {TEXT}; }}
.result-sub {{ color: {MUTED}; font-size: 0.88rem; margin-top: 3px; }}

.stats {{
    display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 18px;
}}
.stat {{
    background: {PANEL}; border: 1px solid {BORDER}; border-radius: 12px; padding: 16px 20px;
}}
.stat.primary {{ border-color: rgba(52,211,153,.45); background: linear-gradient(180deg, rgba(52,211,153,.07), {PANEL}); }}
.stat .num {{
    font-size: 1.75rem; font-weight: 700; color: {TEXT}; margin-top: 4px;
    font-variant-numeric: tabular-nums; letter-spacing: -0.02em;
}}
.stat .unit {{ font-size: 0.95rem; font-weight: 500; color: {MUTED}; margin-left: 4px; }}

/* Route timeline */
.timeline {{
    background: {PANEL}; border: 1px solid {BORDER}; border-radius: 12px;
    padding: 20px 24px; margin-bottom: 8px;
}}
.leg {{ display: flex; gap: 16px; position: relative; padding-bottom: 18px; }}
.leg:last-child {{ padding-bottom: 0; }}
.rail {{ display: flex; flex-direction: column; align-items: center; width: 14px; flex: none; }}
.pin {{ width: 12px; height: 12px; border-radius: 50%; border: 2px solid {ROUTE}; background: {BG}; margin-top: 4px; }}
.pin.start {{ border-color: {START}; background: {START}; }}
.pin.end {{ border-color: {DEST}; background: {DEST}; border-radius: 3px; }}
.line {{ width: 2px; flex: 1; background: {ROUTE}; opacity: .55; margin-top: 4px; }}
.leg:last-child .line {{ display: none; }}
.leg-name {{ color: {TEXT}; font-weight: 600; font-size: 0.98rem; }}
.leg-meta {{ color: {MUTED}; font-size: 0.82rem; margin-top: 2px; }}
.leg-time {{ margin-left: auto; color: {MUTED}; font-size: 0.85rem; font-variant-numeric: tabular-nums; white-space: nowrap; }}

/* ---------- Native widgets ---------- */
.stButton > button {{
    border-radius: 9px; font-weight: 600; min-height: 44px;
    border: 1px solid {BORDER}; transition: background .15s, border-color .15s;
}}
.stButton > button[kind="primary"] {{
    background: {DEST}; border-color: {DEST}; color: #fff;
}}
.stButton > button[kind="primary"]:hover {{ background: #e11d48; border-color: #e11d48; }}
.stButton > button:focus-visible {{ outline: 2px solid {START}; outline-offset: 2px; }}

div[data-baseweb="select"] > div {{ background: {PANEL_2}; border-color: {BORDER}; border-radius: 9px; }}
label, .stSelectbox label p, .stSlider label p {{ color: {MUTED} !important; font-size: 0.82rem !important; font-weight: 500 !important; }}
hr {{ border-color: {BORDER} !important; margin: 1.2rem 0 !important; }}

button[data-baseweb="tab"] {{ font-weight: 600; color: {MUTED}; padding: 10px 4px; margin-right: 18px; }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: {TEXT}; }}
div[data-baseweb="tab-highlight"] {{ background: {ROUTE}; }}
div[data-baseweb="tab-border"] {{ background: {BORDER}; }}

[data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 10px; overflow: hidden; }}

.note {{
    background: {PANEL}; border: 1px solid {BORDER}; border-left: 3px solid {ROUTE};
    border-radius: 8px; padding: 14px 18px; color: {TEXT}; font-size: 0.92rem; line-height: 1.6;
}}
.note b {{ color: #fff; }}
.footer {{ color: {FAINT}; font-size: 0.78rem; margin-top: 28px; }}

@media (max-width: 900px) {{
    .incident, .stats {{ grid-template-columns: 1fr 1fr; }}
    .page-head {{ flex-direction: column; align-items: flex-start; gap: 12px; }}
}}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# CITY NETWORK
# ============================================================

graph = {
    "City Hospital": [("University", 5), ("Residential Area", 3), ("Central Mall", 4)],
    "University": [("City Hospital", 5), ("City Library", 6), ("City Market", 7), ("Central Mall", 6)],
    "City Library": [("University", 6), ("Civic Center", 5), ("Tech Park", 8)],
    "Civic Center": [("City Library", 5), ("Tech Park", 5)],
    "Central Mall": [("City Hospital", 4), ("University", 6), ("Business District", 4), ("Tech Park", 9)],
    "City Market": [("University", 7), ("Residential Area", 4), ("Tech Park", 5)],
    "Residential Area": [("City Hospital", 3), ("City Market", 4), ("Tech Park", 2)],
    "Business District": [("Central Mall", 4), ("Tech Park", 3)],
    "Tech Park": [
        ("Residential Area", 2), ("Central Mall", 9), ("City Market", 5), ("City Library", 8),
        ("Civic Center", 5), ("Business District", 3), ("Railway Station", 4),
    ],
    "Railway Station": [("Tech Park", 4), ("Bus Terminal", 3)],
    "Bus Terminal": [("Railway Station", 3)],
}

positions = {
    "City Hospital": (0.5, 3.5),
    "University": (2.8, 6.3),
    "City Library": (5.6, 7.2),
    "Civic Center": (8.5, 6.3),
    "Central Mall": (5.0, 4.0),
    "City Market": (2.6, 1.5),
    "Residential Area": (0.5, 0.5),
    "Business District": (7.8, 3.0),
    "Tech Park": (10.2, 2.6),
    "Railway Station": (12.7, 2.6),
    "Bus Terminal": (14.6, 4.2),
}


def road_length(a, b):
    for n, w in graph[a]:
        if n == b:
            return w
    return None


def eta_parts(minutes):
    if minutes < 1:
        return str(round(minutes * 60)), "sec"
    return f"{minutes:.1f}", "min"


def fmt_duration(minutes):
    value, unit = eta_parts(minutes)
    return f"{value} {unit}"


blocked_edges = set()  # set from the sidebar; read by build_map_state


# ============================================================
# DIJKSTRA
# ============================================================

def dijkstra_steps(graph, start, destination):
    distances = {n: float("inf") for n in graph}
    previous = {n: None for n in graph}
    distances[start] = 0
    pq = [(0, start)]
    visited = set()
    steps = [{
        "current": None, "visited": set(), "frontier": {start},
        "distances": distances.copy(), "previous": previous.copy(),
        "description": f"Starting search from {start}",
    }]

    while pq:
        d, node = heapq.heappop(pq)
        if d > distances[node] or node in visited:
            continue
        visited.add(node)

        relaxed = []
        for nb, w in graph[node]:
            nd = d + w
            before = distances[nb]
            if nd < before:
                distances[nb] = nd
                previous[nb] = node
                heapq.heappush(pq, (nd, nb))
                result = "Updated"
            elif nb in visited:
                result = "Finalized"
            else:
                result = "No change"
            relaxed.append({"neighbor": nb, "road": w, "candidate": nd,
                            "before": before, "result": result})

        frontier = {n for _, n in pq if n not in visited}
        steps.append({
            "current": node, "visited": visited.copy(), "frontier": frontier,
            "distances": distances.copy(), "previous": previous.copy(),
            "relaxed": relaxed,
            "description": f"Evaluating {node} at {d} km",
        })
        if node == destination:
            break

    if distances[destination] == float("inf"):
        return None, float("inf"), steps, len(visited)

    route, cur = [], destination
    while cur is not None:
        route.append(cur)
        cur = previous[cur]
    route.reverse()

    steps.append({
        "current": destination, "visited": visited.copy(), "frontier": set(),
        "distances": distances.copy(), "previous": previous.copy(),
        "route": route, "description": "Optimal route identified",
    })
    return route, distances[destination], steps, len(visited)


def find_all_routes(graph, start, destination):
    routes = []

    def dfs(cur, path, dist):
        if cur == destination:
            routes.append((path.copy(), dist))
            return
        for nb, w in graph[cur]:
            if nb not in path:
                path.append(nb)
                dfs(nb, path, dist + w)
                path.pop()

    dfs(start, [start], 0)
    routes.sort(key=lambda r: r[1])
    return routes


# ============================================================
# MAP
# ============================================================

def build_map_state(graph, positions, start, destination,
                    visited=None, frontier=None, current=None, final_route=None):
    visited = visited or set()
    frontier = frontier or set()
    final_route = final_route or []

    route_edges = {frozenset((final_route[i], final_route[i + 1])) for i in range(len(final_route) - 1)}
    fig = go.Figure()
    drawn = set()

    for node in graph:
        for nb, dist in graph[node]:
            edge = frozenset((node, nb))
            if edge in drawn:
                continue
            drawn.add(edge)
            x0, y0 = positions[node]
            x1, y1 = positions[nb]
            on_route = edge in route_edges
            closed = edge in blocked_edges
            if closed:
                line = dict(color=CLOSED, width=2.5, dash="dash")
            else:
                line = dict(color=ROUTE if on_route else ROAD, width=6 if on_route else 2)
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1], mode="lines", line=line,
                hoverinfo="none", showlegend=False,
            ))
            fig.add_annotation(
                x=(x0 + x1) / 2, y=(y0 + y1) / 2,
                text="closed" if closed else f"{dist}",
                showarrow=False,
                font=dict(color=CLOSED if closed else (TEXT if on_route else MUTED), size=10),
                bgcolor=PANEL,
                bordercolor=CLOSED if closed else (ROUTE if on_route else BORDER),
                borderwidth=1, borderpad=3,
            )

    for node, (x, y) in positions.items():
        color, size, symbol = NORMAL, 22, "circle"
        if node in visited:
            color = EXPLORED
        if node in frontier:
            color = FRONTIER
        if node == current:
            color, size = CURRENT, 30
        if node in final_route:
            color, size = ROUTE, 26
        if node == start:
            color, size = START, 32
        if node == destination:
            color, size, symbol = DEST, 32, "diamond"

        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode="markers+text", text=[node], textposition="bottom center",
            textfont=dict(color=TEXT, size=11, family="IBM Plex Sans, sans-serif"),
            marker=dict(size=size, color=color, symbol=symbol, line=dict(color=BG, width=3)),
            hovertemplate=f"<b>{node}</b><extra></extra>", showlegend=False,
        ))

    fig.update_layout(
        height=610, paper_bgcolor=BG, plot_bgcolor=BG,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(visible=False, range=[-1.5, 16]),
        yaxis=dict(visible=False, range=[-1.5, 8.5]),
        hovermode="closest", dragmode="pan", showlegend=False,
        font=dict(family="IBM Plex Sans, sans-serif"),
        hoverlabel=dict(bgcolor=PANEL_2, bordercolor=BORDER, font=dict(color=TEXT)),
    )
    return fig


def create_animated_map(graph, positions, start, destination, steps, duration):
    s0 = steps[0]
    fig = build_map_state(graph, positions, start, destination,
                          s0["visited"], s0["frontier"], s0["current"], s0.get("route", []))
    frames = []
    for i, s in enumerate(steps):
        f = build_map_state(graph, positions, start, destination,
                            s["visited"], s["frontier"], s["current"], s.get("route", []))
        frames.append(go.Frame(name=f"step_{i}", data=f.data,
                               layout=go.Layout(annotations=f.layout.annotations)))
    fig.frames = frames

    btn_style = dict(bgcolor=PANEL_2, bordercolor=BORDER, borderwidth=1, font=dict(color=TEXT, size=12))
    fig.update_layout(
        updatemenus=[dict(
            type="buttons", direction="left", x=0.01, y=0.99, xanchor="left", yanchor="top",
            pad=dict(t=4, r=4), **btn_style,
            buttons=[
                dict(label="Replay", method="animate", args=[None, {
                    "frame": {"duration": duration, "redraw": True},
                    "transition": {"duration": 180}, "fromcurrent": False, "mode": "immediate"}]),
                dict(label="Pause", method="animate", args=[[None], {
                    "frame": {"duration": 0, "redraw": False},
                    "transition": {"duration": 0}, "mode": "immediate"}]),
            ],
        )],
        transition=dict(duration=180),
    )
    return fig


def render_interactive_map(fig, auto_play=False, height=650, duration=500):
    html = pio.to_html(
        fig, full_html=False, include_plotlyjs=True, auto_play=auto_play,
        animation_opts={"frame": {"duration": duration, "redraw": True},
                        "transition": {"duration": 180}, "fromcurrent": False},
        config={"responsive": True, "scrollZoom": True, "displaylogo": False,
                "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
    )
    components.html(
        f'<div style="width:100%;height:{height}px;overflow:hidden;background:{BG};">{html}</div>',
        height=height, scrolling=False,
    )


# ============================================================
# SEARCH TRACE EXPLORER
# Self-contained HTML (no Streamlit reruns while stepping)
# ============================================================

def build_trace_component(steps, start, destination, step_ms=1200):
    import json

    X0, X1, Y0, Y1, SC = -1.5, 16, -1.5, 8.5, 55
    W, H = int((X1 - X0) * SC), int((Y1 - Y0) * SC)
    INF = float("inf")

    def pt(n):
        x, y = positions[n]
        return (x - X0) * SC, (Y1 - y) * SC

    def li(num, text):
        return f"<div class='say'><span class='n'>{num}</span><div>{text}</div></div>"

    items = []
    for s in steps:
        cur, dist, prev = s["current"], s["distances"], s["previous"]
        visited, frontier = s["visited"], s["frontier"]
        final_route = s.get("route", [])
        relaxed = s.get("relaxed", [])
        is_final = bool(final_route)
        checked = {r["neighbor"] for r in relaxed}
        queue = sorted(frontier, key=lambda n: (dist[n], n))

        # ---------- Plain-language explanation ----------
        if cur is None:
            title = f"Start at {start}"
            say = (li(1, f"We start at <b>{start}</b> and give it a distance of <b>0 km</b>, "
                         "because we are already there.")
                   + li(2, "Every other place is marked <b>not reached yet</b>.")
                   + li(3, "One rule drives the whole search: <b>always visit the closest "
                           "unvisited place next</b>. Press Next or Play to begin."))
        elif is_final:
            title = "Route found"
            say = (li(1, f"We reached <b>{destination}</b> after <b>{dist[destination]} km</b>.")
                   + li(2, "To read off the route, go backwards. From each place, step to the "
                           f"place we <b>came from</b> (see the scoreboard) until we are back at {start}.")
                   + li(3, f"Route: <b>{' → '.join(final_route)}</b>"))
        else:
            d = dist[cur]
            lines = ""
            for r in relaxed:
                nb, road, cand, before = r["neighbor"], r["road"], r["candidate"], r["before"]
                if r["result"] == "Updated":
                    old = "nothing yet" if before == INF else f"{before} km"
                    lines += (f"<li class='up'><b>{nb}</b>: {d} + {road} = <b>{cand} km</b>. "
                              f"Better than {old}, so we <b>update</b> it.</li>")
                elif r["result"] == "No change":
                    lines += (f"<li class='keep'><b>{nb}</b>: {d} + {road} = {cand} km. "
                              f"Not better than {before} km, so we <b>keep</b> the old value.</li>")
                else:
                    lines += f"<li class='done'><b>{nb}</b>: already visited, nothing to improve.</li>"
            if cur == destination:
                third = f"<b>{destination}</b> is the emergency location, so the search can stop."
            elif queue:
                third = (f"Next up: <b>{queue[0]}</b> at {dist[queue[0]]} km, "
                         "the closest place still waiting.")
            else:
                third = "Nothing is left waiting."
            title = f"Visit {cur} ({d} km away)"
            say = (li(1, f"Pick the closest unvisited place: <b>{cur}</b> at <b>{d} km</b>. "
                         "Nothing unvisited is closer, so this distance is now final.")
                   + li(2, f"Check each road leaving {cur}. Add the road length to {d} km and "
                           f"see if it beats what we already know.<ul class='chk'>{lines}</ul>")
                   + li(3, third))

        # ---------- Mini map ----------
        route_edges = {frozenset(p) for p in zip(final_route, final_route[1:])}
        parts, done = [], set()
        for a in graph:
            for b, w in graph[a]:
                e = frozenset((a, b))
                if e in done:
                    continue
                done.add(e)
                (x0, y0), (x1, y1) = pt(a), pt(b)
                closed = e in blocked_edges
                if closed:
                    style = f"stroke='{CLOSED}' stroke-width='2.5' stroke-dasharray='6 5'"
                elif e in route_edges:
                    style = f"stroke='{ROUTE}' stroke-width='6' stroke-linecap='round'"
                elif cur is not None and not is_final and cur in e and (e - {cur}) <= checked:
                    style = f"stroke='{CURRENT}' stroke-width='4'"
                else:
                    style = f"stroke='{ROAD}' stroke-width='2'"
                parts.append(f"<line x1='{x0:.0f}' y1='{y0:.0f}' x2='{x1:.0f}' y2='{y1:.0f}' {style}/>")
                parts.append(f"<text class='ek' x='{(x0 + x1) / 2:.0f}' y='{(y0 + y1) / 2 + 4:.0f}'>"
                             f"{'closed' if closed else w}</text>")
        for n in graph:
            x, y = pt(n)
            if is_final and n in final_route:
                col = ROUTE
            elif n == cur:
                col = CURRENT
            elif n in visited:
                col = EXPLORED
            elif n in frontier:
                col = FRONTIER
            else:
                col = NORMAL
            ring = START if n == start else (DEST if n == destination else BG)
            parts.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='12' fill='{col}' stroke='{ring}' stroke-width='3'/>")
            parts.append(f"<text class='nm' x='{x:.0f}' y='{y + 31:.0f}'>{n}</text>")
            if dist[n] != INF:
                parts.append(f"<text class='dk' x='{x:.0f}' y='{y - 19:.0f}'>{dist[n]} km</text>")
        map_html = f"<svg viewBox='0 0 {W} {H}' role='img' aria-label='City map for this step'>{''.join(parts)}</svg>"

        # ---------- Waiting list ----------
        if queue:
            chips = "".join(
                f"<span class='chip{' next' if k == 0 and not is_final else ''}'>{n}<b>{dist[n]} km</b></span>"
                for k, n in enumerate(queue))
            queue_html = f"<div class='chips'>{chips}</div>"
        else:
            queue_html = "<div class='hint'>Nobody is waiting.</div>"

        # ---------- Scoreboard ----------
        def status(n):
            if n == cur and not is_final:
                return 0, "Visiting now", "s-cur"
            if n in visited:
                return 1, "Done", "s-fin"
            if n in frontier:
                return 2, "Waiting", "s-q"
            return 3, "Not reached yet", "s-no"

        rows = ""
        for n in sorted(graph, key=lambda n: (status(n)[0], dist[n], n)):
            _, label, cls = status(n)
            came = prev[n] if prev[n] else ("start" if n == start else "—")
            shown = "—" if dist[n] == INF else f"{dist[n]} km"
            on = " class='onroute'" if n in final_route else ""
            rows += (f"<tr{on}><td>{n}</td><td>{shown}</td>"
                     f"<td><span class='badge {cls}'>{label}</span></td><td>{came}</td></tr>")
        dist_html = ("<table><tr><th>Place</th><th>Distance</th><th>Status</th>"
                     f"<th>Came from</th></tr>{rows}</table>")

        # ---------- Tree ----------
        children = {}
        for n, p in prev.items():
            if p is not None:
                children.setdefault(p, []).append(n)

        def node_html(n):
            if n in final_route:
                color = ROUTE
            elif n == cur:
                color = CURRENT
            elif n in visited:
                color = EXPLORED
            else:
                color = FRONTIER
            kids = sorted(children.get(n, []), key=lambda c: (dist[c], c))
            sub = "<ul>" + "".join(node_html(k) for k in kids) + "</ul>" if kids else ""
            return (f"<li><span class='tn' style='border-color:{color}'>"
                    f"<i style='background:{color}'></i>{n}<b>{dist[n]} km</b></span>{sub}</li>")

        items.append({"title": title, "say": say, "map": map_html, "queue": queue_html,
                      "dist": dist_html, "tree": f"<ul class='tree'>{node_html(start)}</ul>"})

    root = (f":root{{--bg:{BG};--panel:{PANEL};--panel2:{PANEL_2};--border:{BORDER};--text:{TEXT};"
            f"--muted:{MUTED};--faint:{FAINT};--route:{ROUTE};--explored:{EXPLORED};"
            f"--frontier:{FRONTIER};--current:{CURRENT};--normal:{NORMAL};--closed:{CLOSED};}}")

    css = root + """
    *{box-sizing:border-box}
    body{margin:0;background:var(--bg);color:var(--text);font-family:'IBM Plex Sans',-apple-system,'Segoe UI',sans-serif;font-size:14px}
    .wrap{padding:4px 2px 16px}
    .ctrl{display:flex;align-items:center;gap:12px;margin-bottom:14px}
    .ctrl button{background:var(--panel2);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:8px 16px;font-size:13px;font-weight:600;font-family:inherit;cursor:pointer}
    .ctrl button:hover:not(:disabled){border-color:var(--route)}
    .ctrl button:disabled{opacity:.4;cursor:default}
    .ctrl button:focus-visible,input:focus-visible,summary:focus-visible{outline:2px solid #3b82f6;outline-offset:2px}
    input[type=range]{flex:1;accent-color:var(--route)}
    #lbl{color:var(--muted);font-size:13px;min-width:92px;text-align:right;font-variant-numeric:tabular-nums}
    .card{background:var(--panel);border:1px solid var(--border);border-left:3px solid var(--route);border-radius:10px;padding:16px 20px;margin-bottom:16px}
    .title{font-size:17px;font-weight:650;margin-bottom:10px}
    .say{display:flex;gap:12px;align-items:flex-start;margin-top:10px;line-height:1.55;color:var(--muted)}
    .say b{color:var(--text)}
    .n{flex:none;width:22px;height:22px;border-radius:50%;background:var(--panel2);border:1px solid var(--border);color:var(--text);font-size:12px;font-weight:600;display:flex;align-items:center;justify-content:center;margin-top:1px}
    ul.chk{list-style:none;margin:8px 0 0;padding:0}
    ul.chk li{padding:6px 10px;margin-bottom:5px;border-radius:7px;background:var(--panel2);border-left:3px solid var(--faint);font-size:13px}
    ul.chk li.up{border-left-color:var(--route)}
    ul.chk li.keep{border-left-color:var(--frontier)}
    .grid{display:grid;grid-template-columns:1.35fr 1fr;gap:18px}
    @media(max-width:820px){.grid{grid-template-columns:1fr}}
    h4{margin:0 0 8px;font-size:13px;font-weight:600;color:var(--text)}
    .col>div+h4{margin-top:16px}
    .hint{color:var(--muted);font-size:12.5px;line-height:1.5;margin-bottom:8px}
    .mapbox{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:6px}
    svg{width:100%;height:auto;display:block}
    svg .nm{text-anchor:middle;fill:var(--text);font-size:12px}
    svg .dk{text-anchor:middle;fill:var(--frontier);font-size:11px;font-weight:600}
    svg .ek{text-anchor:middle;fill:var(--muted);font-size:10px;paint-order:stroke;stroke:var(--panel);stroke-width:4px}
    .key{display:flex;flex-wrap:wrap;gap:14px;margin:10px 0 0;color:var(--muted);font-size:12px}
    .key span{display:inline-flex;align-items:center;gap:6px}
    .key i{width:9px;height:9px;border-radius:50%;display:inline-block}
    table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--border);border-radius:10px;overflow:hidden;font-size:13px}
    th{color:var(--muted);font-weight:500;text-align:left;padding:8px 10px;border-bottom:1px solid var(--border);font-size:12px}
    td{padding:7px 10px;border-bottom:1px solid var(--border);font-variant-numeric:tabular-nums}
    tr:last-child td{border-bottom:none}
    tr.onroute td{background:rgba(52,211,153,.08)}
    .badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:600;border:1px solid var(--border);color:var(--muted);white-space:nowrap}
    .s-cur{background:rgba(167,139,250,.2);border-color:rgba(167,139,250,.55);color:var(--current)}
    .s-fin{color:var(--explored);border-color:rgba(56,189,248,.4)}
    .s-q{color:var(--frontier);border-color:rgba(251,191,36,.4)}
    .s-no{color:var(--faint)}
    .chips{display:flex;flex-wrap:wrap;gap:8px}
    .chip{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:5px 10px;font-size:13px}
    .chip b{margin-left:8px;color:var(--frontier);font-weight:600}
    .chip.next{border-color:var(--frontier)}
    details{margin-top:18px;background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:12px 16px}
    summary{cursor:pointer;font-weight:600;font-size:13px}
    details[open] summary{margin-bottom:10px}
    .tree,.tree ul{list-style:none;margin:0;padding-left:26px}
    .tree{padding-left:0}
    .tree li{position:relative;padding:5px 0 5px 20px}
    .tree>li{padding-left:0}
    .tree ul li::before{content:"";position:absolute;left:-1px;top:0;bottom:0;border-left:1px solid var(--faint)}
    .tree ul li:last-child::before{height:19px;bottom:auto}
    .tree ul li::after{content:"";position:absolute;left:-1px;top:19px;width:18px;border-top:1px solid var(--faint)}
    .tn{display:inline-flex;align-items:center;gap:8px;background:var(--panel2);border:1px solid;border-radius:8px;padding:4px 10px;font-size:13px;white-space:nowrap}
    .tn i{width:8px;height:8px;border-radius:50%;display:inline-block}
    .tn b{color:var(--muted);font-weight:500;font-variant-numeric:tabular-nums}
    """

    html = f"""
<style>@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');{css}</style>
<div class="wrap">
  <div class="ctrl">
    <button id="play">Play</button>
    <button id="prev">Previous</button>
    <input id="sl" type="range" min="0" max="{len(items) - 1}" value="0" aria-label="Search step">
    <button id="next">Next</button>
    <span id="lbl"></span>
  </div>
  <div class="card"><div id="title" class="title"></div><div id="say"></div></div>
  <div class="grid">
    <div class="col">
      <h4>Where we are on the map</h4>
      <div class="mapbox"><div id="map"></div></div>
      <div class="key">
        <span><i style="background:var(--current)"></i>Visiting now</span>
        <span><i style="background:var(--explored)"></i>Done</span>
        <span><i style="background:var(--frontier)"></i>Waiting</span>
        <span><i style="background:var(--normal)"></i>Not reached yet</span>
        <span><i style="background:var(--route)"></i>Final route</span>
      </div>
      <h4 style="margin-top:16px">Waiting list (closest first)</h4>
      <div id="queue"></div>
    </div>
    <div class="col">
      <h4>Scoreboard</h4>
      <div class="hint">Shortest distance found so far from {start} to each place.</div>
      <div id="dist"></div>
    </div>
  </div>
  <details>
    <summary>Show the path tree</summary>
    <div class="hint">Each place hangs under the place we came from. Following a branch from the top shows the route to that place.</div>
    <div id="tree"></div>
  </details>
</div>
<script>
const S = {json.dumps(items, ensure_ascii=False).replace("</", "<\\/")};
const n = S.length;
const $ = id => document.getElementById(id);
function show(k) {{
  const i = Math.max(0, Math.min(n - 1, k));
  for (const key of ["title", "say", "map", "queue", "dist", "tree"]) $(key).innerHTML = S[i][key];
  $("sl").value = i;
  $("lbl").textContent = "Step " + (i + 1) + " of " + n;
  $("prev").disabled = i === 0;
  $("next").disabled = i === n - 1;
  window.cur = i;
}}
let timer = null;
function stop() {{
  if (timer) {{ clearInterval(timer); timer = null; }}
  $("play").textContent = "Play";
}}
$("prev").onclick = () => {{ stop(); show(window.cur - 1); }};
$("next").onclick = () => {{ stop(); show(window.cur + 1); }};
$("sl").oninput = e => {{ stop(); show(+e.target.value); }};
$("play").onclick = () => {{
  if (timer) {{ stop(); return; }}
  if (window.cur >= n - 1) show(0);
  $("play").textContent = "Pause";
  timer = setInterval(() => {{
    show(window.cur + 1);
    if (window.cur >= n - 1) stop();
  }}, {step_ms});
}};
show(0);
</script>
"""
    return html


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.html("""
    <div class="brand">
        <div class="brand-mark">🚑</div>
        <div class="brand-name">Celerity</div>
    </div>
    <div class="brand-sub">Emergency response routing</div>
    """)
    st.divider()

    st.html('<div class="side-heading">Dispatch</div>')
    start = st.selectbox("Dispatch from", ["City Hospital"])
    destination = st.selectbox("Emergency location", [n for n in graph if n != start])

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    find_route = st.button("Find fastest route", use_container_width=True, type="primary")
    st.caption("Calculates the shortest road distance from the dispatch point.")

    st.divider()
    st.html('<div class="side-heading">Road closures</div>')
    edge_options = {}
    for a in graph:
        for b, w in graph[a]:
            if a < b:
                edge_options[f"{a} – {b} ({w} km)"] = frozenset((a, b))
    closed_labels = st.multiselect("Closed roads", list(edge_options), placeholder="None")
    blocked_edges = {edge_options[label] for label in closed_labels}
    st.caption("Closed roads are skipped and the route is recalculated.")

    st.divider()
    st.html('<div class="side-heading">Response</div>')
    avg_speed = st.slider("Average speed (km/h)", 20, 80, 40, step=5)
    st.caption("Assumed speed used to estimate arrival time.")

    st.divider()
    st.html('<div class="side-heading">Simulation</div>')
    speed = st.select_slider("Search animation speed", options=["Fast", "Normal", "Slow"], value="Normal")
    animation_duration = {"Fast": 280, "Normal": 500, "Slow": 800}[speed]

    st.divider()
    st.html("""
    <div class="side-heading">Method</div>
    <div class="side-note">
        Dijkstra's algorithm finds the minimum-distance route
        across the weighted road network.
    </div>
    """)

# ============================================================
# HEADER
# ============================================================

closure_html = (
    f' <span class="k">({len(blocked_edges)} road{"s" if len(blocked_edges) != 1 else ""} closed)</span>'
    if blocked_edges else ""
)
status_html = (
    '<span class="status"><span class="dot live"></span>Route calculated</span>'
    if find_route else
    '<span class="status"><span class="dot"></span>Awaiting dispatch</span>'
)
st.html(f"""
<div class="page-head">
    <div>
        <div class="page-title">Emergency Dispatch Console</div>
        <div class="page-sub">Shortest-path routing for ambulance response across the city network.</div>
    </div>
    {status_html}
</div>
<div class="incident">
    <div><div class="k">Dispatch point</div>
         <div class="v"><span class="tag" style="background:{START}"></span>{start}</div></div>
    <div><div class="k">Emergency location</div>
         <div class="v"><span class="tag" style="background:{DEST}"></span>{destination}</div></div>
    <div><div class="k">Routing method</div>
         <div class="v">Dijkstra shortest path{closure_html}</div></div>
</div>
""")

# ============================================================
# COMPUTE
# ============================================================

active_graph = {
    n: [(nb, w) for nb, w in nbrs if frozenset((n, nb)) not in blocked_edges]
    for n, nbrs in graph.items()
}
route = distance = steps = None
nodes_explored = 0
base_route = base_distance = None
if find_route:
    route, distance, steps, nodes_explored = dijkstra_steps(active_graph, start, destination)
    if blocked_edges:
        base_route, base_distance, _, _ = dijkstra_steps(graph, start, destination)

# ============================================================
# MAP
# ============================================================

legend = [(START, "Dispatch"), (DEST, "Emergency"), (FRONTIER, "Frontier"),
          (EXPLORED, "Explored"), (CURRENT, "Evaluating"), (ROUTE, "Optimal route"), (CLOSED, "Closed road")]
legend_html = "".join(f'<span><i style="background:{c}"></i>{t}</span>' for c, t in legend)
st.html(f"""
<div class="map-bar">
    <div class="map-title">City road network</div>
    <div class="legend">{legend_html}</div>
</div>
""")

if find_route and route is not None:
    render_interactive_map(
        create_animated_map(graph, positions, start, destination, steps, animation_duration),
        auto_play=True, height=650, duration=animation_duration,
    )
elif not find_route:
    render_interactive_map(build_map_state(graph, positions, start, destination), height=650)
else:
    if blocked_edges:
        st.error(f"No route to {destination} is available with the current road closures. "
                 "Reopen a road in the sidebar to restore access.")
    else:
        st.error("No route could be found between the selected locations.")

st.caption("Road labels show distance in km. Scroll to zoom and drag to pan.")

# ============================================================
# RESULTS
# ============================================================

if find_route and route is not None:
    eta_value, eta_unit = eta_parts(distance / avg_speed * 60)
    st.html(f"""
    <div class="result-head">
        <div class="result-title">Recommended route</div>
        <div class="result-sub">{start} to {destination}</div>
    </div>
    <div class="stats">
        <div class="stat primary"><div class="k">Total distance</div>
            <div class="num">{distance}<span class="unit">km</span></div></div>
        <div class="stat"><div class="k">Estimated arrival</div>
            <div class="num">{eta_value}<span class="unit">{eta_unit} at {avg_speed} km/h</span></div></div>
        <div class="stat"><div class="k">Stops on route</div>
            <div class="num">{len(route)}</div></div>
        <div class="stat"><div class="k">Road segments</div>
            <div class="num">{len(route) - 1}</div></div>
        <div class="stat"><div class="k">Locations explored</div>
            <div class="num">{nodes_explored}<span class="unit">of {len(graph)}</span></div></div>
    </div>
    """)

    legs = []
    km_so_far = 0
    for i, node in enumerate(route):
        cls = "start" if i == 0 else ("end" if i == len(route) - 1 else "")
        if i < len(route) - 1:
            seg = road_length(node, route[i + 1])
            meta = f"{seg} km to {route[i + 1]}"
        else:
            seg = 0
            meta = "Arrival at emergency location"
        if i == 0:
            meta = "Dispatch point. " + meta
            when = "Depart"
        else:
            when = "Arrive " + fmt_duration(km_so_far / avg_speed * 60)
        legs.append(
            f'<div class="leg"><div class="rail"><div class="pin {cls}"></div><div class="line"></div></div>'
            f'<div><div class="leg-name">{node}</div><div class="leg-meta">{meta}</div></div>'
            f'<div class="leg-time">{when}</div></div>'
        )
        km_so_far += seg
    st.html(f'<div class="timeline">{"".join(legs)}</div>')

    if blocked_edges and base_route is not None:
        if base_route == route:
            reroute = "The selected road closures do not affect this route."
        else:
            extra = distance - base_distance
            extra_t = fmt_duration(extra / avg_speed * 60)
            reroute = (f"<b>Rerouted around closures.</b> The normal route is "
                       f"{' → '.join(base_route)} ({base_distance} km). The detour is "
                       f"<b>{distance} km</b>, which is {extra} km longer and adds about {extra_t}.")
        st.html(f'<div class="note" style="border-left-color:{CLOSED};margin-bottom:18px">{reroute}</div>')

    tab_alt, tab_why, tab_trace, tab_algo = st.tabs(
        ["Alternative routes", "Why this route", "Search trace", "About the algorithm"]
    )

    all_routes = find_all_routes(active_graph, start, destination)

    with tab_alt:
        rows = []
        for rank, (path, d) in enumerate(all_routes[:8], start=1):
            if path == route:
                decision = "Selected"
            else:
                diff = d - distance
                decision = f"+{diff} km" if diff > 0 else "Equivalent"
            rows.append({"Rank": rank, "Route": " → ".join(path),
                         "Distance": f"{d} km", "Decision": decision})
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.caption(f"Showing the {len(rows)} shortest of {len(all_routes)} possible routes.")

    with tab_why:
        alt = next(((p, d) for p, d in all_routes if p != route), None)
        if alt is None:
            st.html('<div class="note">This is the only possible route between the two locations.</div>')
        else:
            diff = alt[1] - distance
            if diff > 0:
                body = (f"This route is the shortest available at <b>{distance} km</b>. "
                        f"The next best alternative is <b>{alt[1]} km</b>, which is "
                        f"<b>{diff} km longer</b>.")
            else:
                body = (f"This route is one of several with the minimum distance of <b>{distance} km</b>.")
            st.html(f"""
            <div class="note">{body}<br><br>
            Dijkstra always expands the closest unexplored location first and updates the
            distances of its neighbours. Once the emergency location is selected, its distance
            is final, so no shorter route can exist.</div>
            """)

    with tab_trace:
        st.caption("Press Play, or use Next to go one step at a time. Each step explains what the "
                   "algorithm picks, what it checks, and why.")
        components.html(build_trace_component(steps, start, destination,
                                              step_ms=max(700, animation_duration * 2)),
                        height=1100, scrolling=True)

        st.markdown("**All steps at a glance**")
        trace = []
        for i, s in enumerate(steps, start=1):
            cur, dist_map = s["current"], s["distances"]
            if cur is None:
                picked, final_d = "Start", 0
            elif s.get("route"):
                picked, final_d = "Done", dist_map[destination]
            else:
                picked, final_d = cur, dist_map[cur]
            updates = ", ".join(f"{r['neighbor']} ({r['candidate']} km)"
                                for r in s.get("relaxed", []) if r["result"] == "Updated")
            queue = ", ".join(f"{n} ({dist_map[n]})"
                              for n in sorted(s["frontier"], key=lambda n: dist_map[n]))
            trace.append({
                "Step": i,
                "Location picked": picked,
                "Final distance": f"{final_d} km",
                "Distances updated": updates or "None",
                "Queue after step": queue or "Empty",
                "Explored": len(s["visited"]),
            })
        st.dataframe(trace, use_container_width=True, hide_index=True)

    with tab_algo:
        st.markdown("""
**Dijkstra's shortest path algorithm** finds the minimum-distance path from a start node
to every reachable node in a graph with non-negative edge weights.

1. Set the dispatch point's distance to 0 and every other location to infinity.
2. Pick the unvisited location with the smallest known distance.
3. Check each neighbouring road and update the neighbour if a shorter distance is found.
4. Repeat until the emergency location is selected.
5. Rebuild the route by following the predecessor of each location back to the start.

**Time complexity:** `O((V + E) log V)`  **Space complexity:** `O(V + E)`,
where `V` is the number of locations and `E` the number of roads.
""")

st.html('<div class="footer">Celerity. Distances are road kilometres in the simulated city network.</div>')