import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import networkx as nx
import matplotlib

matplotlib.use('TkAgg')  # Use TkAgg backend for Matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import math
import os


class GraphVisualizerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Graph Algorithms Visualization")

        # Initially, the graph is undirected
        self.is_directed = False
        self.graph = nx.Graph()
        self.positions = {}  # Stores positions of nodes
        self.add_node_mode = False
        self.add_edge_mode = False
        self.edge_start_node = None
        self.node_list = []

        # Create the main UI components
        self.create_menu()
        self.create_toolbar()
        self.create_canvas()
        self.create_status_bar()

    def create_menu(self):
        # Create a menu bar
        menubar = tk.Menu(self.master)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Graph", command=self.new_graph)
        file_menu.add_command(label="Open Graph...", command=self.open_graph)
        file_menu.add_command(label="Save Graph...", command=self.save_graph)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Algorithms menu
        self.algorithms_menu = tk.Menu(menubar, tearoff=0)
        self.algorithms_menu.add_command(label="Run Dijkstra", command=self.run_dijkstra)
        self.algorithms_menu.add_command(label="Run Bellman-Ford", command=self.run_bellman_ford)
        self.algorithms_menu.add_command(label="Run A*", command=self.run_astar)
        self.algorithms_menu.add_command(label="Run Kruskal", command=self.run_kruskal)
        self.algorithms_menu.add_command(label="Run Prim", command=self.run_prim)
        menubar.add_cascade(label="Algorithms", menu=self.algorithms_menu)

        # Add Directed Algorithms submenu (initially disabled)
        self.directed_algorithms_menu = tk.Menu(self.algorithms_menu, tearoff=0)
        self.directed_algorithms_menu.add_command(label="Run Kosaraju", command=self.run_kosaraju)
        self.directed_algorithms_menu.add_command(label="Run Tarjan", command=self.run_tarjan)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        self.directed_var = tk.BooleanVar()
        view_menu.add_checkbutton(label="Directed Graph", variable=self.directed_var, command=self.toggle_directed)
        menubar.add_cascade(label="View", menu=view_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.master.config(menu=menubar)

    def create_toolbar(self):
        # Create a toolbar frame
        toolbar = tk.Frame(self.master, bd=1, relief=tk.RAISED)

        # Add Node Button with text label
        self.add_node_button = tk.Button(toolbar, text="Add Node", command=self.add_node_mode_on)
        self.add_node_button.pack(side=tk.LEFT, padx=2, pady=2)

        # Add Edge Button with text label
        self.add_edge_button = tk.Button(toolbar, text="Add Edge", command=self.add_edge_mode_on)
        self.add_edge_button.pack(side=tk.LEFT, padx=2, pady=2)

        toolbar.pack(side=tk.TOP, fill=tk.X)

    def create_canvas(self):
        # Create canvas for graph
        self.figure = plt.Figure(figsize=(6, 4))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_axis_on()
        self.ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.figure, self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Connect events
        self.canvas.mpl_connect('button_press_event', self.on_canvas_click)
        self.canvas.mpl_connect('pick_event', self.on_pick)

        # Right-click context menu
        self.canvas.get_tk_widget().bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self.master, tearoff=0)
        self.context_menu.add_command(label="Delete Node", command=self.delete_node)
        self.context_menu.add_command(label="Delete Edge", command=self.delete_edge)

    def create_status_bar(self):
        # Create a status bar
        self.status = tk.StringVar()
        self.status.set("Welcome to Graph Algorithms Visualization!")
        status_bar = tk.Label(self.master, textvariable=self.status, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        self.status.set(message)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def new_graph(self):
        self.graph.clear()
        self.positions.clear()
        self.node_list.clear()
        self.draw_graph()
        self.update_status("New graph created.")

    def open_graph(self):
        file_path = filedialog.askopenfilename(defaultextension=".graphml",
                                               filetypes=[("GraphML files", "*.graphml"), ("All Files", "*.*")])
        if file_path:
            try:
                self.graph = nx.read_graphml(file_path)
                self.positions = nx.spring_layout(self.graph)
                self.node_list = list(self.graph.nodes())
                self.draw_graph()
                self.update_status(f"Graph loaded from {file_path}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load graph: {e}")

    def save_graph(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".graphml",
                                                 filetypes=[("GraphML files", "*.graphml"), ("All Files", "*.*")])
        if file_path:
            try:
                nx.write_graphml(self.graph, file_path)
                self.update_status(f"Graph saved to {file_path}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save graph: {e}")

    def show_about(self):
        messagebox.showinfo("About", "Graph Algorithms Visualization\nDeveloped with Tkinter and NetworkX")

    def toggle_directed(self):
        # Get the current state of the checkbox
        self.is_directed = self.directed_var.get()

        # Reinitialize the graph with the appropriate type
        if self.is_directed:
            self.graph = nx.DiGraph()
            # Add directed algorithms to the menu
            self.algorithms_menu.add_cascade(label="Directed Algorithms", menu=self.directed_algorithms_menu)
            self.update_status("Switched to Directed Graph mode.")
        else:
            self.graph = nx.Graph()
            # Remove directed algorithms from the menu
            self.algorithms_menu.delete("Directed Algorithms")
            self.update_status("Switched to Undirected Graph mode.")

        # Clear existing nodes and edges
        self.positions = {}
        self.node_list = []
        self.edge_start_node = None
        self.add_node_mode = False
        self.add_edge_mode = False

        # Redraw the graph
        self.draw_graph()

    def add_node_mode_on(self):
        self.add_node_mode = True
        self.master.config(cursor="crosshair")
        self.update_status("Click on the canvas to add a node.")

    def add_edge_mode_on(self):
        if len(self.graph.nodes) < 2:
            messagebox.showwarning("Warning", "Need at least two nodes.")
            return
        self.add_edge_mode = True
        self.edge_start_node = None
        self.master.config(cursor="tcross")
        self.update_status("Click on the source node, then the destination node.")

    def on_canvas_click(self, event):
        if event.xdata is None or event.ydata is None:
            return  # Clicked outside the graph area

        if self.add_node_mode:
            # Add node at clicked position
            node_id = len(self.graph.nodes) + 1
            self.graph.add_node(node_id)
            self.positions[node_id] = (event.xdata, event.ydata)
            self.draw_graph()
            self.add_node_mode = False
            self.master.config(cursor="")
            self.update_status(f"Node {node_id} added.")
        elif self.add_edge_mode:
            # Wait for pick_event when clicking on a node
            pass
        else:
            pass  # Can add other functionalities

    def on_pick(self, event):
        if self.add_edge_mode:
            ind = event.ind[0]  # Index of the selected node
            node_id = self.node_list[ind]
            if self.edge_start_node is None:
                # Select starting node
                self.edge_start_node = node_id
                self.update_status(f"Source node {node_id} selected. Now click on the destination node.")
            else:
                # Add edge
                if node_id != self.edge_start_node:
                    # Ask for weight
                    weight = simpledialog.askfloat("Edge Weight", "Enter weight for the edge:", minvalue=0.1)
                    if weight is None:
                        weight = 1.0  # Default weight
                    if self.is_directed:
                        # Add directed edge from start node to current node
                        self.graph.add_edge(self.edge_start_node, node_id, weight=weight)
                        self.update_status(f"Edge added from node {self.edge_start_node} to {node_id}.")
                    else:
                        # Add undirected edge
                        self.graph.add_edge(self.edge_start_node, node_id, weight=weight)
                        self.update_status(f"Edge added between nodes {self.edge_start_node} and {node_id}.")
                    self.draw_graph()
                else:
                    messagebox.showwarning("Warning", "Cannot create an edge from a node to itself.")
                # Reset edge addition state
                self.edge_start_node = None
                self.add_edge_mode = False
                self.master.config(cursor="")
        else:
            pass  # Other modes can be added here

    def draw_graph(self, path=[]):
        self.ax.clear()
        self.ax.set_axis_on()
        self.ax.grid(True)
        self.ax.set_aspect('equal')  # Set aspect ratio to equal

        # Define fixed axis limits (adjust as necessary for your use case)
        fixed_margin = 10  # Adjust to control how much space is visible around the graph
        if not hasattr(self, 'fixed_limits'):
            self.fixed_limits = (-fixed_margin, fixed_margin, -fixed_margin, fixed_margin)

        x_min, x_max, y_min, y_max = self.fixed_limits
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)

        if len(self.graph.nodes) > 0:
            self.node_list = list(self.graph.nodes())
            nodes = nx.draw_networkx_nodes(
                self.graph,
                self.positions,
                nodelist=self.node_list,
                ax=self.ax,
                node_color='skyblue',
                node_size=500
            )
            nodes.set_picker(5)

            # Draw edges
            if self.is_directed:
                nx.draw_networkx_edges(
                    self.graph,
                    self.positions,
                    ax=self.ax,
                    arrows=True,
                    arrowstyle='-|>',
                    arrowsize=12,
                    connectionstyle='arc3,rad=0.1'
                )
            else:
                nx.draw_networkx_edges(
                    self.graph,
                    self.positions,
                    ax=self.ax,
                    arrows=False,
                    connectionstyle='arc3,rad=0.1'
                )

            nx.draw_networkx_labels(self.graph, self.positions, ax=self.ax)

            # Add edge labels (weights)
            edge_labels = nx.get_edge_attributes(self.graph, 'weight')
            nx.draw_networkx_edge_labels(
                self.graph, self.positions, edge_labels=edge_labels, ax=self.ax
            )

            # Highlight path if provided
            if path:
                edge_list = list(zip(path, path[1:]))
                nx.draw_networkx_edges(
                    self.graph,
                    self.positions,
                    edgelist=edge_list,
                    edge_color='r',
                    width=2,
                    ax=self.ax,
                    arrows=self.is_directed,
                    arrowstyle='-|>' if self.is_directed else '-',
                    connectionstyle='arc3,rad=0.1'
                )

        self.canvas.draw()

    def delete_node(self):
        # Implement node deletion functionality
        node_id = simpledialog.askinteger("Delete Node", "Enter node ID to delete:")
        if node_id in self.graph.nodes:
            self.graph.remove_node(node_id)
            self.positions.pop(node_id, None)
            self.draw_graph()
            self.update_status(f"Node {node_id} deleted.")
        else:
            messagebox.showerror("Error", "Node ID not found.")

    def delete_edge(self):
        # Implement edge deletion functionality
        edge = simpledialog.askstring("Delete Edge", "Enter edge to delete in format 'source,target':")
        if edge:
            try:
                source, target = map(int, edge.split(','))
                if self.graph.has_edge(source, target):
                    self.graph.remove_edge(source, target)
                    self.draw_graph()
                    self.update_status(f"Edge from {source} to {target} deleted.")
                else:
                    messagebox.showerror("Error", "Edge not found.")
            except ValueError:
                messagebox.showerror("Error", "Invalid edge format.")

    def run_dijkstra(self):
        if len(self.graph.nodes) < 2:
            messagebox.showwarning("Warning", "Need at least two nodes.")
            return
        source = simpledialog.askinteger("Dijkstra's Algorithm", "Enter source node:")
        target = simpledialog.askinteger("Dijkstra's Algorithm", "Enter target node:")
        if source not in self.graph.nodes or target not in self.graph.nodes:
            messagebox.showerror("Error", "Invalid source or target node.")
            return
        try:
            path = nx.dijkstra_path(self.graph, source=source, target=target, weight='weight')
            self.draw_graph(path=path)
            self.update_status(f"Dijkstra's algorithm: Shortest path from {source} to {target} highlighted.")
        except nx.NetworkXNoPath:
            messagebox.showerror("Error", "No path exists between the nodes.")

    def run_bellman_ford(self):
        if len(self.graph.nodes) < 2:
            messagebox.showwarning("Warning", "Need at least two nodes.")
            return
        source = simpledialog.askinteger("Bellman-Ford Algorithm", "Enter source node:")
        target = simpledialog.askinteger("Bellman-Ford Algorithm", "Enter target node:")
        if source not in self.graph.nodes or target not in self.graph.nodes:
            messagebox.showerror("Error", "Invalid source or target node.")
            return
        try:
            path = nx.bellman_ford_path(self.graph, source=source, target=target, weight='weight')
            self.draw_graph(path=path)
            self.update_status(f"Bellman-Ford algorithm: Shortest path from {source} to {target} highlighted.")
        except nx.NetworkXNoPath:
            messagebox.showerror("Error", "No path exists between the nodes.")

    def heuristic(self, u, v):
        # Heuristic function for A* (Euclidean distance)
        pos_u = self.positions[u]
        pos_v = self.positions[v]
        return math.hypot(pos_u[0] - pos_v[0], pos_u[1] - pos_v[1])

    def run_astar(self):
        if len(self.graph.nodes) < 2:
            messagebox.showwarning("Warning", "Need at least two nodes.")
            return
        source = simpledialog.askinteger("A* Algorithm", "Enter source node:")
        target = simpledialog.askinteger("A* Algorithm", "Enter target node:")
        if source not in self.graph.nodes or target not in self.graph.nodes:
            messagebox.showerror("Error", "Invalid source or target node.")
            return
        try:
            path = nx.astar_path(self.graph, source, target, heuristic=self.heuristic, weight='weight')
            self.draw_graph(path=path)
            self.update_status(f"A* algorithm: Shortest path from {source} to {target} highlighted.")
        except nx.NetworkXNoPath:
            messagebox.showerror("Error", "No path exists between the nodes.")

    def run_kruskal(self):
        if len(self.graph.nodes) < 1:
            messagebox.showwarning("Warning", "Graph is empty.")
            return
        # Convert to undirected graph for MST algorithms if necessary
        if self.is_directed:
            undirected_graph = self.graph.to_undirected()
        else:
            undirected_graph = self.graph.copy()

        mst = nx.minimum_spanning_tree(undirected_graph, algorithm='kruskal', weight='weight')
        self.ax.clear()
        self.ax.set_axis_on()
        self.ax.grid(True)
        nx.draw(
            mst,
            self.positions,
            ax=self.ax,
            with_labels=True,
            node_color='skyblue',
            node_size=500,
            edge_color='g'
        )

        # Add edge labels (weights)
        edge_labels = nx.get_edge_attributes(mst, 'weight')
        nx.draw_networkx_edge_labels(
            mst, self.positions, edge_labels=edge_labels, ax=self.ax
        )

        self.canvas.draw()
        self.update_status("Kruskal's algorithm: Minimum spanning tree displayed.")

    def run_prim(self):
        if len(self.graph.nodes) < 1:
            messagebox.showwarning("Warning", "Graph is empty.")
            return
        # Convert to undirected graph for MST algorithms if necessary
        if self.is_directed:
            undirected_graph = self.graph.to_undirected()
        else:
            undirected_graph = self.graph.copy()

        mst = nx.minimum_spanning_tree(undirected_graph, algorithm='prim', weight='weight')
        self.ax.clear()
        self.ax.set_axis_on()
        self.ax.grid(True)
        nx.draw(
            mst,
            self.positions,
            ax=self.ax,
            with_labels=True,
            node_color='skyblue',
            node_size=500,
            edge_color='g'
        )

        # Add edge labels (weights)
        edge_labels = nx.get_edge_attributes(mst, 'weight')
        nx.draw_networkx_edge_labels(
            mst, self.positions, edge_labels=edge_labels, ax=self.ax
        )

        self.canvas.draw()
        self.update_status("Prim's algorithm: Minimum spanning tree displayed.")

    def run_kosaraju(self):
        if not self.is_directed:
            messagebox.showwarning("Warning", "Kosaraju's algorithm requires a directed graph.")
            return
        scc = list(nx.strongly_connected_components(self.graph))
        self.draw_scc(scc)
        self.update_status("Kosaraju's algorithm: Strongly connected components displayed.")

    def run_tarjan(self):
        if not self.is_directed:
            messagebox.showwarning("Warning", "Tarjan's algorithm requires a directed graph.")
            return
        scc = list(nx.strongly_connected_components(self.graph))
        self.draw_scc(scc)
        self.update_status("Tarjan's algorithm: Strongly connected components displayed.")

    def draw_scc(self, scc):
        self.ax.clear()
        self.ax.set_axis_on()
        self.ax.grid(True)
        colors = plt.cm.tab10.colors  # Use a colormap for coloring SCCs
        for i, component in enumerate(scc):
            nx.draw_networkx_nodes(self.graph, self.positions, nodelist=list(component),
                                   node_color=[colors[i % len(colors)]], node_size=500, ax=self.ax)
        nx.draw_networkx_edges(
            self.graph,
            self.positions,
            ax=self.ax,
            arrows=True,
            arrowstyle='-|>',
            arrowsize=12,
            connectionstyle='arc3,rad=0.1'
        )
        nx.draw_networkx_labels(self.graph, self.positions, ax=self.ax)
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphVisualizerApp(root)
    root.mainloop()
