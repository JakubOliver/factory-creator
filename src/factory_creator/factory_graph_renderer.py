import matplotlib.pyplot as plt
import networkx


class FactoryGraphRenderer:
    @staticmethod
    def draw_graph(graph) -> None:
        graph_layout = networkx.nx_pydot.graphviz_layout(graph, prog="dot")
        networkx.draw(graph, graph_layout, with_labels=False)

        node_labels = networkx.get_node_attributes(graph, "label")
        networkx.draw_networkx_labels(graph, graph_layout, node_labels)

        edge_labels = networkx.get_edge_attributes(graph, "label")
        networkx.draw_networkx_edge_labels(graph, graph_layout, edge_labels=edge_labels)

    @staticmethod
    def show_graph(graph) -> None:
        FactoryGraphRenderer.draw_graph(graph)
        plt.show()

    @staticmethod
    def export_graph(
        graph,
        png_path: str = "output/tree.png",
        svg_path: str = "output/tree.svg"
    ) -> tuple[str, str]:
        pydot_graph = networkx.drawing.nx_pydot.to_pydot(graph)
        pydot_graph.write_png(png_path)
        pydot_graph.write_svg(svg_path)

        return png_path, svg_path
