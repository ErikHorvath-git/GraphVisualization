import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import networkx as nx
import matplotlib
import math
import gzip
from show_grafy import get_sample_graph_1, get_sample_graph_2, get_directed_graph, get_complex_graph

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class GraphVisualizerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Vizualizácia grafových algoritmov – bakalárska práca")
        self.master.geometry("1300x750")  

        style = ttk.Style()
        style.theme_use('clam')

        self.is_directed = False
        self.show_edges = True
        self.graph = nx.Graph()
        self.positions = {}         
        self.node_list = []         
        self.current_step_index = -1  
        self.algorithm_steps = []   

        self.show_weights = True
        self.node_id = 0
        self.add_node_mode = False
        self.add_edge_mode = False
        self.edge_start_node = None
        self.create_widgets()

    def clear_step_visualization(self):
        self.stack_listbox.delete(0, tk.END)
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.config(state=tk.DISABLED)

    def create_widgets(self):
        self.paned_window = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.sidebar = ttk.Frame(self.paned_window, width=320, padding=10)
        self.paned_window.add(self.sidebar, weight=0)

        self.main_area = ttk.Frame(self.paned_window, padding=10)
        self.paned_window.add(self.main_area, weight=1)

        self.create_sidebar_components()
        self.create_canvas()
        self.create_menu()
        self.create_toolbar()
        self.create_status_bar()

    def create_sidebar_components(self):
        pseudocode_label = ttk.Label(self.sidebar, text="Pseudokód", font=("Arial", 12, "bold"))
        pseudocode_label.pack(anchor=tk.W, pady=(0, 5))
        self.pseudocode_area = tk.Text(self.sidebar, wrap=tk.WORD, height=10, width=40, background="#F5F5F5")
        self.pseudocode_area.pack(fill=tk.X, pady=(0, 10))
        self.pseudocode_area.config(state=tk.DISABLED)

        stack_label = ttk.Label(self.sidebar, text="Vizualizácia dátovej štruktúry", font=("Arial", 12, "bold"))
        stack_label.pack(anchor=tk.W, pady=(0, 5))
        self.stack_listbox = tk.Listbox(self.sidebar, height=10, width=40)
        self.stack_listbox.pack(fill=tk.BOTH, pady=(0, 10))

        details_label = ttk.Label(self.sidebar, text="Detailný popis kroku", font=("Arial", 12, "bold"))
        details_label.pack(anchor=tk.W, pady=(0, 5))
        self.details_text = tk.Text(self.sidebar, wrap=tk.WORD, height=10, width=40, background="#F5F5F5")
        self.details_text.pack(fill=tk.BOTH, pady=(0, 10))
        self.details_text.config(state=tk.DISABLED)

    def create_canvas(self):
        self.figure = plt.Figure(figsize=(6, 4))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_axis_on()
        self.ax.grid(True)
        self.ax.set_aspect('equal')
        self.fixed_margin = 10
        self.fixed_limits = (-self.fixed_margin, self.fixed_margin, -self.fixed_margin, self.fixed_margin)
        self.ax.set_xlim(self.fixed_limits[0], self.fixed_limits[1])
        self.ax.set_ylim(self.fixed_limits[2], self.fixed_limits[3])

        self.canvas = FigureCanvasTkAgg(self.figure, self.main_area)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.annot = self.ax.annotate("", xy=(0, 0), xytext=(10, 10),
                                      textcoords="offset points",
                                      bbox=dict(boxstyle="round", fc="w"),
                                      arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)
        self.canvas.mpl_connect("pick_event", self.on_pick)

        self.canvas.get_tk_widget().bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self.master, tearoff=0)
        self.context_menu.add_command(label="Zmazať vrchol", command=self.delete_node)
        self.context_menu.add_command(label="Zmazať hranu", command=self.delete_edge)

    def on_hover(self, event):
        if event.inaxes != self.ax:
            self.annot.set_visible(False)
            self.canvas.draw_idle()
            return
        threshold = 0.3
        vis = False
        if event.xdata is None or event.ydata is None:
            self.annot.set_visible(False)
            self.canvas.draw_idle()
            return
        for node in self.node_list:
            pos = self.positions.get(node)
            if pos is None:
                continue
            dx = pos[0] - event.xdata
            dy = pos[1] - event.ydata
            if math.hypot(dx, dy) < threshold:
                self.annot.xy = pos
                self.annot.set_text(f"vrchol: {node}")
                self.annot.get_bbox_patch().set_facecolor("lightyellow")
                self.annot.get_bbox_patch().set_alpha(0.9)
                vis = True
                break
        self.annot.set_visible(vis)
        self.canvas.draw_idle()

    def create_menu(self):
        menubar = tk.Menu(self.master)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nový graf", command=self.new_graph)
        file_menu.add_command(label="Otvoriť graf...", command=self.open_graph)
        file_menu.add_command(label="Uložiť graf...", command=self.save_graph)
        file_menu.add_separator()
        file_menu.add_command(label="Ukončiť", command=self.master.quit)
        file_menu.add_separator()
        file_menu.add_command(label="Načítať neorientovaný graf 1", command=lambda: self.load_sample_graph(get_sample_graph_1))
        file_menu.add_command(label="Načítať neorientovaný graf 2", command=lambda: self.load_sample_graph(get_sample_graph_2))
        file_menu.add_command(label="Načítať orientovaný graf 1", command=lambda: self.load_sample_graph(get_directed_graph))
        file_menu.add_command(label="Načítať orientovaný graf 2", command=lambda: self.load_sample_graph(get_complex_graph))
        menubar.add_cascade(label="Súbor", menu=file_menu)

        algorithms_menu = tk.Menu(menubar, tearoff=0)
        algorithms_menu.add_command(label="Dijkstrov algoritmus", command=self.run_dijkstra)
        algorithms_menu.add_command(label="Bellman-Fordov algoritmus", command=self.run_bellman_ford)
        algorithms_menu.add_command(label="A* algoritmus", command=self.run_astar)
        algorithms_menu.add_command(label="Kruskalov algoritmus", command=self.run_kruskal)
        algorithms_menu.add_command(label="Primov algoritmus", command=self.run_prim)
        algorithms_menu.add_command(label="Kosarajuho algoritmus", command=self.run_kosaraju)
        algorithms_menu.add_command(label="Tarjanov algoritmus", command=self.run_tarjan)
        menubar.add_cascade(label="Algoritmy", menu=algorithms_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        self.directed_var = tk.BooleanVar(value=False)
        view_menu.add_checkbutton(label="Orientovaný graf", variable=self.directed_var, command=self.toggle_directed)
        menubar.add_cascade(label="Režim", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="O programe", command=self.show_about)
        menubar.add_cascade(label="Pomoc", menu=help_menu)

        self.master.config(menu=menubar)

    def create_toolbar(self):
        toolbar = ttk.Frame(self.master, padding=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.add_node_button = ttk.Button(toolbar, text="Pridat vrchol", command=self.add_node_mode_on)
        self.add_node_button.pack(side=tk.LEFT, padx=5)

        self.add_edge_button = ttk.Button(toolbar, text="Pridat hranu", command=self.add_edge_mode_on)
        self.add_edge_button.pack(side=tk.LEFT, padx=5)

        self.prev_step_button = ttk.Button(toolbar, text="Predošlý krok", command=self.prev_step, state=tk.DISABLED)
        self.prev_step_button.pack(side=tk.LEFT, padx=5)

        self.next_step_button = ttk.Button(toolbar, text="Nasledujúci krok", command=self.next_step, state=tk.DISABLED)
        self.next_step_button.pack(side=tk.LEFT, padx=5)

        self.tutorial_button = ttk.Button(toolbar, text="Tutorial", command=self.show_tutorial)
        self.tutorial_button.pack(side=tk.LEFT, padx=5)

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Vitajte! Vyberte si algoritmus pre vizualizáciu.")
        self.status_bar = ttk.Label(self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        self.status_var.set(message)

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
        self.update_status("Nový graf vytvorený.")

    def save_graph(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Textové súbory", "*.txt"), ("Všetky súbory", "*.*")])
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
                self.update_status(f"Graf uložený do {file_path}.")
            except Exception as e:
                messagebox.showerror("Chyba", f"Uloženie grafu zlyhalo: {e}")

    def open_graph(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt",
                                               filetypes=[("Textové súbory", "*.txt"), ("Všetky súbory", "*.*")])
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
                self.update_status(f"Graf načítaný z {file_path}.")
            except Exception as e:
                messagebox.showerror("Chyba", f"Načítanie grafu zlyhalo: {e}")

    def show_about(self):
        about_message = (
            "Interaktívna vizualizácia grafových algoritmov\n"
            "Táto aplikácia bola navrhnutá ako učebná pomôcka pre študentov a učiteľov.\n"
            "Používa Tkinter, NetworkX a Matplotlib.\n"
            "Pre detailné vysvetlenie kliknite na tlačidlo Tutorial.\n"
            "Užite si učenie!"
        )
        messagebox.showinfo("O programe", about_message)

    def toggle_directed(self):
        self.is_directed = self.directed_var.get()
        if self.is_directed:
            self.update_status("Prepnuté do orientovaného módu. Graf bol vymazaný.")
            self.graph = nx.DiGraph()  

        else:
            self.update_status("Prepnuté do neorientovaného módu. Graf bol vymazaný.")
        
        self.graph.clear()
        self.positions.clear()
        self.node_list.clear()
        self.edge_start_node = None
        self.add_node_mode = False
        self.add_edge_mode = False
        self.draw_graph()

    def add_node_mode_on(self):
        self.add_node_mode = True
        self.master.config(cursor="crosshair")
        self.update_status("Kliknite na plátno pre pridanie vrcholu.")

    def add_edge_mode_on(self):
        if len(self.graph.nodes) < 2:
            messagebox.showwarning("Upozornenie", "Na pridanie hrany sú potrebné aspoň dva vrcholy.")
            return
        self.add_edge_mode = True
        self.edge_start_node = None
        self.master.config(cursor="tcross")
        self.update_status("Najprv vyberte zdrojový vrchol, potom cieľový vrchol.")

    
    def on_canvas_click(self, event):
        if event.xdata is None or event.ydata is None:
            return
        if self.add_node_mode:
            if not self.graph.nodes:
                self.node_id = 1 
            else:
                self.node_id = max(self.graph.nodes) + 1  

            self.graph.add_node(self.node_id)
            self.positions[self.node_id] = (event.xdata, event.ydata)

            self.draw_graph()

            self.add_node_mode = False
            self.master.config(cursor="")

            self.update_status(f"vrchol {self.node_id} pridaný.")


    def on_pick(self, event):
        if self.add_edge_mode:
            if event.mouseevent.xdata is None or event.mouseevent.ydata is None:
                return

            min_dist = float("inf")
            selected_node = None
            threshold = 0.3  

            for node, pos in self.positions.items():
                dx = pos[0] - event.mouseevent.xdata
                dy = pos[1] - event.mouseevent.ydata
                dist = math.hypot(dx, dy)

                if dist < min_dist and dist < threshold:
                    min_dist = dist
                    selected_node = node

            if selected_node is None:
                return

            if self.edge_start_node is None:
                self.edge_start_node = selected_node
                self.update_status(f"Zdrojový vrchol {selected_node} vybraný. Teraz vyberte cieľový vrchol.")
            else:
                if selected_node != self.edge_start_node:
                    weight = simpledialog.askfloat("Hodnota hrany", "Zadajte hodnotu hrany:")
                    if weight is None:
                        weight = 1.0
                
                    self.graph.add_edge(self.edge_start_node, selected_node, weight=weight)

                    self.update_status(f"Hrana medzi vrcholami {self.edge_start_node} a {selected_node} pridaná.")
                    self.draw_graph()
                else:
                    messagebox.showwarning("Upozornenie", "Nemôžete vytvoriť hranu zo samotného seba.")

                self.edge_start_node = None
                self.add_edge_mode = False
                self.master.config(cursor="")


    def draw_graph(self, path=[]):
        if not self.positions or any(node not in self.positions for node in self.graph.nodes()):
            self.positions = nx.spring_layout(self.graph)
        self.ax.clear()
        self.ax.set_axis_on()
        self.ax.grid(True)
        self.ax.set_aspect('equal')
        self.ax.set_xlim(self.fixed_limits[0], self.fixed_limits[1])
        self.ax.set_ylim(self.fixed_limits[2], self.fixed_limits[3])
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
                )
            nx.draw_networkx_labels(self.graph, self.positions, ax=self.ax)
            if self.show_weights:
                edge_labels = nx.get_edge_attributes(self.graph, 'weight')
                nx.draw_networkx_edge_labels(self.graph, self.positions, edge_labels=edge_labels, ax=self.ax)
        self.canvas.draw()

    def check_weights(self):
        for u, v, data in self.graph.edges(data=True):
            if 'weight' not in data:
                return False
            try:
                float(data['weight'])
            except (ValueError, TypeError):
                return False
        return True

    def animate_transition(self, old_step, new_step, frames=10, delay=50):
        def update_frame(frame):
            frac = frame / frames
            self.ax.clear()
            self.ax.set_axis_on()
            self.ax.grid(True)
            nx.draw_networkx_nodes(self.graph, self.positions, ax=self.ax, node_color='skyblue', node_size=500)
            nx.draw_networkx_edges(self.graph, self.positions, ax=self.ax, edge_color='black', width=1)
            nx.draw_networkx_labels(self.graph, self.positions, ax=self.ax)
            updated_edges = new_step.get('updated_edges', [])
            if updated_edges:
                width = 1 + 3 * frac
                nx.draw_networkx_edges(
                    self.graph, self.positions,
                    ax=self.ax,
                    edgelist=updated_edges,
                    edge_color='green',
                    width=width
                )
            no_update_edges = new_step.get('no_update_edges', [])
            if no_update_edges:
                width = 1 + 3 * frac
                nx.draw_networkx_edges(
                    self.graph, self.positions,
                    ax=self.ax,
                    edgelist=no_update_edges,
                    edge_color='red',
                    width=width,
                    style='dashed'
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
            self.update_status(f"Krok {self.current_step_index + 1} z {len(self.algorithm_steps)}")
            self.prev_step_button.config(state=tk.NORMAL)
            if self.current_step_index + 1 == len(self.algorithm_steps):
                self.next_step_button.config(state=tk.DISABLED)
        else:
            self.update_status("Žiadne ďalšie kroky.")

    def prev_step(self):
        if self.current_step_index > 0:
            old_step = self.algorithm_steps[self.current_step_index]
            self.current_step_index -= 1
            new_step = self.algorithm_steps[self.current_step_index]
            self.animate_transition(old_step, new_step)
            self.update_status(f"Krok {self.current_step_index + 1} z {len(self.algorithm_steps)}")
            self.next_step_button.config(state=tk.NORMAL)
            if self.current_step_index == 0:
                self.prev_step_button.config(state=tk.DISABLED)
        else:
            self.update_status("Na začiatku krokov.")

    def draw_graph_with_step(self, step):
        self.ax.clear()
        self.ax.set_axis_on()
        self.ax.grid(True)
        
        nx.draw_networkx_nodes(self.graph, self.positions, ax=self.ax, node_color='skyblue', node_size=500)
        
        
        if 'edges' in step and step['edges']:
            nx.draw_networkx_edges(
                self.graph, self.positions, ax=self.ax,
                edgelist=step['edges'], edge_color='green', width=2
            )
        else:
            nx.draw_networkx_edges(self.graph, self.positions, ax=self.ax, edge_color='black', width=1)
            updated_edges = step.get('updated_edges', [])
            no_update_edges = step.get('no_update_edges', [])
            if updated_edges:
                nx.draw_networkx_edges(
                    self.graph, self.positions, ax=self.ax,
                    edgelist=updated_edges, edge_color='green', width=2
                )
            if no_update_edges:
                nx.draw_networkx_edges(
                    self.graph, self.positions, ax=self.ax,
                    edgelist=no_update_edges, edge_color='red', width=2, style='dashed'
                )
        
        highlight = step.get('highlight', [])
        if highlight:
            nx.draw_networkx_nodes(
                self.graph, self.positions, nodelist=highlight, ax=self.ax,
                node_color='yellow', node_size=500
            )
        
        nx.draw_networkx_labels(self.graph, self.positions, ax=self.ax)
        
        if self.show_weights:
            edge_labels = nx.get_edge_attributes(self.graph, 'weight')
            nx.draw_networkx_edge_labels(self.graph, self.positions, edge_labels=edge_labels, ax=self.ax)
        
        import matplotlib.lines as mlines
        handles = []
        if step.get('updated_edges', []):
            green_line = mlines.Line2D([], [], color='green', linewidth=2, label='Aktualizácia (Update)')
            handles.append(green_line)
        if step.get('no_update_edges', []):
            red_line = mlines.Line2D([], [], color='red', linewidth=2, linestyle='dashed', label='Bez aktualizácie')
            handles.append(red_line)
        if handles:
            self.ax.legend(handles=handles, loc='upper right')
        
        structure_type = step.get('structure_type', "")
        self.update_stack_display(step.get('stack', []), structure_type)
        self.update_details_display(step.get('details', []))
        
        self.canvas.draw()


    def update_stack_display(self, stack, structure_type=""):
        self.stack_listbox.delete(0, tk.END)
        if structure_type:
            self.stack_listbox.insert(tk.END, f"{structure_type}:")
            self.stack_listbox.insert(tk.END, "-" * 20)
        for item in stack:
            if isinstance(item, tuple):
                if len(item) == 3:
                    self.stack_listbox.insert(tk.END, f"Hrana: Vrchol: {item[1]}->{item[2]}-> Ohodnotenie: {item[0]}")
                elif len(item) == 2:
                    self.stack_listbox.insert(tk.END, f"vrchol: {item[1]}, Vzdialenosť: {item[0]}")
                elif len(item) == 3:
                    self.stack_listbox.insert(tk.END, f"{item[2]} ← {item[1]} (vzdialenosť: {item[0]})")

                else:
                    self.stack_listbox.insert(tk.END, str(item))
            else:
                self.stack_listbox.insert(tk.END, str(item))

    def update_details_display(self, details):
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        for line in details:
            self.details_text.insert(tk.END, line + "\n")
        self.details_text.config(state=tk.DISABLED)

    def delete_node(self):
        node_id = simpledialog.askinteger("Zmazať vrchol", "Zadajte ID vrchola na zmazanie:")
        if node_id in self.graph.nodes:
            self.graph.remove_node(node_id)
            self.positions.pop(node_id, None)
            self.draw_graph()
            self.update_status(f"vrchol {node_id} zmazaný.")
        else:
            messagebox.showerror("Chyba", "vrchol s týmto ID neexistuje.")

    def delete_edge(self):
        edge = simpledialog.askstring("Zmazať hranu", "Zadajte hranu vo formáte 'zdroj,ciel':")
        if edge:
            try:
                source, target = map(int, edge.split(','))
                if self.graph.has_edge(source, target):
                    self.graph.remove_edge(source, target)
                    self.draw_graph()
                    self.update_status(f"Hrana {source}->{target} zmazaná.")
                else:
                    messagebox.showerror("Chyba", "Hrana neexistuje.")
            except ValueError:
                messagebox.showerror("Chyba", "Nesprávny formát.")

    def display_pseudocode(self, pseudocode):
        self.pseudocode_area.config(state=tk.NORMAL)
        self.pseudocode_area.delete("1.0", tk.END)
        self.pseudocode_area.insert(tk.END, pseudocode)
        self.pseudocode_area.config(state=tk.DISABLED)

    def load_sample_graph(self, graph_func):
        self.graph, self.positions = graph_func()
        if not self.positions:
            self.positions = nx.spring_layout(self.graph)
        self.draw_graph()

    # ----------------------- Implementácie algoritmov -----------------------

    def contains_negative_edge(self):
        for u, v, data in self.graph.edges(data=True):
            weight = data.get('weight', 1)
            if weight < 0:
                return True
        return False

    def run_dijkstra(self):
        self.clear_step_visualization()
        self.show_edges = True

        if self.contains_negative_edge():
            messagebox.showerror("Tento algoritmus nepracuje so zápornými hranami")
            return

        if not self.check_weights():
            messagebox.showwarning("Upozornenie", "Nie všetky hrany majú nastavenú váhu. Váhy budú deaktivované pre tento algoritmus.")
            self.show_weights = False
        else:
            self.show_weights = True

        pseudocode = (
            "DIJKSTRA(G, w, s)\n"
            "1  pre každý vrchol u ∈ G.V\n"
            "2      u.vzdialenosť = ∞\n"
            "3      u.predchodca = NIL\n"
            "4  s.vzdialenosť = 0\n"
            "5  S = ∅\n"
            "6  Q = G.V\n"
            "7  kým Q ≠ ∅\n"
            "8      u = EXTRAHUJ-MIN(Q)\n"
            "9      S = S ∪ {u}\n"
            "10 pre každý vrchol v ∈ G.Susedia[u]\n"
            "11     ak v ∈ Q a v.vzdialenosť > u.vzdialenosť + w(u, v)\n"
            "12         v.vzdialenosť = u.vzdialenosť + w(u, v)\n"
            "13         v.predchodca = u\n"
        )
        self.display_pseudocode(pseudocode)

        source = simpledialog.askinteger("Dijkstrov algoritmus", "Zadajte zdrojový vrchol:")
        self.master.update()
        target = simpledialog.askinteger("Dijkstrov algoritmus", "Zadajte cieľový vrchol:")

        if source not in self.graph.nodes or target not in self.graph.nodes:
            messagebox.showerror("Chyba", "Nesprávne vrcholy.")
            return

        self.draw_graph()
        self.algorithm_steps = []

        distances = {node: float('inf') for node in self.graph.nodes}
        distances[source] = 0
        predecessors = {node: None for node in self.graph.nodes}
        priority_queue = [(0, source, None)]  # (vzdialenosť, cieľ, predchodca)
        visited = set()

        while priority_queue:
            priority_queue.sort(key=lambda x: x[0])
            current_distance, current_node, from_node = priority_queue.pop(0)

            if current_node in visited:
                continue
            visited.add(current_node)

            step_details = []
            updated_edges = []
            no_update_edges = []

            step_details.append(f"Spracovávaný vrchol: {current_node} (vzdialenosť: {current_distance})")

            for neighbor in self.graph.neighbors(current_node):
                weight = self.graph[current_node][neighbor].get('weight', 1)
                new_distance = current_distance + weight
                step_details.append(f"Zvažovaná hrana ({current_node} → {neighbor}) s váhou {weight}")

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current_node
                    priority_queue.append((new_distance, neighbor, current_node))
                    step_details.append(f"Aktualizácia: vzdialenosť {neighbor} = {new_distance}")
                    step_details.append(f"Predchodca {neighbor} = {current_node}")
                    updated_edges.append((current_node, neighbor))
                else:
                    step_details.append(f"Bez zmeny pre {neighbor} (aktuálna vzdialenosť: {distances[neighbor]})")
                    no_update_edges.append((current_node, neighbor))

            self.algorithm_steps.append({
                'updated_edges': updated_edges,
                'no_update_edges': no_update_edges,
                'stack': priority_queue.copy(),  # obsahuje aj predchodcov
                'details': step_details,
                'structure_type': "Prioritný front"
            })

        # Finálna cesta
        try:
            path = nx.dijkstra_path(self.graph, source=source, target=target, weight='weight')
            path_edges = list(zip(path, path[1:]))
            self.algorithm_steps.append({
                'updated_edges': path_edges,
                'no_update_edges': [],
                'stack': [],
                'details': ["Finálna najkratšia cesta zvýraznená."],
                'structure_type': ""
            })
            self.current_step_index = -1
            self.next_step_button.config(state=tk.NORMAL)
            self.prev_step_button.config(state=tk.DISABLED)
            self.update_status("Dijkstrov algoritmus pripravený na vizualizáciu.")
        except nx.NetworkXNoPath:
            messagebox.showerror("Chyba", "Medzi zadanými vrcholami neexistuje cesta.")


    def run_bellman_ford(self):
        self.clear_step_visualization()
        self.show_edges = True

        if not self.check_weights():
            messagebox.showwarning("Upozornenie", "Nie všetky hrany majú nastavenú váhu. Váhy budú deaktivované pre tento algoritmus.")
            self.show_weights = False
        else:
            self.show_weights = True

        pseudocode = (
        "BELLMAN-FORD(G, w, s)\n"
        "1  pre každý vrchol v ∈ G.V:\n"
        "2      v.vzdialenosť = ∞\n"
        "3      v.predchodca = NIL\n"
        "4  s.vzdialenosť = 0\n"
        "5  pre i = 1 po |G.V| - 1:\n"
        "6      pre každú hranu (u, v) ∈ G.E:\n"
        "7          ak v.vzdialenosť > u.vzdialenosť + w(u, v):\n"
        "8              v.vzdialenosť = u.vzdialenosť + w(u, v)\n"
        "9              v.predchodca = u\n"
        "10 pre každú hranu (u, v) ∈ G.E:\n"
        "11     ak v.vzdialenosť > u.vzdialenosť + w(u, v):\n"
        "12         hlás chybu: graf obsahuje záporný cyklus\n"
        "Výstup: Pole vzdialeností a predchodcov, alebo chyba pri zápornom cykle\n"
        )

        self.display_pseudocode(pseudocode)

        source = simpledialog.askinteger("Bellman-Fordov algoritmus", "Zadajte zdrojový vrchol:")
        self.master.update()
        target = simpledialog.askinteger("Bellman-Fordov algoritmus", "Zadajte cieľový vrchol:")

        if source not in self.graph.nodes or target not in self.graph.nodes:
            messagebox.showerror("Chyba", "Nesprávne vrcholy.")
            return

        self.draw_graph()
        self.algorithm_steps = []

        distances = {node: float('inf') for node in self.graph.nodes}
        distances[source] = 0
        edges = list(self.graph.edges(data=True))

        for i in range(len(self.graph.nodes) - 1):
            step_details = [f"Iterácia {i+1}: Relaxácia hrán"]
            updated_edges = []
            no_update_edges = []
            updated = False  

            for u, v, data in edges:
                weight = data.get('weight', 1)
                step_details.append(f"➡️ Kontrola hrany ({u} → {v}), váha {weight}")

                if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    step_details.append(f"Aktualizácia: d({v}) = {distances[v]}")
                    updated_edges.append((u, v))
                    updated = True
                else:
                    step_details.append(f"Bez zmeny pre {v} (d = {distances[v]})")
                    no_update_edges.append((u, v))

            self.algorithm_steps.append({
                'updated_edges': updated_edges,
                'no_update_edges': no_update_edges,
                'stack': edges.copy(),
                'details': step_details,
                'structure_type': "Zoznam hrán"
            })

            if not updated:
                break  

        step_details = [" Kontrola záporných cyklov:"]
        negative_cycle_edges = []

        for u, v, data in edges:
            weight = data.get('weight', 1)
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                step_details.append(f" Detekovaný záporný cyklus na hrane ({u} → {v}) s váhou {weight}")
                print(f"❗ Problémová hrana: {u} → {v}, váha = {weight}, d({u}) = {distances[u]}, d({v}) = {distances[v]}")
                negative_cycle_edges.append((u, v))

        if negative_cycle_edges:
            self.algorithm_steps.append({
                'updated_edges': negative_cycle_edges,
                'no_update_edges': [],
                'stack': [],
                'details': step_details,
                'structure_type': "Detekcia cyklu"
            })
            messagebox.showerror("Negatívny cyklus detekovaný!", "Algoritmus nemôže pokračovať.")
            self.update_status("Negatívny cyklus detekovaný!")
            return

        step_details.append("Žiadne záporné cykly neboli nájdené.")
        self.algorithm_steps.append({
            'updated_edges': [],
            'no_update_edges': [],
            'stack': [],
            'details': step_details,
            'structure_type': ""
        })

        try:
            path = nx.bellman_ford_path(self.graph, source=source, target=target, weight='weight')
            path_edges = list(zip(path, path[1:]))
            self.algorithm_steps.append({
                'updated_edges': path_edges,
                'no_update_edges': [],
                'stack': [],
                'details': ["🏁 Finálna najkratšia cesta zvýraznená."],
                'structure_type': "Najkratšia cesta"
            })
        except nx.NetworkXUnbounded:
            messagebox.showerror("Chyba", "Negatívny cyklus detekovaný! Algoritmus nemôže pokračovať.")
            self.update_status("Negatívny cyklus detekovaný!")
            return
        except nx.NetworkXNoPath:
            messagebox.showerror("Medzi zadanými vrcholami neexistuje cesta.", "Nie je možné pokračovať.")
            self.update_status("Medzi zadanými vrcholami neexistuje cesta.")
            return

        self.current_step_index = -1
        self.next_step_button.config(state=tk.NORMAL)
        self.prev_step_button.config(state=tk.DISABLED)
        self.update_status("Bellman-Ford pripravený na vizualizáciu.")



    def run_astar(self):
        self.show_edges = True
        self.clear_step_visualization()
        if self.contains_negative_edge():
            messagebox.showerror("Tento algoritmus nepracuje so zápornými hranami")
            return
        if not self.check_weights():
            messagebox.showwarning("Upozornenie", "Nie všetky hrany majú nastavenú váhu. Váhy budú deaktivované pre tento algoritmus.")
            self.show_weights = False
        else:
            self.show_weights = True

        pseudocode = (
            "A*(G, štart, cieľ, h)\n"
            "1  pre každý vrchol v ∈ G.V:\n"
            "2      g[v] = ∞        # skutočná vzdialenosť od štartu\n"
            "3      f[v] = ∞        # odhadovaná celková vzdialenosť (g + h)\n"
            "4      predchodca[v] = NIL\n"
            "5  g[štart] = 0\n"
            "6  f[štart] = h(štart)\n"
            "7  otvorené = množina obsahujúca iba štart\n"
            "8  kým otvorené nie je prázdne:\n"
            "9      v = vrchol v otvorených s najmenším f[v]\n"
            "10     ak v == cieľ:\n"
            "11         vráť cestu zrekonštruovanú pomocou predchodca\n"
            "12     odstráň v z otvorených\n"
            "13     pre každého suseda u vrcholu v:\n"
            "14         dočasné_g = g[v] + w(v, u)\n"
            "15         ak dočasné_g < g[u]:\n"
            "16             predchodca[u] = v\n"
            "17             g[u] = dočasné_g\n"
            "18             f[u] = g[u] + h(u)\n"
            "19             ak u nie je v otvorených:\n"
            "20                 pridaj u do otvorených\n"
            "Výstup: Najkratšia cesta z 'štart' do 'cieľ' alebo informácia, že neexistuje\n"
        )

        self.display_pseudocode(pseudocode)
        source = simpledialog.askinteger("A* algoritmus", "Zadajte zdrojový vrchol:")
        self.master.update()
        target = simpledialog.askinteger("A* algoritmus", "Zadajte cieľový vrchol:")
        if source not in self.graph.nodes or target not in self.graph.nodes:
            messagebox.showerror("Chyba", "Nesprávne vrcholy.")
            return

        self.draw_graph()
        self.algorithm_steps = []
        open_list = [(self.heuristic(source, target), source)]
        g_scores = {node: float('inf') for node in self.graph.nodes}
        g_scores[source] = 0
        f_scores = {node: float('inf') for node in self.graph.nodes}
        f_scores[source] = self.heuristic(source, target)

        while open_list:
            open_list.sort(key=lambda x: x[0])
            current_f, current = open_list.pop(0)
            step_details = [f"Spracovávame vrchol {current} (f = {f_scores[current]:.2f})"]
            updated_edges = []
            no_update_edges = []
            if current == target:
                step_details.append("Cieľový vrchol dosiahnutý.")
                break
            for neighbor in self.graph.neighbors(current):
                weight = self.graph[current][neighbor].get('weight', 1)
                tentative_g = g_scores[current] + weight
                step_details.append(f"Hrana ({current}->{neighbor}), hodnota {weight}")
                if tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    f_scores[neighbor] = tentative_g + self.heuristic(neighbor, target)
                    open_list.append((f_scores[neighbor], neighbor))
                    step_details.append(f"Aktualizácia: g({neighbor}) = {tentative_g:.2f}, f({neighbor}) = {f_scores[neighbor]:.2f}")
                    updated_edges.append((current, neighbor))
                else:
                    step_details.append(f"Bez aktualizácie pre {neighbor} (g = {g_scores[neighbor]:.2f})")
                    no_update_edges.append((current, neighbor))
            step_details.append(f"Otvárací zoznam: {open_list}")
            self.algorithm_steps.append({
                'updated_edges': updated_edges,
                'no_update_edges': no_update_edges,
                'stack': open_list.copy(),
                'details': step_details,
                'structure_type': "Prioritný front"
            })

        try:
            path = nx.astar_path(self.graph, source, target, heuristic=self.heuristic, weight='weight')
            path_edges = list(zip(path, path[1:]))
            self.algorithm_steps.append({'updated_edges': path_edges, 'no_update_edges': [], 'stack': [], 'details': ["Finálna najkratšia cesta zvýraznená."], 'structure_type': ""})
            self.current_step_index = -1
            self.next_step_button.config(state=tk.NORMAL)
            self.prev_step_button.config(state=tk.DISABLED)
            self.update_status("A* algoritmus pripravený na vizualizáciu.")
        except nx.NetworkXNoPath:
            messagebox.showerror("Chyba", "Medzi zadanými vrcholami neexistuje cesta.")

    def run_kruskal(self):
        self.show_edges = True
        self.clear_step_visualization()
        if self.contains_negative_edge():
            messagebox.showerror("Tento algoritmus nepracuje so zápornými hranami")
            return

        pseudocode = (
            "KRUSKAL(G)\n"
            "1  A ← ∅                # množina hrán v minimálnej kostre\n"
            "2  Pre každý vrchol v ∈ G.V:\n"
            "3      VYTVOR-MNOŽINU(v)\n"
            "4  Zoradíme všetky hrany (u, v) ∈ G.E podľa váhy w(u, v) vzostupne\n"
            "5  Pre každú hranu (u, v) ∈ G.E v tomto poradí:\n"
            "6      ak ZISTI-MNOŽINU(u) ≠ ZISTI-MNOŽINU(v):\n"
            "7          A ← A ∪ {(u, v)}\n"
            "8          ZJEDNOTI-MNOŽINY(u, v)\n"
            "9  vráť A ako množinu hrán minimálnej kostry\n"
        )

        self.display_pseudocode(pseudocode)

        if len(self.graph.edges) < 1:
            messagebox.showwarning("Upozornenie", "Graf neobsahuje žiadne hrany.")
            return

        self.draw_graph()
        self.algorithm_steps = []
        edges = sorted(self.graph.edges(data=True), key=lambda x: x[2].get('weight', 1))
        mst_edges = []
        disjoint_set = {node: node for node in self.graph.nodes()}

        def find(node):
            if disjoint_set[node] != node:
                disjoint_set[node] = find(disjoint_set[node])
            return disjoint_set[node]

        def union(u, v):
            root_u = find(u)
            root_v = find(v)
            if root_u != root_v:
                disjoint_set[root_v] = root_u

        for u, v, data in edges:
            weight = data.get('weight', 1)
            step_details = [f"Hrana ({u}->{v}), hodnota {weight}"]
            if find(u) != find(v):
                mst_edges.append((u, v))
                union(u, v)
                step_details.append("Hrana pridaná do MST.")
            else:
                step_details.append("Hrana vytvára cyklus – preskočená.")
            self.algorithm_steps.append({
                'edges': mst_edges.copy(),
                'stack': edges,
                'details': step_details,
                'structure_type': "Zoznam hrán"
            })

        self.algorithm_steps.append({
            'edges': mst_edges.copy(),
            'stack': [],
            'details': ["Kruskalov algoritmus dokončený. Finálne MST zostavené."],
            'structure_type': " union-find štruktúra"
        })
        self.current_step_index = -1
        self.next_step_button.config(state=tk.NORMAL)
        self.prev_step_button.config(state=tk.DISABLED)
        self.update_status("Kruskalov algoritmus pripravený na vizualizáciu.")

    def run_prim(self):
        self.clear_step_visualization()
        self.show_edges = True
        if self.contains_negative_edge():
            messagebox.showerror("Tento algoritmus nepracuje so zápornými hranami")
            return

        pseudocode = (
            "PRIM(G, štart)\n"
            "1  Pre každý vrchol v ∈ G.V:\n"
            "2      kľúč[v] ← ∞\n"
            "3      predchodca[v] ← NIL\n"
            "4  kľúč[štart] ← 0\n"
            "5  Q ← množina všetkých vrcholov V\n"
            "6  Kým Q nie je prázdna:\n"
            "7      u ← vrchol z Q s najmenším kľúč[u]\n"
            "8      Odstráň u z Q\n"
            "9      Pre každého suseda v vrcholu u:\n"
            "10         ak v ∈ Q a w(u, v) < kľúč[v]:\n"
            "11             predchodca[v] ← u\n"
            "12             kľúč[v] ← w(u, v)\n"
            "Výstup: Pole predchodcov definuje minimálnu kostru\n"
        )

        self.display_pseudocode(pseudocode)

        if len(self.graph.nodes) < 1:
            messagebox.showwarning("Upozornenie", "Graf je prázdny.")
            return

        self.draw_graph()
        self.algorithm_steps = []
        mst_nodes = set()
        mst_edges = []
        start_node = list(self.graph.nodes)[0]
        mst_nodes.add(start_node)
        priority_queue = [(self.graph[start_node][neighbor]['weight'], start_node, neighbor) for neighbor in self.graph.neighbors(start_node)]
        self.algorithm_steps.append({
            'edges': mst_edges.copy(),
            'stack': priority_queue.copy(),
            'details': [f"Začiatok vo vrchole {start_node}", f"Počiatočné hrany: {priority_queue}"],
            'structure_type': "Prioritný front"
        })

        while priority_queue:
            priority_queue.sort(key=lambda x: x[0])
            weight, u, v = priority_queue.pop(0)
            step_details = [f"Hrana ({u}->{v}), hodnota {weight}"]
            if v not in mst_nodes:
                mst_nodes.add(v)
                mst_edges.append((u, v))
                step_details.append(f"vrchol {v} pridaný do MST.")
                for neighbor in self.graph.neighbors(v):
                    if neighbor not in mst_nodes:
                        edge_weight = self.graph[v][neighbor]['weight']
                        priority_queue.append((edge_weight, v, neighbor))
                step_details.append(f"Zoznam: {priority_queue}")
            else:
                step_details.append("Hrana vytvára cyklus – preskočená.")
            self.algorithm_steps.append({
                'edges': mst_edges.copy(),
                'stack': priority_queue.copy(),
                'details': step_details,
                'structure_type': "Prioritný front"
            })

        self.algorithm_steps.append({
            'edges': mst_edges.copy(),
            'stack': [],
            'details': ["Primov algoritmus dokončený. Finálne MST zostavené."],
            'structure_type': ""
        })
        self.current_step_index = -1
        self.next_step_button.config(state=tk.NORMAL)
        self.prev_step_button.config(state=tk.DISABLED)
        self.update_status("Primov algoritmus pripravený na vizualizáciu.")

    def run_kosaraju(self):
        self.clear_step_visualization()
        self.show_edges = False
        pseudocode = (
            "KOSARAJU(G)\n"
            "1  navštívené ← prázdna množina\n"
            "2  zásobník ← prázdny\n"
            "3  Pre každý vrchol v ∈ G.V:\n"
            "4      ak v nie je v navštívené:\n"
            "5          DFS-PRVÁ-FÁZA(G, v, navštívené, zásobník)\n"
            "6  GT ← transponovaný graf G (s opačnými hranami)\n"
            "7  navštívené ← prázdna množina\n"
            "8  Pre každý vrchol v zo zásobníka (v poradí pop):\n"
            "9      ak v nie je v navštívené:\n"
            "10         komponent ← prázdny\n"
            "11         DFS-DRUHÁ-FÁZA(GT, v, navštívené, komponent)\n"
            "12         vypíš komponent ako jednu silne súvislú komponentu\n"
        )

        self.display_pseudocode(pseudocode)
        if not self.is_directed:
            messagebox.showwarning("Upozornenie", "Kosarajuho algoritmus vyžaduje orientovaný graf.")
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
                'details': [f"Fáza 1: Návšteva vrcholu {node}"],
                'structure_type': "Zásobník"
            })
            for neighbor in self.graph.neighbors(node):
                if neighbor not in visited:
                    dfs_phase1(neighbor)
            finish_stack.append(node)
            self.algorithm_steps.append({
                'highlight': [node],
                'stack': finish_stack.copy(),
                'details': [f"Fáza 1: vrchol {node} dokončený, pridaný do zásobníka"],
                'structure_type': ""
            })

        for node in list(self.graph.nodes()):
            if node not in visited:
                dfs_phase1(node)

        try:
            reversed_graph = self.graph.reverse(copy=True)
        except AttributeError:
            messagebox.showerror("Chyba", "Pre Kosarajuho algoritmus je potrebný orientovaný graf.")
            return

        self.algorithm_steps.append({
            'highlight': [],
            'stack': finish_stack.copy(),
            'details': ["Graf prevrátený pre Fázu 2."],
            'structure_type': "Zásobník"
        })

        visited.clear()
        sccs = []
        while finish_stack:
            node = finish_stack.pop()
            if node not in visited:
                scc = []
                stack = [node]
                self.algorithm_steps.append({
                    'highlight': [node],
                    'stack': stack.copy(),
                    'details': [f"Fáza 3: DFS z vrcholu {node} v prevrátenom grafe"],
                    'structure_type': "Zásobník"
                })
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        scc.append(current)
                        self.algorithm_steps.append({
                            'highlight': [current],
                            'stack': stack.copy(),
                            'details': [f"Návšteva vrcholu {current}"],
                            'structure_type': "Zásobník"
                        })
                        for neighbor in reversed_graph.neighbors(current):
                            if neighbor not in visited:
                                stack.append(neighbor)
                                self.algorithm_steps.append({
                                    'highlight': [neighbor],
                                    'stack': stack.copy(),
                                    'details': [f"Pridaný sused {neighbor} do zásobníka"],
                                    'structure_type': "Zásobník"
                                })
                sccs.append(scc)
                self.algorithm_steps.append({
                    'highlight': scc,
                    'stack': stack.copy(),
                    'details': [f"Zistený silne súvislý komponent: {scc}"],
                    'structure_type': "Zásobník"
                })

        self.draw_scc(sccs)
        self.algorithm_steps.append({
            'highlight': [],
            'stack': [],
            'details': [f"Kosarajuho algoritmus dokončený. Silne súvislé komponenty: {sccs}"],
            'structure_type': ""
        })
        self.current_step_index = -1
        self.next_step_button.config(state=tk.NORMAL)
        self.prev_step_button.config(state=tk.DISABLED)
        self.update_status("Kosarajuho algoritmus pripravený na vizualizáciu.")

    def run_tarjan(self):
        self.clear_step_visualization()
        self.show_edges = False
        pseudocode = (
            "TARJAN(G)\n"
            "1  index ← 0\n"
            "2  zásobník ← prázdny\n"
            "3  Pre každý vrchol v ∈ G.V:\n"
            "4      ak v.index nie je definovaný:\n"
            "5          STRONGCONNECT(v)\n"
            "\n"
            "Funkcia STRONGCONNECT(v):\n"
            "6      v.index ← index\n"
            "7      v.lowlink ← index\n"
            "8      index ← index + 1\n"
            "9      vlož v na zásobník\n"
            "10     v.naZásobníku ← true\n"
            "11     Pre každého suseda w vrcholu v:\n"
            "12         ak w.index nie je definovaný:\n"
            "13             STRONGCONNECT(w)\n"
            "14             v.lowlink ← min(v.lowlink, w.lowlink)\n"
            "15         inak ak w.naZásobníku:\n"
            "16             v.lowlink ← min(v.lowlink, w.index)\n"
            "17     ak v.lowlink == v.index:\n"
            "18         komponent ← prázdny\n"
            "19         opakuj:\n"
            "20             w ← zásobník.pop()\n"
            "21             w.naZásobníku ← false\n"
            "22             pridaj w do komponentu\n"
            "23         kým w ≠ v\n"
            "24         vypíš komponent ako silne súvislú komponentu\n"
        )

        self.display_pseudocode(pseudocode)
        if not self.is_directed:
            messagebox.showwarning("Upozornenie", "Tarjanov algoritmus vyžaduje orientovaný graf.")
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
                'details': [f"vrchol {node} pridaný: index {indices[node]}, low-link {low_link[node]}"],
                'structure_type': "Zásobník"
            })
            for neighbor in self.graph.neighbors(node):
                if neighbor not in indices:
                    self.algorithm_steps.append({
                        'highlight': [neighbor],
                        'stack': stack.copy(),
                        'details': [f"Prechod na suseda {neighbor} z vrcholu {node}"],
                        'structure_type': "Zásobník"
                    })
                    strong_connect(neighbor)
                    low_link[node] = min(low_link[node], low_link[neighbor])
                    self.algorithm_steps.append({
                        'highlight': [node],
                        'stack': stack.copy(),
                        'details': [f"Aktualizácia low-link {node} na {low_link[node]} po návšteve {neighbor}"],
                        'structure_type': "Zásobník"
                    })
                elif neighbor in on_stack:
                    low_link[node] = min(low_link[node], indices[neighbor])
                    self.algorithm_steps.append({
                        'highlight': [node, neighbor],
                        'stack': stack.copy(),
                        'details': [f"Sused {neighbor} v zásobníku: aktualizácia low-link {node} na {low_link[node]}"],
                        'structure_type': "Zásobník"
                    })
            if low_link[node] == indices[node]:
                scc = []
                self.algorithm_steps.append({
                    'highlight': [node],
                    'stack': stack.copy(),
                    'details': [f"vrchol {node} je koreňom SCC, začíname vytvárať SCC."],
                    'structure_type': "Zásobník"
                })
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    self.algorithm_steps.append({
                        'highlight': [w],
                        'stack': stack.copy(),
                        'details': [f"Vyradený vrchol {w} zo zásobníka, aktuálne SCC: {scc}"],
                        'structure_type': "Zásobník"
                    })
                    if w == node:
                        break
                sccs.append(scc)
                self.algorithm_steps.append({
                    'highlight': scc,
                    'stack': stack.copy(),
                    'details': [f"SCC dokončené: {scc}"],
                    'structure_type': "Zásobník"
                })

        for node in list(self.graph.nodes()):
            if node not in indices:
                strong_connect(node)

        self.draw_scc(sccs)
        self.algorithm_steps.append({
            'highlight': [],
            'stack': [],
            'details': [f"Tarjanov algoritmus dokončený. Silne súvislé komponenty: {sccs}"],
            'structure_type': ""
        })
        self.current_step_index = -1
        self.next_step_button.config(state=tk.NORMAL)
        self.prev_step_button.config(state=tk.DISABLED)
        self.update_status("Tarjanov algoritmus pripravený na vizualizáciu.")

    def heuristic(self, u, v):
        pos_u = self.positions.get(u, (0, 0))
        pos_v = self.positions.get(v, (0, 0))
        return math.hypot(pos_u[0] - pos_v[0], pos_u[1] - pos_v[1])

    def draw_scc(self, sccs):
        self.ax.clear()
        self.ax.set_axis_on()
        self.ax.grid(True)
        colors = plt.cm.tab10.colors
        for i, component in enumerate(sccs):
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
        if self.show_weights:
            edge_labels = nx.get_edge_attributes(self.graph, 'weight')
            nx.draw_networkx_edge_labels(self.graph, self.positions, edge_labels=edge_labels, ax=self.ax)
        self.canvas.draw()

    def show_tutorial(self):
        tutorial_win = tk.Toplevel(self.master)
        tutorial_win.title("Tutorial – Ako fungujú grafové algoritmy")
        tutorial_win.geometry("800x600")
        tutorial_text = tk.Text(tutorial_win, wrap=tk.WORD, background="#FAFAD2", font=("Arial", 11))
        tutorial_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tutorial_message = (
            "Vitajte v interaktívnej vizualizácii grafových algoritmov!\n\n"
            "Predtým ako si vytvoríte alebo načítate graf zvoľte si režim.\n\n"
            "Ako ju používať:\n"
            "1. Vyberte si algoritmus z menu 'Algoritmy'. Algoritmy, ktoré vyžadujú orientovaný graf (Kosarajuho, Tarjanov), sa spustia len ak je prepnutý orientovaný režim.\n"
            "2. Ak algoritmus vyžaduje váhy (Dijkstrov, Bellman-Ford, A*), aplikácia overí, či sú váhy správne nastavené. Ak nie, zobrazí sa upozornenie a váhy sa deaktivujú (nebudú zobrazené).\n"
            "3. Pomocou tlačidiel 'Pridať vrchol' a 'Pridať hranu' môžete vytvoriť vlastný graf, alebo načítať vzorový graf cez menu 'Súbor'.\n"
            "4. Po spustení algoritmu sa krok za krokom zobrazí, čo sa deje – aktualizované hrany (zelená) a hrany bez aktualizácie (červená, so šikmým štýlom) sú animované.\n"
            "5. Použite tlačidlá 'Predošlý krok' a 'Nasledujúci krok' na prechod medzi jednotlivými krokmi a sledujte detailný popis v postrannom paneli.\n"
            "6. Pri prejdení myšou nad vrcholami sa zobrazí tooltip s informáciou o vrchole.\n\n"
            "Tipy:\n"
            " - Ak algoritmus vyžaduje orientovaný graf, ale aktuálny graf je neorientovaný, zobrazí sa upozornenie.\n"
            " - Ak niektorá hrana nemá nastavenú váhu (alebo je nečíselná), váhy budú deaktivované a algoritmus bude používať predvolenú hodnotu 1.\n\n"
            "Užite si učenie a objavujte, ako fungujú grafové algoritmy!"
        )
        tutorial_text.insert(tk.END, tutorial_message)
        tutorial_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphVisualizerApp(root)
    root.mainloop()
