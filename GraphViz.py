import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import networkx as nx
import matplotlib
import time 
import math
import os

matplotlib.use('TkAgg')  # Use TkAgg backend for Matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


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
        self.node_canvas_ids = {}
        self.create_pseudocode_area()
        self.create_stack_area()
        self.create_details_area()

        #stepping
        self.algorithm_steps = []  # Stores the steps for an algorithm
        self.current_step_index = -1  # Current step index

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
        self.algorithms_menu.add_command(label="Run Kosaraju", command=self.run_kosaraju)
        self.algorithms_menu.add_command(label="Run Tarjan", command=self.run_tarjan)
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
        toolbar = tk.Frame(self.master, bd=1, relief=tk.RAISED)

        self.add_node_button = tk.Button(toolbar, text="Add Node", command=self.add_node_mode_on)
        self.add_node_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.add_edge_button = tk.Button(toolbar, text="Add Edge", command=self.add_edge_mode_on)
        self.add_edge_button.pack(side=tk.LEFT, padx=2, pady=2)

        # Step buttons
        self.prev_step_button = tk.Button(toolbar, text="Previous Step", command=self.prev_step, state=tk.DISABLED)
        self.prev_step_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.next_step_button = tk.Button(toolbar, text="Next Step", command=self.next_step, state=tk.DISABLED)
        self.next_step_button.pack(side=tk.LEFT, padx=2, pady=2)

        toolbar.pack(side=tk.TOP, fill=tk.X)

    def animate_transition(self, old_step, new_step, frames=10, delay=50):
        """
        Animates transition between steps.
        """
        def update_frame(frame):
            frac = frame / frames
            self.ax.clear()
            self.ax.set_axis_on()
            self.ax.grid(True)
            # Draw base graph
            nx.draw_networkx_nodes(self.graph, self.positions, ax=self.ax, node_color='skyblue', node_size=500)
            nx.draw_networkx_edges(self.graph, self.positions, ax=self.ax, edge_color='black', width=1)
            nx.draw_networkx_labels(self.graph, self.positions, ax=self.ax)
            # Highlight edges from new step with increasing width
            new_edges = new_step.get('edges', [])
            if new_edges:
                interpolated_width = 1 + 3 * frac
                nx.draw_networkx_edges(
                    self.graph, self.positions, 
                    ax=self.ax, 
                    edgelist=new_edges, 
                    edge_color='red', 
                    width=interpolated_width
                )
            self.canvas.draw()
            if frame < frames:
                self.master.after(delay, lambda: update_frame(frame + 1))
            else:
                self.draw_graph_with_step(new_step)
        update_frame(0)

    def next_step(self):
        if self.current_step_index + 1 < len(self.algorithm_steps):
            old_step = self.algorithm_steps[self.current_step_index] if self.current_step_index >= 0 else {}
            self.current_step_index += 1
            new_step = self.algorithm_steps[self.current_step_index]
            self.animate_transition(old_step, new_step)
            self.update_status(f"Step {self.current_step_index + 1}/{len(self.algorithm_steps)}")
            self.prev_step_button.config(state=tk.NORMAL)
            if self.current_step_index + 1 == len(self.algorithm_steps):
                self.next_step_button.config(state=tk.DISABLED)
        else:
            self.update_status("No more steps forward.")

    def prev_step(self):
        if self.current_step_index > 0:
            old_step = self.algorithm_steps[self.current_step_index]
            self.current_step_index -= 1
            new_step = self.algorithm_steps[self.current_step_index]
            self.animate_transition(old_step, new_step)
            self.update_status(f"Step {self.current_step_index + 1}/{len(self.algorithm_steps)}")
            self.next_step_button.config(state=tk.NORMAL)
            if self.current_step_index == 0:
                self.prev_step_button.config(state=tk.DISABLED)
        else:
            self.update_status("No more steps backward.")

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

    def save_graph(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                adjacency_matrix = nx.adjacency_matrix(self.graph).todense()
                with open(file_path, 'w') as file:
                    for node in self.graph.nodes():
                        pos = self.positions[node]
                        file.write(f"{node} {pos[0]} {pos[1]}\n")
                    file.write("MATRIX\n")
                    for row in adjacency_matrix.tolist():
                        file.write(" ".join(map(str, row)) + "\n")
                self.update_status(f"Graph with positions saved to {file_path}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save graph: {e}")

    def open_graph(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt",
                                           filetypes=[("Text files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    separator_index = lines.index("MATRIX\n")
                    self.graph.clear()
                    self.positions.clear()
                    for line in lines[:separator_index]:
                        node, x, y = line.strip().split()
                        self.graph.add_node(int(node))
                        self.positions[int(node)] = (float(x), float(y))
                    adjacency_matrix = [list(map(float, line.strip().split())) for line in lines[separator_index + 1:]]
                    nodes = list(self.graph.nodes())
                    for i, row in enumerate(adjacency_matrix):
                        for j, weight in enumerate(row):
                            if weight != 0:
                                self.graph.add_edge(nodes[i], nodes[j], weight=weight)
                self.draw_graph()
                self.update_status(f"Graph with positions loaded from {file_path}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load graph: {e}")

    def show_about(self):
        messagebox.showinfo("About", "Graph Algorithms Visualization\nDeveloped with Tkinter and NetworkX")

    def toggle_directed(self):
        self.is_directed = self.directed_var.get()
        if self.is_directed:
            self.graph = nx.DiGraph()
            self.algorithms_menu.add_cascade(label="Directed Algorithms", menu=self.directed_algorithms_menu)
            self.update_status("Switched to Directed Graph mode.")
        else:
            self.graph = nx.Graph()
            self.algorithms_menu.delete("Directed Algorithms")
            self.update_status("Switched to Undirected Graph mode.")
        self.positions = {}
        self.node_list = []
        self.edge_start_node = None
        self.add_node_mode = False
        self.add_edge_mode = False
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
            return
        if self.add_node_mode:
            node_id = len(self.graph.nodes) + 1
            self.graph.add_node(node_id)
            self.positions[node_id] = (event.xdata, event.ydata)
            self.draw_graph()
            self.add_node_mode = False
            self.master.config(cursor="")
            self.update_status(f"Node {node_id} added.")
        elif self.add_edge_mode:
            pass
        else:
            pass

    def on_pick(self, event):
        if self.add_edge_mode:
            ind = event.ind[0]
            node_id = self.node_list[ind]
            if self.edge_start_node is None:
                self.edge_start_node = node_id
                self.update_status(f"Source node {node_id} selected. Now click on the destination node.")
            else:
                if node_id != self.edge_start_node:
                    weight = simpledialog.askfloat("Edge Weight", "Enter weight for the edge:", minvalue=0.1)
                    if weight is None:
                        weight = 1.0
                    if self.is_directed:
                        self.graph.add_edge(self.edge_start_node, node_id, weight=weight)
                        self.update_status(f"Edge added from node {self.edge_start_node} to {node_id}.")
                    else:
                        self.graph.add_edge(self.edge_start_node, node_id, weight=weight)
                        self.update_status(f"Edge added between nodes {self.edge_start_node} and {node_id}.")
                    self.draw_graph()
                else:
                    messagebox.showwarning("Warning", "Cannot create an edge from a node to itself.")
                self.edge_start_node = None
                self.add_edge_mode = False
                self.master.config(cursor="")
        else:
            pass

    def draw_graph_with_step(self, step):
        self.ax.clear()
        self.ax.set_axis_on()
        self.ax.grid(True)
        # Draw all nodes and edges in default style
        nx.draw_networkx_nodes(self.graph, self.positions, ax=self.ax, node_color='skyblue', node_size=500)
        nx.draw_networkx_edges(self.graph, self.positions, ax=self.ax, edge_color='black', width=1)
        # Highlight nodes if specified in the step
        highlight = step.get('highlight', [])
        if highlight:
            nx.draw_networkx_nodes(self.graph, self.positions, nodelist=highlight, ax=self.ax, node_color='yellow', node_size=500)
        step_edges = step.get('edges', [])
        if step_edges:
            nx.draw_networkx_edges(self.graph, self.positions, ax=self.ax, edgelist=step_edges, edge_color='r', width=2)
        nx.draw_networkx_labels(self.graph, self.positions, ax=self.ax)
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, self.positions, edge_labels=edge_labels, ax=self.ax)
        self.update_stack_display(step.get('stack', []))
        self.update_details_display(step.get('details', []))
        self.canvas.draw()

    def create_details_area(self):
        details_frame = tk.Frame(self.master)
        details_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        details_label = tk.Label(details_frame, text="Step Details", font=("Arial", 12, "bold"))
        details_label.pack()
        self.details_text = tk.Text(details_frame, wrap=tk.WORD, height=20, width=40)
        self.details_text.pack(fill=tk.Y, padx=5, pady=5)
        self.details_text.config(state=tk.DISABLED)

    def update_details_display(self, details):
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        for line in details:
            self.details_text.insert(tk.END, line + "\n")
        self.details_text.config(state=tk.DISABLED)

    def create_stack_area(self):
        stack_frame = tk.Frame(self.master)
        stack_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        stack_label = tk.Label(stack_frame, text="Stack Visualization", font=("Arial", 12, "bold"))
        stack_label.pack()
        self.stack_listbox = tk.Listbox(stack_frame, height=20, width=35)
        self.stack_listbox.pack(fill=tk.Y, padx=5, pady=5)

    def update_stack_display(self, stack):
        self.stack_listbox.delete(0, tk.END)
        for item in stack:
            if isinstance(item, tuple):
                if len(item) == 3:
                    weight, u, v = item
                    self.stack_listbox.insert(tk.END, f"Edge: ({u} -> {v}), Weight: {weight}")
                elif len(item) == 2:
                    distance, node = item
                    self.stack_listbox.insert(tk.END, f"Node: {node}, Distance: {distance}")
                else:
                    self.stack_listbox.insert(tk.END, f"Tuple: {item}")
            elif isinstance(item, int):
                self.stack_listbox.insert(tk.END, f"Node: {item}")
            elif isinstance(item, list):
                self.stack_listbox.insert(tk.END, f"Group: {item}")
            else:
                self.stack_listbox.insert(tk.END, f"Unknown: {item}")

    def delete_node(self):
        node_id = simpledialog.askinteger("Delete Node", "Enter node ID to delete:")
        if node_id in self.graph.nodes:
            self.graph.remove_node(node_id)
            self.positions.pop(node_id, None)
            self.draw_graph()
            self.update_status(f"Node {node_id} deleted.")
        else:
            messagebox.showerror("Error", "Node ID not found.")

    def delete_edge(self):
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

    def draw_graph(self, path=[]):
        self.ax.clear()
        self.ax.set_axis_on()
        self.ax.grid(True)
        self.ax.set_aspect('equal')
        fixed_margin = 10
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
            edge_labels = nx.get_edge_attributes(self.graph, 'weight')
            nx.draw_networkx_edge_labels(
                self.graph, self.positions, edge_labels=edge_labels, ax=self.ax
            )
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

    def run_dijkstra(self):
        pseudocode = """Dijkstra's Algorithm:
1. Initialize distances to infinity, source distance = 0
2. Add source node to the priority queue
3. While the queue is not empty:
    a. Extract the node with the smallest distance
    b. For each neighbor:
        i. If new distance < current distance:
            Update distance
            Add neighbor to the queue
4. Return shortest path
"""
        self.display_pseudocode(pseudocode)

        source = simpledialog.askinteger("Dijkstra's Algorithm", "Enter source node:")
        target = simpledialog.askinteger("Dijkstra's Algorithm", "Enter target node:")
        if source not in self.graph.nodes or target not in self.graph.nodes:
            messagebox.showerror("Error", "Invalid source or target node.")
            return
        
        try:
            self.draw_graph()
            self.algorithm_steps = []
            distances = {node: float('inf') for node in self.graph.nodes}
            distances[source] = 0
            priority_queue = [(0, source)]
            visited = set()

            while priority_queue:
                priority_queue.sort()
                current_distance, current_node = priority_queue.pop(0)
                if current_node in visited:
                    continue
                visited.add(current_node)

                step_details = []
                step_edges = []

                for neighbor in self.graph.neighbors(current_node):
                    weight = self.graph[current_node][neighbor].get('weight', 1)
                    new_distance = current_distance + weight
                    step_details.append(f"Considering edge ({current_node} -> {neighbor}) with weight {weight}")
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        priority_queue.append((new_distance, neighbor))
                        step_details.append(f"Updated distance of node {neighbor} to {new_distance}")
                        step_edges.append((current_node, neighbor))
                    else:
                        step_details.append(f"Distance of node {neighbor} remains {distances[neighbor]}")

                self.algorithm_steps.append({
                    'edges': step_edges,
                    'stack': priority_queue.copy(),
                    'details': step_details
                })

            path = nx.dijkstra_path(self.graph, source=source, target=target, weight='weight')
            path_edges = list(zip(path, path[1:]))
            self.algorithm_steps.append({'edges': path_edges, 'stack': [], 'details': ["Final shortest path highlighted"]})
            self.current_step_index = -1
            self.next_step_button.config(state=tk.NORMAL)
            self.prev_step_button.config(state=tk.DISABLED)
            self.update_status("Dijkstra's algorithm ready for step-by-step visualization.")
        except nx.NetworkXNoPath:
            messagebox.showerror("Error", "No path exists between the nodes.")

    def run_bellman_ford(self):
        pseudocode = """Bellman-Ford Algorithm:
1. Initialize distances to infinity, source distance = 0
2. For |V|-1 iterations:
    a. For each edge (u, v):
        i. If distance[u] + weight < distance[v]:
            Update distance[v]
3. Check for negative-weight cycles:
    a. For each edge (u, v):
        i. If distance[u] + weight < distance[v]:
            Negative cycle detected
"""
        self.display_pseudocode(pseudocode)

        source = simpledialog.askinteger("Bellman-Ford Algorithm", "Enter source node:")
        target = simpledialog.askinteger("Bellman-Ford Algorithm", "Enter target node:")
        if source not in self.graph.nodes or target not in self.graph.nodes:
            messagebox.showerror("Error", "Invalid source or target node.")
            return

        try:
            self.draw_graph()
            self.algorithm_steps = []
            distances = {node: float('inf') for node in self.graph.nodes}
            distances[source] = 0
            edges = list(self.graph.edges(data=True))

            for iteration in range(len(self.graph.nodes) - 1):
                step_details = [f"Iteration {iteration + 1}:"]
                step_edges = []
                for u, v, data in edges:
                    weight = data.get('weight', 1)
                    step_details.append(f"Considering edge ({u} -> {v}) with weight {weight}")
                    if distances[u] + weight < distances[v]:
                        distances[v] = distances[u] + weight
                        step_details.append(f"Updated distance of node {v} to {distances[v]}")
                        step_edges.append((u, v))
                    else:
                        step_details.append(f"No update for node {v}, current distance: {distances[v]}")

                self.algorithm_steps.append({
                    'edges': step_edges,
                    'stack': edges.copy(),
                    'details': step_details
                })

            step_details = ["Checking for negative-weight cycles:"]
            for u, v, data in edges:
                weight = data.get('weight', 1)
                if distances[u] + weight < distances[v]:
                    step_details.append(f"Negative cycle detected due to edge ({u} -> {v})")
                    break
            else:
                step_details.append("No negative-weight cycles detected.")

            self.algorithm_steps.append({'edges': [], 'stack': [], 'details': step_details})
            path = nx.bellman_ford_path(self.graph, source=source, target=target, weight='weight')
            path_edges = list(zip(path, path[1:]))
            self.algorithm_steps.append({'edges': path_edges, 'stack': [], 'details': ["Final shortest path highlighted"]})
            self.current_step_index = -1
            self.next_step_button.config(state=tk.NORMAL)
            self.prev_step_button.config(state=tk.DISABLED)
            self.update_status("Bellman-Ford algorithm ready for step-by-step visualization.")
        except nx.NetworkXNoPath:
            messagebox.showerror("Error", "No path exists between the nodes.")

    def run_astar(self):
        pseudocode = """A* Algorithm:
1. Initialize distances and heuristic scores (f = g + h)
2. Add the source node to the open list
3. While the open list is not empty:
    a. Extract the node with the smallest f value
    b. If the node is the target, return the path
    c. For each neighbor:
        i. If g(neighbor) > g(current) + edge_weight:
            Update g(neighbor), f(neighbor)
            Add neighbor to the open list
"""
        self.display_pseudocode(pseudocode)

        source = simpledialog.askinteger("A* Algorithm", "Enter source node:")
        target = simpledialog.askinteger("A* Algorithm", "Enter target node:")
        if source not in self.graph.nodes or target not in self.graph.nodes:
            messagebox.showerror("Error", "Invalid source or target node.")
            return

        try:
            self.draw_graph()
            self.algorithm_steps = []
            open_list = [(0, source)]
            g_scores = {node: float('inf') for node in self.graph.nodes}
            g_scores[source] = 0
            f_scores = {node: float('inf') for node in self.graph.nodes}
            f_scores[source] = self.heuristic(source, target)

            while open_list:
                open_list.sort()
                _, current = open_list.pop(0)
                step_details = [f"Processing node {current} with f_score {f_scores[current]}"]
                step_edges = []

                if current == target:
                    step_details.append("Target node reached.")
                    break

                for neighbor in self.graph.neighbors(current):
                    weight = self.graph[current][neighbor].get('weight', 1)
                    tentative_g = g_scores[current] + weight
                    step_details.append(f"Considering edge ({current} -> {neighbor}) with weight {weight}")
                    if tentative_g < g_scores[neighbor]:
                        g_scores[neighbor] = tentative_g
                        f_scores[neighbor] = tentative_g + self.heuristic(neighbor, target)
                        open_list.append((f_scores[neighbor], neighbor))
                        step_details.append(f"Updated g_score of node {neighbor} to {g_scores[neighbor]}")
                        step_edges.append((current, neighbor))
                    else:
                        step_details.append(f"No update for node {neighbor}, current g_score: {g_scores[neighbor]}")

                step_details.append(f"Open list: {open_list}")
                self.algorithm_steps.append({'edges': step_edges, 'stack': open_list.copy(), 'details': step_details})

            path = nx.astar_path(self.graph, source, target, heuristic=self.heuristic, weight='weight')
            path_edges = list(zip(path, path[1:]))
            self.algorithm_steps.append({'edges': path_edges, 'stack': [], 'details': ["Final shortest path highlighted"]})
            self.current_step_index = -1
            self.next_step_button.config(state=tk.NORMAL)
            self.prev_step_button.config(state=tk.DISABLED)
            self.update_status("A* algorithm ready for step-by-step visualization.")
        except nx.NetworkXNoPath:
            messagebox.showerror("Error", "No path exists between the nodes.")

    def run_kruskal(self):
        pseudocode = """Kruskal's Algorithm:
1. Sort all edges in ascending order by weight
2. Initialize an empty MST
3. For each edge in sorted order:
    a. If adding the edge does not form a cycle:
        Add the edge to the MST
4. Return MST
"""
        self.display_pseudocode(pseudocode)

        if len(self.graph.edges) < 1:
            messagebox.showwarning("Warning", "Graph has no edges.")
            return

        self.draw_graph()
        self.algorithm_steps = []
        edges = sorted(self.graph.edges(data=True), key=lambda x: x[2].get('weight', 1))
        mst_edges = []
        disjoint_set = {node: node for node in self.graph.nodes}

        def find(node):
            if disjoint_set[node] != node:
                disjoint_set[node] = find(disjoint_set[node])
            return disjoint_set[node]

        def union(node1, node2):
            root1 = find(node1)
            root2 = find(node2)
            if root1 != root2:
                disjoint_set[root2] = root1

        for edge in edges:
            u, v, data = edge
            weight = data.get('weight', 1)
            step_details = [f"Considering edge ({u} -> {v}) with weight {weight}"]
            if find(u) != find(v):
                mst_edges.append((u, v))
                union(u, v)
                step_details.append(f"Added edge ({u} -> {v}) to MST")
            else:
                step_details.append(f"Edge ({u} -> {v}) forms a cycle and is ignored")
            self.algorithm_steps.append({'edges': mst_edges.copy(), 'stack': edges, 'details': step_details})
        self.algorithm_steps.append({'edges': mst_edges.copy(), 'stack': [], 'details': ["Kruskal's algorithm complete", "Final MST constructed"]})
        self.current_step_index = -1
        self.next_step_button.config(state=tk.NORMAL)
        self.prev_step_button.config(state=tk.DISABLED)
        self.update_status("Kruskal's algorithm ready for step-by-step visualization.")

    def run_prim(self):
        pseudocode = """Prim's Algorithm:
1. Initialize MST with an arbitrary starting node
2. Add all edges from the starting node to a priority queue
3. While the priority queue is not empty:
    a. Extract the smallest edge (u, v)
    b. If v is not in MST:
        Add v to MST
        Add all edges from v to the priority queue
4. Return MST
"""
        self.display_pseudocode(pseudocode)

        if len(self.graph.nodes) < 1:
            messagebox.showwarning("Warning", "Graph is empty.")
            return

        self.draw_graph()
        self.algorithm_steps = []
        mst_nodes = set()
        mst_edges = []
        start_node = list(self.graph.nodes)[0]
        mst_nodes.add(start_node)
        priority_queue = [(self.graph[start_node][neighbor]['weight'], start_node, neighbor) for neighbor in self.graph.neighbors(start_node)]
        self.algorithm_steps.append({'edges': mst_edges.copy(), 'stack': priority_queue.copy(), 'details': [f"Start with node {start_node}", f"Initial edges in priority queue: {priority_queue}"]})
        while priority_queue:
            priority_queue.sort()
            weight, u, v = priority_queue.pop(0)
            step_details = [f"Considering edge ({u} -> {v}) with weight {weight}"]
            if v not in mst_nodes:
                mst_nodes.add(v)
                mst_edges.append((u, v))
                step_details.append(f"Added edge ({u} -> {v}) to MST")
                step_details.append(f"Current MST nodes: {mst_nodes}")
                step_details.append(f"Current MST edges: {mst_edges}")
                for neighbor in self.graph.neighbors(v):
                    if neighbor not in mst_nodes:
                        edge_weight = self.graph[v][neighbor]['weight']
                        priority_queue.append((edge_weight, v, neighbor))
                step_details.append(f"Updated priority queue: {priority_queue}")
            else:
                step_details.append(f"Edge ({u} -> {v}) forms a cycle and is ignored")
            self.algorithm_steps.append({'edges': mst_edges.copy(), 'stack': priority_queue.copy(), 'details': step_details})
        self.algorithm_steps.append({'edges': mst_edges.copy(), 'stack': [], 'details': ["Prim's algorithm complete", "Final MST constructed"]})
        self.current_step_index = -1
        self.next_step_button.config(state=tk.NORMAL)
        self.prev_step_button.config(state=tk.DISABLED)
        self.update_status("Prim's algorithm ready for step-by-step visualization.")

    def run_kosaraju(self):
        pseudocode = """Kosaraju's Algorithm:
1. Perform DFS on the original graph, recording finish times.
2. Reverse the graph.
3. Perform DFS on the reversed graph in order of decreasing finish times to discover SCCs.
"""
        self.display_pseudocode(pseudocode)
        if not self.is_directed:
            messagebox.showwarning("Warning", "Kosaraju's algorithm requires a directed graph.")
            return

        self.draw_graph()
        self.algorithm_steps = []
        finish_stack = []
        visited = set()

        def dfs_phase1(node):
            visited.add(node)
            self.algorithm_steps.append({
                'highlight': [node],
                'stack': finish_stack.copy(),
                'details': [f"Phase1: Visit node {node}"]
            })
            for neighbor in self.graph.neighbors(node):
                if neighbor not in visited:
                    dfs_phase1(neighbor)
            finish_stack.append(node)
            self.algorithm_steps.append({
                'highlight': [node],
                'stack': finish_stack.copy(),
                'details': [f"Phase1: Finished node {node}, push to finish_stack"]
            })

        for node in list(self.graph.nodes()):
            if node not in visited:
                dfs_phase1(node)

        # Phase 2: Reverse the graph
        reversed_graph = self.graph.reverse()
        self.algorithm_steps.append({
            'highlight': [],
            'stack': finish_stack.copy(),
            'details': ["Phase2: Graph reversed."]
        })

        # Phase 3: DFS on reversed graph using finish_stack order
        visited.clear()
        sccs = []
        while finish_stack:
            node = finish_stack.pop()
            if node not in visited:
                scc = []
                stack = [node]
                self.algorithm_steps.append({
                    'highlight': [node],
                    'stack': finish_stack.copy(),
                    'details': [f"Phase3: Start DFS from node {node} in reversed graph"]
                })
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        scc.append(current)
                        self.algorithm_steps.append({
                            'highlight': [current],
                            'stack': stack.copy(),
                            'details': [f"Phase3: Visit node {current}"]
                        })
                        for neighbor in reversed_graph.neighbors(current):
                            if neighbor not in visited:
                                stack.append(neighbor)
                                self.algorithm_steps.append({
                                    'highlight': [neighbor],
                                    'stack': stack.copy(),
                                    'details': [f"Phase3: Add neighbor {neighbor} to stack"]
                                })
                sccs.append(scc)
                self.algorithm_steps.append({
                    'highlight': scc,
                    'stack': stack.copy(),
                    'details': [f"Phase3: Discovered SCC: {scc}"]
                })

        # Final step: Color the graph based on SCCs
        self.draw_scc(sccs)
        self.algorithm_steps.append({
            'highlight': [],
            'stack': [],
            'details': [f"Kosaraju complete. SCCs: {sccs}"]
        })

        self.current_step_index = -1
        self.next_step_button.config(state=tk.NORMAL)
        self.prev_step_button.config(state=tk.DISABLED)
        self.update_status("Kosaraju's algorithm ready for step-by-step visualization.")

    def run_tarjan(self):
        pseudocode = """Tarjan's Algorithm:
1. Perform DFS on the graph, assigning each node an index and low-link value.
2. Use a stack to keep track of visited nodes.
3. When a node's low-link equals its index, pop nodes from the stack to form an SCC.
"""
        self.display_pseudocode(pseudocode)
        if not self.is_directed:
            messagebox.showwarning("Warning", "Tarjan's algorithm requires a directed graph.")
            return

        self.draw_graph()
        self.algorithm_steps = []
        index = 0
        stack = []
        indices = {}
        low_link = {}
        on_stack = set()
        sccs = []

        def strong_connect(node):
            nonlocal index
            indices[node] = index
            low_link[node] = index
            index += 1
            stack.append(node)
            on_stack.add(node)
            self.algorithm_steps.append({
                'highlight': [node],
                'stack': stack.copy(),
                'details': [f"Push node {node} onto stack. Index: {indices[node]}, LowLink: {low_link[node]}"]
            })
            for neighbor in self.graph.neighbors(node):
                if neighbor not in indices:
                    self.algorithm_steps.append({
                        'highlight': [neighbor],
                        'stack': stack.copy(),
                        'details': [f"Neighbor {neighbor} not visited, recurse."]
                    })
                    strong_connect(neighbor)
                    low_link[node] = min(low_link[node], low_link[neighbor])
                    self.algorithm_steps.append({
                        'highlight': [node],
                        'stack': stack.copy(),
                        'details': [f"After visiting {neighbor}, update LowLink of {node} to {low_link[node]}"]
                    })
                elif neighbor in on_stack:
                    low_link[node] = min(low_link[node], indices[neighbor])
                    self.algorithm_steps.append({
                        'highlight': [node, neighbor],
                        'stack': stack.copy(),
                        'details': [f"Neighbor {neighbor} in stack, update LowLink of {node} to {low_link[node]}"]
                    })
            if low_link[node] == indices[node]:
                scc = []
                self.algorithm_steps.append({
                    'highlight': [node],
                    'stack': stack.copy(),
                    'details': [f"Node {node} is root of an SCC. Start popping stack."]
                })
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    self.algorithm_steps.append({
                        'highlight': [w],
                        'stack': stack.copy(),
                        'details': [f"Popped node {w} from stack. Current SCC: {scc}"]
                    })
                    if w == node:
                        break
                sccs.append(scc)
                self.algorithm_steps.append({
                    'highlight': scc,
                    'stack': stack.copy(),
                    'details': [f"Completed SCC: {scc}"]
                })

        for node in list(self.graph.nodes()):
            if node not in indices:
                strong_connect(node)

        self.draw_scc(sccs)
        self.algorithm_steps.append({
            'highlight': [],
            'stack': [],
            'details': [f"Tarjan complete. SCCs: {sccs}"]
        })

        self.current_step_index = -1
        self.next_step_button.config(state=tk.NORMAL)
        self.prev_step_button.config(state=tk.DISABLED)
        self.update_status("Tarjan's algorithm ready for step-by-step visualization.")

    def heuristic(self, u, v):
        pos_u = self.positions[u]
        pos_v = self.positions[v]
        return math.hypot(pos_u[0] - pos_v[0], pos_u[1] - pos_v[1])

    def draw_scc(self, scc):
        self.ax.clear()
        self.ax.set_axis_on()
        self.ax.grid(True)
        colors = plt.cm.tab10.colors
        for i, component in enumerate(scc):
            color = colors[i % len(colors)]
            nx.draw_networkx_nodes(
                self.graph, 
                self.positions, 
                nodelist=list(component),
                node_color=[color], 
                node_size=500, 
                ax=self.ax
            )
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

    def create_pseudocode_area(self):
        self.pseudocode_area = tk.Text(self.master, wrap=tk.WORD, height=20, width=40)
        self.pseudocode_area.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.pseudocode_area.config(state=tk.DISABLED)

    def display_pseudocode(self, pseudocode):
        self.pseudocode_area.config(state=tk.NORMAL)
        self.pseudocode_area.delete(1.0, tk.END)
        self.pseudocode_area.insert(tk.END, pseudocode)
        self.pseudocode_area.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphVisualizerApp(root)
    root.mainloop()
