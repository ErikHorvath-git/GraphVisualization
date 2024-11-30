import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphVisualizerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Graph Visualizer")
        self.graph = nx.Graph()
        self.positions = {}
        self.create_menu()
        self.create_canvas()
        self.create_status_bar()

    def create_menu(self):
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Graph", command=self.new_graph)
        file_menu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.master.config(menu=menubar)

    def create_canvas(self):
        self.figure = plt.Figure(figsize=(5, 4))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_axis_on()
        self.ax.grid(True)
        
        self.canvas = FigureCanvasTkAgg(self.figure, self.master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_status_bar(self):
        self.status = tk.StringVar()
        self.status.set("Welcome to the Graph Visualizer!")
        status_bar = tk.Label(self.master, textvariable=self.status, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def new_graph(self):
        self.graph.clear()
        self.positions.clear()
        self.update_status("New graph created.")
        self.draw_graph()

    def update_status(self, message):
        self.status.set(message)

    def draw_graph(self):
        self.ax.clear()
        self.ax.set_axis_on()
        self.ax.grid(True)
        
        if self.graph.nodes:
            nx.draw(self.graph, self.positions, ax=self.ax, with_labels=True, node_color='skyblue', node_size=500)
        
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphVisualizerApp(root)
    root.mainloop()
