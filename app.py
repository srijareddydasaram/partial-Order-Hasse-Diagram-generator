import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt


# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="Partial Order & Hasse Diagram Generator",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Partial Order & Hasse Diagram Generator")

st.write(
    "Enter the elements only. "
    "The relation will be generated automatically."
)


# ============================================================
# GENERATE RELATION
# ============================================================

def generate_relation(elements, relation_type):

    relation = set()

    for a in elements:
        for b in elements:

            # Less than or equal to
            if relation_type == "Less than or equal to (≤)":

                if a <= b:
                    relation.add((a, b))

            # Divisibility
            elif relation_type == "Divisibility (|)":

                if a != 0 and b % a == 0:
                    relation.add((a, b))

    return relation


# ============================================================
# CHECK REFLEXIVE
# ============================================================

def is_reflexive(elements, relation):

    for x in elements:

        if (x, x) not in relation:
            return False

    return True


# ============================================================
# CHECK ANTISYMMETRIC
# ============================================================

def is_antisymmetric(relation):

    for a, b in relation:

        if a != b:

            if (b, a) in relation:
                return False

    return True


# ============================================================
# CHECK TRANSITIVE
# ============================================================

def is_transitive(elements, relation):

    for a in elements:

        for b in elements:

            for c in elements:

                if (a, b) in relation and (b, c) in relation:

                    if (a, c) not in relation:
                        return False

    return True


# ============================================================
# FIND HASSE / COVER RELATIONS
# ============================================================

def find_hasse_relations(elements, relation):

    hasse = []

    for a, b in relation:

        # Remove (a,a)
        if a == b:
            continue

        cover = True

        for c in elements:

            if c != a and c != b:

                # If a < c < b,
                # then a,b is not a cover relation
                if (
                    (a, c) in relation
                    and
                    (c, b) in relation
                ):

                    cover = False
                    break

        if cover:

            hasse.append((a, b))

    return sorted(hasse)


# ============================================================
# FIND LEVELS
# ============================================================

def find_levels(elements, hasse):

    graph = nx.DiGraph()

    graph.add_nodes_from(elements)

    graph.add_edges_from(hasse)

    levels = {}

    # --------------------------------------------------------
    # Start with elements having no predecessors
    # --------------------------------------------------------

    remaining = set(elements)

    current_level = 0

    while remaining:

        current_nodes = []

        for node in remaining:

            predecessors = list(
                graph.predecessors(node)
            )

            # Node can be placed in the current level
            # if all its predecessors are already placed
            if all(
                p not in remaining
                for p in predecessors
            ):

                current_nodes.append(node)

        if not current_nodes:
            break

        for node in current_nodes:

            levels[node] = current_level

        remaining -= set(current_nodes)

        current_level += 1

    return graph, levels


# ============================================================
# CREATE STRUCTURED POSITIONS
# ============================================================

def create_positions(elements, hasse):

    graph, levels = find_levels(
        elements,
        hasse
    )

    # --------------------------------------------------------
    # Group nodes by level
    # --------------------------------------------------------

    level_nodes = {}

    for node in elements:

        level = levels[node]

        if level not in level_nodes:

            level_nodes[level] = []

        level_nodes[level].append(node)

    # Sort each level
    for level in level_nodes:

        level_nodes[level] = sorted(
            level_nodes[level]
        )

    # --------------------------------------------------------
    # Create positions
    # --------------------------------------------------------

    positions = {}

    vertical_gap = 3.5
    horizontal_gap = 2.8

    for level in sorted(level_nodes):

        nodes = level_nodes[level]

        count = len(nodes)

        # Total width of current level
        total_width = (
            (count - 1)
            * horizontal_gap
        )

        # Start from left so that
        # the complete level is centered
        start_x = -total_width / 2

        for i, node in enumerate(nodes):

            x = (
                start_x
                + i * horizontal_gap
            )

            # Bottom level has smaller y
            # Higher levels have larger y
            y = level * vertical_gap

            positions[node] = (
                x,
                y
            )

    return graph, levels, level_nodes, positions


# ============================================================
# DRAW HASSE DIAGRAM
# ============================================================

def draw_hasse_diagram(
    elements,
    hasse
):

    (
        graph,
        levels,
        level_nodes,
        positions
    ) = create_positions(
        elements,
        hasse
    )

    # --------------------------------------------------------
    # Figure size
    # --------------------------------------------------------

    maximum_nodes = max(
        len(nodes)
        for nodes in level_nodes.values()
    )

    number_of_levels = len(
        level_nodes
    )

    figure_width = max(
        6,
        maximum_nodes * 2.5
    )

    figure_height = max(
        6,
        number_of_levels * 2
    )

    fig, ax = plt.subplots(
        figsize=(
            figure_width,
            figure_height
        )
    )

    # --------------------------------------------------------
    # DRAW EDGES
    # --------------------------------------------------------

    nx.draw_networkx_edges(
        graph,
        positions,
        ax=ax,
        arrows=False,
        width=2
    )

    # --------------------------------------------------------
    # DRAW NODES
    # --------------------------------------------------------

    nx.draw_networkx_nodes(
        graph,
        positions,
        ax=ax,
        node_size=1700,
        node_color="white",
        edgecolors="black",
        linewidths=2
    )

    # --------------------------------------------------------
    # DRAW LABELS
    # --------------------------------------------------------

    nx.draw_networkx_labels(
        graph,
        positions,
        ax=ax,
        font_size=14,
        font_weight="bold"
    )

    # --------------------------------------------------------
    # REMOVE AXIS
    # --------------------------------------------------------

    ax.axis("off")

    # Important:
    # Do NOT invert the y-axis.
    # Therefore smallest elements remain at bottom
    # and larger elements appear above.

    plt.tight_layout()

    return fig, levels


# ============================================================
# INPUT
# ============================================================

st.header("1. Enter Elements")

elements_input = st.text_input(
    "Enter elements separated by commas",
    placeholder="Example: 1,2,3,4,6,12"
)


# ============================================================
# SELECT RELATION
# ============================================================

st.header("2. Select Relation")

relation_type = st.selectbox(
    "Choose relation",
    [
        "Less than or equal to (≤)",
        "Divisibility (|)"
    ]
)


# ============================================================
# GENERATE BUTTON
# ============================================================

if st.button(
    "🔍 GENERATE HASSE DIAGRAM",
    type="primary"
):

    # ========================================================
    # READ ELEMENTS
    # ========================================================

    if elements_input.strip() == "":

        st.error(
            "❌ Please enter elements."
        )

        st.stop()

    try:

        elements = [
            int(x.strip())
            for x in elements_input.split(",")
            if x.strip()
        ]

    except ValueError:

        st.error(
            "❌ Invalid input. "
            "Enter elements like 1,2,3,4"
        )

        st.stop()


    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    elements = list(
        dict.fromkeys(elements)
    )


    # ========================================================
    # CHECK MINIMUM ELEMENTS
    # ========================================================

    if len(elements) < 2:

        st.error(
            "❌ Please enter at least two elements."
        )

        st.stop()


    # ========================================================
    # GENERATE RELATION
    # ========================================================

    relation = generate_relation(
        elements,
        relation_type
    )


    # ========================================================
    # GENERATED RELATION
    # ========================================================

    st.header(
        "3. Generated Relation"
    )

    relation_text = ""

    for a, b in sorted(relation):

        relation_text += (
            f"({a}, {b})\n"
        )

    st.code(
        relation_text
    )


    # ========================================================
    # CHECK PARTIAL ORDER PROPERTIES
    # ========================================================

    reflexive = is_reflexive(
        elements,
        relation
    )

    antisymmetric = is_antisymmetric(
        relation
    )

    transitive = is_transitive(
        elements,
        relation
    )


    # ========================================================
    # DISPLAY PROPERTIES
    # ========================================================

    st.header(
        "4. Partial Order Validation"
    )

    if reflexive:

        st.success(
            "✅ Reflexive"
        )

    else:

        st.error(
            "❌ Not Reflexive"
        )


    if antisymmetric:

        st.success(
            "✅ Antisymmetric"
        )

    else:

        st.error(
            "❌ Not Antisymmetric"
        )


    if transitive:

        st.success(
            "✅ Transitive"
        )

    else:

        st.error(
            "❌ Not Transitive"
        )


    # ========================================================
    # VALID PARTIAL ORDER
    # ========================================================

    if not (
        reflexive
        and antisymmetric
        and transitive
    ):

        st.error(
            "❌ The relation is NOT a partial order."
        )

        st.stop()


    st.success(
        "🎉 The relation is a VALID PARTIAL ORDER!"
    )


    # ========================================================
    # HASSE RELATIONS
    # ========================================================

    hasse = find_hasse_relations(
        elements,
        relation
    )


    # ========================================================
    # DISPLAY HASSE RELATIONS
    # ========================================================

    st.header(
        "5. Hasse / Cover Relations"
    )

    if len(hasse) == 0:

        st.write(
            "No cover relations found."
        )

    else:

        for a, b in hasse:

            st.write(
                f"({a}, {b})"
            )


    # ========================================================
    # CREATE DIAGRAM
    # ========================================================

    fig, levels = draw_hasse_diagram(
        elements,
        hasse
    )


    # ========================================================
    # LEVEL-BY-LEVEL STRUCTURE
    # ========================================================

    st.header(
        "6. Level-by-Level Structure"
    )

    max_level = max(
        levels.values()
    )

    for level in range(
        max_level + 1
    ):

        nodes = sorted(
            [
                node
                for node in elements
                if levels[node] == level
            ]
        )

        st.write(
            f"**Level {level + 1}:** "
            + ", ".join(
                str(node)
                for node in nodes
            )
        )


    # ========================================================
    # HASSЕ DIAGRAM
    # ========================================================

    st.header(
        "7. Hasse Diagram"
    )

    # ========================================================
    # IMPORTANT:
    # THIS IS THE ONLY st.pyplot()
    # ========================================================

    st.pyplot(
        fig,
        use_container_width=False
    )