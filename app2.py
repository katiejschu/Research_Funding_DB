# app.py

import streamlit as st
from pyvis.network import Network
from neo4j_conn import run_cypher
import pandas as pd

st.set_page_config(page_title="Research Funding Graph Explorer", layout="wide")

st.title("Minnesota Research Funding Graph Explorer (Prototype)")
st.markdown(
    """
This is a **prototype** Streamlit app connected to Neo4j. 

Use the sidebar to choose different views of the Minnesota research funding ecosystem:
- Top PIs by number of grants
- Cancer-related grants and where they are held
- Full ecosystem with Frascati-themed research themes
- PIs with grants at multiple organizations
- Grants held at Minnesota State University, Mankato
"""
)

# ---------------- Sidebar controls ----------------

st.sidebar.header("Exploration options")

view = st.sidebar.radio(
    "Choose a view",
    [
        "Top 10 PIs by Grants Led",
        "Cancer-related PI–Org network",
        "Full ecosystem (with Frascati-themed ResearchThemes)",
        "PIs with multi-organization portfolios",
        "MSU Mankato grant ecosystem",
    ],
)

max_rows = st.sidebar.slider(
    "Max rows for graph views",
    min_value=20,
    max_value=500,
    value=100,
    step=20,
    help="Upper bound on Cypher rows for network visualizations.",
)


# ---------------- Helpers ----------------

def add_node(nodes, node_id, label, group):
    if node_id is None:
        return
    if node_id not in nodes:
        nodes[node_id] = {
            "id": node_id,
            "label": label or group,
            "group": group,
        }


def build_and_render_network(nodes, edges, title: str):
    """
    nodes: dict[node_id] = {"id": id, "label": label, "group": group}
    edges: list[(src_id, dst_id)]
    """
    if not nodes:
        st.warning("No nodes to display for this query.")
        return

    net = Network(
        height="700px",
        width="100%",
        bgcolor="#FFFFFF",
        font_color="#000000",
        directed=False,
    )

    net.barnes_hut()

    group_colors = {
        "pi": "#3A7CA5",
        "grant": "#F4A259",
        "org": "#5B8E7D",
        "funder": "#D1495B",
        "system": "#735D78",
        "theme": "#F6AE2D",
    }

    for node in nodes.values():
        color = group_colors.get(node["group"], "#999999")
        net.add_node(
            node["id"],
            label=node["label"],
            color=color,
            title=f"{node['group'].title()}: {node['label']}",
        )

    for src, dst in edges:
        net.add_edge(src, dst)

    # IMPORTANT: valid JSON only (no "var options =")
    net.set_options(
        """
        {
          "nodes": {
            "shape": "dot",
            "scaling": {
              "min": 5,
              "max": 20
            }
          },
          "physics": {
            "stabilization": true,
            "barnesHut": {
              "gravitationalConstant": -20000,
              "springLength": 150
            }
          },
          "interaction": {
            "hover": true,
            "dragNodes": true,
            "zoomView": true
          }
        }
        """
    )

    net.save_graph("graph.html")
    with open("graph.html", "r", encoding="utf-8") as f:
        html = f.read()

    st.subheader(title)
    st.caption("You can drag nodes, zoom, and hover for details.")
    st.components.v1.html(html, height=700, scrolling=True)


# ---------------- View 1: Top 10 PIs by Grants Led ----------------

if view == "Top 10 PIs by Grants Led":
    st.markdown(
        """
**View:** Top Principal Investigators ranked by number of grants they lead.
"""
    )

    query = """
    MATCH (pi:PrincipalInvestigator)<-[:LED_BY]-(g:Grant)
    RETURN pi.name AS pi_name, COUNT(g) AS grants_led
    ORDER BY grants_led DESC
    LIMIT 10
    """

    rows = run_cypher(query, {})

    if not rows:
        st.warning("No data returned for this query.")
    else:
        st.success(f"Loaded {len(rows)} rows.")

        df = pd.DataFrame(rows)
        st.dataframe(df)

        st.bar_chart(df, x="pi_name", y="grants_led")


# ---------------- View 2: Cancer-related PI–Org network ----------------

elif view == "Cancer-related PI–Org network":
    st.markdown(
        """
**View:** Cancer-related grants and where they are held,
showing PIs, grants, and organizations.
"""
    )

    query = f"""
    MATCH (pi:PrincipalInvestigator)<-[:LED_BY]-(g:Grant)-[:HELD_AT]->(o:Organization)
    WHERE toLower(g.Title) CONTAINS 'cancer'
    RETURN DISTINCT
        id(pi) AS pi_id,
        pi.name AS pi_name,
        id(g) AS grant_id,
        g.Title AS grant_title,
        id(o) AS org_id,
        o.name AS org_name
    LIMIT {max_rows}
    """

    rows = run_cypher(query, {})

    if not rows:
        st.warning("No cancer-related grants found with this pattern.")
    else:
        st.success(f"Loaded {len(rows)} PI–grant–org rows.")

        nodes = {}
        edges = []

        for r in rows:
            pi_id = r["pi_id"]
            pi_name = r["pi_name"]
            grant_id = r["grant_id"]
            grant_title = r["grant_title"]
            org_id = r["org_id"]
            org_name = r["org_name"]

            add_node(nodes, pi_id, pi_name, "pi")
            add_node(nodes, grant_id, grant_title, "grant")
            add_node(nodes, org_id, org_name, "org")

            edges.append((pi_id, grant_id))
            edges.append((grant_id, org_id))

        build_and_render_network(
            nodes,
            edges,
            "Cancer-related PI–Organization network",
        )


# ---------------- View 3: Full ecosystem with Frascati-themed ResearchThemes ----------------

elif view == "Full ecosystem (with Frascati-themed ResearchThemes)":
    st.markdown(
        """
**View:** Funding agencies, grants, PIs, organizations, institution systems,
and research themes (filtered to themes with `Frascati_theme` when present).
"""
    )

    query = f"""
    MATCH (fa:FundingAgency)<-[funded:FUNDED_BY]-(g:Grant)
    OPTIONAL MATCH (g)-[:LED_BY]->(pi:PrincipalInvestigator)
    OPTIONAL MATCH (g)-[:HELD_AT]->(o:Organization)
    OPTIONAL MATCH (o)-[:PART_OF]->(sys:InstitutionSystem)
    OPTIONAL MATCH (g)-[:ADDRESSES]->(rt:ResearchTheme)
    WHERE rt IS NULL OR rt.Frascati_theme IS NOT NULL
    RETURN DISTINCT
      id(fa) AS funder_id, fa.name AS funder_name,
      id(g) AS grant_id, g.Title AS grant_title,
      id(pi) AS pi_id, pi.name AS pi_name,
      id(o) AS org_id, o.name AS org_name,
      id(sys) AS system_id, sys.name AS system_name,
      id(rt) AS theme_id, rt.name AS theme_name,
      rt.Frascati_theme AS frascati_theme
    LIMIT {max_rows}
    """

    rows = run_cypher(query, {})

    if not rows:
        st.warning("No ecosystem data returned.")
    else:
        st.success(f"Loaded {len(rows)} ecosystem rows.")

        nodes = {}
        edges = []

        for r in rows:
            funder_id = r["funder_id"]
            funder_name = r["funder_name"]
            grant_id = r["grant_id"]
            grant_title = r["grant_title"]
            pi_id = r["pi_id"]
            pi_name = r["pi_name"]
            org_id = r["org_id"]
            org_name = r["org_name"]
            system_id = r["system_id"]
            system_name = r["system_name"]
            theme_id = r["theme_id"]
            theme_name = r["theme_name"]
            frascati_theme = r["frascati_theme"]

            add_node(nodes, funder_id, funder_name, "funder")
            add_node(nodes, grant_id, grant_title, "grant")
            add_node(nodes, pi_id, pi_name, "pi")
            add_node(nodes, org_id, org_name, "org")
            add_node(nodes, system_id, system_name, "system")

            if theme_id is not None:
                label = theme_name or frascati_theme or "Theme"
                add_node(nodes, theme_id, label, "theme")

            if funder_id is not None and grant_id is not None:
                edges.append((funder_id, grant_id))
            if pi_id is not None and grant_id is not None:
                edges.append((pi_id, grant_id))
            if org_id is not None and grant_id is not None:
                edges.append((grant_id, org_id))
            if system_id is not None and org_id is not None:
                edges.append((org_id, system_id))
            if theme_id is not None and grant_id is not None:
                edges.append((grant_id, theme_id))

        build_and_render_network(
            nodes,
            edges,
            "Full funding ecosystem with Frascati-themed ResearchThemes",
        )


# ---------------- View 4: PIs with multi-organization portfolios ----------------

elif view == "PIs with multi-organization portfolios":
    st.markdown(
        """
**View:** Principal Investigators who lead grants held at **more than one organization**.
"""
    )

    query = f"""
    MATCH (pi:PrincipalInvestigator)<-[:LED_BY]-(g:Grant)-[:HELD_AT]->(o:Organization)
    WITH pi, COLLECT(DISTINCT o) AS orgs
    WHERE SIZE(orgs) > 1
    UNWIND orgs AS o
    MATCH (pi)<-[:LED_BY]-(g:Grant)-[:HELD_AT]->(o)
    RETURN DISTINCT
        id(pi) AS pi_id, pi.name AS pi_name,
        id(g) AS grant_id, g.Title AS grant_title,
        id(o) AS org_id, o.name AS org_name
    LIMIT {max_rows}
    """

    rows = run_cypher(query, {})

    if not rows:
        st.warning("No PIs found with grants at multiple organizations.")
    else:
        st.success(f"Loaded {len(rows)} PI–grant–org rows.")

        nodes = {}
        edges = []

        for r in rows:
            pi_id = r["pi_id"]
            pi_name = r["pi_name"]
            grant_id = r["grant_id"]
            grant_title = r["grant_title"]
            org_id = r["org_id"]
            org_name = r["org_name"]

            add_node(nodes, pi_id, pi_name, "pi")
            add_node(nodes, grant_id, grant_title, "grant")
            add_node(nodes, org_id, org_name, "org")

            edges.append((pi_id, grant_id))
            edges.append((grant_id, org_id))

        build_and_render_network(
            nodes,
            edges,
            "PIs with multi-organization grant portfolios",
        )


# ---------------- View 5: MSU Mankato grant ecosystem ----------------

elif view == "MSU Mankato grant ecosystem":
    st.markdown(
        """
**View:** Grants held at **Minnesota State University, Mankato**, showing PIs and funders.
"""
    )

    query = f"""
    MATCH (pi:PrincipalInvestigator)<-[:LED_BY]-(g:Grant)-[:FUNDED_BY]->(fa:FundingAgency),
          (g)-[:HELD_AT]->(o:Organization {{name: "Minnesota State University, Mankato"}})
    RETURN DISTINCT
        id(pi) AS pi_id, pi.name AS pi_name,
        id(g) AS grant_id, g.Title AS grant_title,
        id(fa) AS funder_id, fa.name AS funder_name,
        id(o) AS org_id, o.name AS org_name
    LIMIT {max_rows}
    """

    rows = run_cypher(query, {})

    if not rows:
        st.warning("No MSU Mankato–held grants found.")
    else:
        st.success(f"Loaded {len(rows)} PI–grant–funder rows for MSU Mankato.")

        nodes = {}
        edges = []

        for r in rows:
            pi_id = r["pi_id"]
            pi_name = r["pi_name"]
            grant_id = r["grant_id"]
            grant_title = r["grant_title"]
            funder_id = r["funder_id"]
            funder_name = r["funder_name"]
            org_id = r["org_id"]
            org_name = r["org_name"]

            add_node(nodes, pi_id, pi_name, "pi")
            add_node(nodes, grant_id, grant_title, "grant")
            add_node(nodes, funder_id, funder_name, "funder")
            add_node(nodes, org_id, org_name, "org")

            edges.append((pi_id, grant_id))
            edges.append((grant_id, funder_id))
            edges.append((grant_id, org_id))

        build_and_render_network(
            nodes,
            edges,
            "MSU Mankato grant ecosystem (PIs, grants, funders)",
        )


