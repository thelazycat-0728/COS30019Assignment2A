import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import deque
import threading
import time

from bfs import BFS
from dfs import DFS
from dijkstra import CUS1
from gbfs import GBFS
from astar import AS
from idastar import CUS2


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Search Algorithm Visualizer")
        self.root.geometry("1600x900")
        
        self.graph = None
        self.search_tree = []
        self.solution_path = None
        self.is_running = False
        self.is_paused = False
        self.node_counter = 0
        self.node_ids = {}

        # Tooltip management
        self.hover_tooltip = None
        self.hover_timer = None
        self.fade_timer = None
        self.tooltip_alpha = 0.0
        self.current_hover_node = None
        self.bound = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Top control panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # File selection
        ttk.Label(control_frame, text="File:").grid(row=0, column=0, padx=5)
        self.file_entry = ttk.Entry(control_frame, width=40)
        self.file_entry.grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)
        
        # Algorithm selection
        ttk.Label(control_frame, text="Algorithm:").grid(row=0, column=3, padx=5)
        self.algorithm_var = tk.StringVar(value="bfs")
        algorithms = ["bfs", "dfs", "dijkstra", "gbfs", "astar", "idastar"]
        algo_menu = ttk.Combobox(control_frame, textvariable=self.algorithm_var, 
                                 values=algorithms, state="readonly", width=15)
        algo_menu.grid(row=0, column=4, padx=5)
        
        # Speed control
        ttk.Label(control_frame, text="Speed (s):").grid(row=0, column=5, padx=5)
        self.speed_var = tk.DoubleVar(value=0.5)
        speed_scale = ttk.Scale(control_frame, from_=0.1, to=2.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL, length=100)
        speed_scale.grid(row=0, column=6, padx=5)
        self.speed_label = ttk.Label(control_frame, text="0.5")
        self.speed_label.grid(row=0, column=7, padx=5)
        self.speed_var.trace_add('write', lambda *args: self.speed_label.config(text=f"{self.speed_var.get():.2f}"))
        
        # Control buttons
        self.run_button = ttk.Button(control_frame, text="▶ Run", command=self.run_search)
        self.run_button.grid(row=0, column=8, padx=5)
        
        self.pause_button = ttk.Button(control_frame, text="⏸ Pause", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=9, padx=5)
        
        self.reset_button = ttk.Button(control_frame, text="↺ Reset", command=self.reset_visualization, state=tk.DISABLED)
        self.reset_button.grid(row=0, column=10, padx=5)
        
        # Main content area
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Graph visualization with scrollbars
        left_frame = ttk.LabelFrame(content_frame, text="Graph Visualization", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Add scrollbars for graph canvas
        graph_scroll_y = ttk.Scrollbar(left_frame, orient=tk.VERTICAL)
        graph_scroll_x = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL)
        
        self.graph_canvas = tk.Canvas(left_frame, bg="white", width=600, height=600,
                                      yscrollcommand=graph_scroll_y.set,
                                      xscrollcommand=graph_scroll_x.set)
        
        graph_scroll_y.config(command=self.graph_canvas.yview)
        graph_scroll_x.config(command=self.graph_canvas.xview)
        
        graph_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        graph_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right side - Search tree and info
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Search tree
        tree_frame = ttk.LabelFrame(right_frame, text="Search Tree", padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Add scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.tree_canvas = tk.Canvas(tree_frame, bg="white", 
                                     yscrollcommand=tree_scroll_y.set,
                                     xscrollcommand=tree_scroll_x.set)
        tree_scroll_y.config(command=self.tree_canvas.yview)
        tree_scroll_x.config(command=self.tree_canvas.xview)
        
        # Bind scroll events to update bound label position
        self.tree_canvas.bind('<Configure>', self.update_bound_label_position)
        tree_scroll_y.config(command=lambda *args: (self.tree_canvas.yview(*args), self.update_bound_label_position()))
        tree_scroll_x.config(command=lambda *args: (self.tree_canvas.xview(*args), self.update_bound_label_position()))
        
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Status panel
        status_frame = ttk.LabelFrame(right_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(5, 5))
        
        self.status_text = tk.Text(status_frame, height=6, width=50, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Results panel
        results_frame = ttk.LabelFrame(right_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.X)
        
        self.results_text = tk.Text(results_frame, height=8, width=50, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select graph file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            self.load_graph(filename)
    
    def load_graph(self, filename):
        try:
            self.graph = self.open_file(filename)
            self.draw_graph()
            messagebox.showinfo("Success", "Graph loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load graph: {str(e)}")
            print(e)
    
    def open_file(self, fname):
        graph = {
            'nodes': {},
            'adjacency_list': {},
            'origin': None,
            'destinations': []
        }
        
        with open(fname, 'r') as file:
            lines = file.readlines()
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line == "Nodes:":
                current_section = "nodes"
                continue
            elif line == "Edges:":
                current_section = "edges"
                continue
            elif line == "Origin:":
                current_section = "origin"
                continue
            elif line == "Destinations:":
                current_section = "destinations"
                continue
            
            if current_section == "nodes":
                parts = line.split(': ')
                node_id = int(parts[0])
                coords = parts[1].strip('()').split(',')
                x, y = int(coords[0]), int(coords[1])
                graph['nodes'][node_id] = (x, y)
                graph['adjacency_list'][node_id] = []
            
            elif current_section == "edges":
                parts = line.split(': ')
                edge = parts[0].strip('()').split(',')
                from_node = int(edge[0])
                to_node = int(edge[1])
                cost = int(parts[1])
                
                if from_node not in graph['adjacency_list']:
                    graph['adjacency_list'][from_node] = []
                graph['adjacency_list'][from_node].append((to_node, cost))
            
            elif current_section == "origin":
                graph['origin'] = int(line)
            
            elif current_section == "destinations":
                dest_list = line.split(';')
                graph['destinations'] = [int(d.strip()) for d in dest_list]
        
        for node in graph['adjacency_list']:
            graph['adjacency_list'][node].sort(key=lambda x: x[0])
        
        return graph
    
    def draw_graph(self, highlight_current=None, highlight_frontier=None, highlight_path=None):
        if not self.graph:
            return
        
        self.graph_canvas.delete("all")
        
        nodes = self.graph['nodes']
        if not nodes:
            return
        
        xs = [coord[0] for coord in nodes.values()]
        ys = [coord[1] for coord in nodes.values()]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        padding = 60
        canvas_width = self.graph_canvas.winfo_width() or 600
        canvas_height = self.graph_canvas.winfo_height() or 600
        
        scale_x = (canvas_width - 2 * padding) / (max_x - min_x) if max_x != min_x else 1
        scale_y = (canvas_height - 2 * padding) / (max_y - min_y) if max_y != min_y else 1
        scale = min(scale_x, scale_y)
        
        # Calculate actual drawing area needed
        drawing_width = (max_x - min_x) * scale + 2 * padding
        drawing_height = (max_y - min_y) * scale + 2 * padding
        
        # Make canvas larger if needed, but at least the window size
        scroll_width = max(canvas_width, drawing_width)
        scroll_height = max(canvas_height, drawing_height)
        
        # Set scroll region
        self.graph_canvas.config(scrollregion=(0, 0, scroll_width, scroll_height))
        
        def transform(x, y):
            tx = padding + (x - min_x) * scale
            ty = scroll_height - (padding + (y - min_y) * scale)
            return tx, ty
        
        # Helper function to check if edge is bidirectional
        def is_bidirectional(from_node, to_node):
            """Check if there's a reverse edge"""
            if to_node in self.graph['adjacency_list']:
                for neighbor, _ in self.graph['adjacency_list'][to_node]:
                    if neighbor == from_node:
                        return True
            return False
        
        # Draw solution path edges first (if available)
        if highlight_path:
            for i in range(len(highlight_path) - 1):
                from_node = highlight_path[i]
                to_node = highlight_path[i + 1]
                x1, y1 = transform(*nodes[from_node])
                x2, y2 = transform(*nodes[to_node])
                
                # Calculate direction vector
                dx = x2 - x1
                dy = y2 - y1
                length = (dx**2 + dy**2)**0.5
                
                r = 22
                
                if length > 0:
                    ux = dx / length
                    uy = dy / length
                    start_x = x1 + ux * r
                    start_y = y1 + uy * r
                    end_x = x2 - ux * r
                    end_y = y2 - uy * r
                else:
                    start_x, start_y = x1, y1
                    end_x, end_y = x2, y2
                
                # Check if bidirectional
                bidirectional = is_bidirectional(from_node, to_node)
                
                if bidirectional:
                    # No arrow for bidirectional
                    self.graph_canvas.create_line(start_x, start_y, end_x, end_y,
                                                 fill="yellow", width=4)
                else:
                    # Arrow at 25% point for unidirectional
                    arrow_x = start_x + (end_x - start_x) * 0.25
                    arrow_y = start_y + (end_y - start_y) * 0.25
                    
                    # Draw line in two parts: before arrow and after arrow
                    self.graph_canvas.create_line(start_x, start_y, arrow_x, arrow_y,
                                                 fill="yellow", width=4, arrow=tk.LAST,
                                                 arrowshape=(10, 12, 5))
                    self.graph_canvas.create_line(arrow_x, arrow_y, end_x, end_y,
                                                 fill="yellow", width=4)
        
        # Draw edges
        drawn_edges = set()  # Track drawn edges to avoid duplicates
        
        for from_node, neighbors in self.graph['adjacency_list'].items():
            x1, y1 = transform(*nodes[from_node])
            for to_node, cost in neighbors:
                # Skip if we've already drawn this edge pair
                if (min(from_node, to_node), max(from_node, to_node)) in drawn_edges:
                    continue
                
                x2, y2 = transform(*nodes[to_node])
                
                # Calculate direction vector
                dx = x2 - x1
                dy = y2 - y1
                length = (dx**2 + dy**2)**0.5
                
                # Node radius
                r = 22
                
                # Calculate start and end points (outside the node circles)
                if length > 0:
                    # Unit vector
                    ux = dx / length
                    uy = dy / length
                    
                    # Start point (just outside from_node)
                    start_x = x1 + ux * r
                    start_y = y1 + uy * r
                    
                    # End point (just at edge of to_node)
                    end_x = x2 - ux * r
                    end_y = y2 - uy * r
                else:
                    start_x, start_y = x1, y1
                    end_x, end_y = x2, y2
                
                # Check if bidirectional
                bidirectional = is_bidirectional(from_node, to_node)
                
                if bidirectional:
                    # Draw simple line without arrow for bidirectional edges
                    self.graph_canvas.create_line(start_x, start_y, end_x, end_y,
                                                 fill="gray", width=2)
                    drawn_edges.add((min(from_node, to_node), max(from_node, to_node)))
                else:
                    # Arrow at 25% point for unidirectional edges
                    arrow_x = start_x + (end_x - start_x) * 0.25
                    arrow_y = start_y + (end_y - start_y) * 0.25
                    
                    # Draw line in two parts: before arrow and after arrow
                    self.graph_canvas.create_line(start_x, start_y, arrow_x, arrow_y,
                                                 fill="gray", width=2, arrow=tk.LAST,
                                                 arrowshape=(10, 12, 5))
                    self.graph_canvas.create_line(arrow_x, arrow_y, end_x, end_y,
                                                 fill="gray", width=2)
                
                # Calculate midpoint for cost label
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                
                # Calculate perpendicular offset
                if length > 0:
                    # Perpendicular vector (rotated 90 degrees)
                    perp_x = -dy / length
                    perp_y = dx / length
                    
                    # Offset distance from the line
                    offset = 12
                    
                    if bidirectional:
                        # For bidirectional: show both costs
                        
                        text_x_top = mid_x - perp_x * offset
                        text_y_top = mid_y - perp_y * offset
                        
                        label_top = tk.Label(
                            self.graph_canvas, 
                            text=str(cost), 
                            bg="white", 
                            fg="blue", 
                            font=("Arial", 9, "bold")
                        )
                        self.graph_canvas.create_window(text_x_top, text_y_top, window=label_top)
                        
                        
                        reverse_cost = None
                        if to_node in self.graph['adjacency_list']:
                            for neighbor, edge_cost in self.graph['adjacency_list'][to_node]:
                                if neighbor == from_node:
                                    reverse_cost = edge_cost
                                    break
                        
                        
                        if reverse_cost is not None:
                            text_x_bottom = mid_x + perp_x * offset
                            text_y_bottom = mid_y + perp_y * offset
                            
                            label_bottom = tk.Label(
                                self.graph_canvas, 
                                text=str(reverse_cost), 
                                bg="white", 
                                fg="blue", 
                                font=("Arial", 9, "bold")
                            )
                            self.graph_canvas.create_window(text_x_bottom, text_y_bottom, window=label_bottom)
                    else:
                        # For unidirectional: show single cost
                        text_x = mid_x + perp_x * offset
                        text_y = mid_y + perp_y * offset
                        
                        label = tk.Label(
                            self.graph_canvas, 
                            text=str(cost), 
                            bg="white", 
                            fg="blue", 
                            font=("Arial", 9, "bold")
                        )
                        self.graph_canvas.create_window(text_x, text_y, window=label)
                else:
                    text_x = mid_x
                    text_y = mid_y + 12
                    
                    label = tk.Label(
                        self.graph_canvas, 
                        text=str(cost), 
                        bg="white", 
                        fg="blue", 
                        font=("Arial", 9, "bold")
                    )
                    self.graph_canvas.create_window(text_x, text_y, window=label)
        
        # Draw nodes
        for node_id, (x, y) in nodes.items():
            tx, ty = transform(x, y)
            
            # Determine color
            if highlight_current and node_id == highlight_current:
                color = "orange"
                outline_width = 4
            elif highlight_path and node_id in highlight_path:
                color = "yellow"
                outline_width = 3
            elif highlight_frontier and node_id in highlight_frontier:
                color = "lightyellow"
                outline_width = 3
                outline_width = 2
            elif node_id == self.graph['origin']:
                color = "green"
                outline_width = 2
            elif node_id in self.graph['destinations']:
                color = "red"
                outline_width = 2
            else:
                color = "white"
                outline_width = 2
            
            r = 22
            self.graph_canvas.create_oval(tx - r, ty - r, tx + r, ty + r, 
                                         fill=color, outline="black", width=outline_width)
            self.graph_canvas.create_text(tx, ty, text=str(node_id), 
                                         font=("Arial", 12, "bold"))
        
        # Draw legend
        legend_x, legend_y = 10, 10
        self.graph_canvas.create_rectangle(legend_x, legend_y, legend_x + 180, legend_y + 120, 
                                          fill="white", outline="black", width=2)
        
        items = [
            ("green", "Origin"),
            ("red", "Destination"),
            ("lightblue", "Visited"),
            ("orange", "Current"),
            ("lightyellow", "Frontier")
        ]
        
        for i, (color, label) in enumerate(items):
            y_offset = legend_y + 10 + i * 22
            self.graph_canvas.create_oval(legend_x + 10, y_offset, legend_x + 28, y_offset + 18, 
                                          fill=color, outline="black")
            self.graph_canvas.create_text(legend_x + 95, y_offset + 9, text=label, anchor=tk.W,
                                         font=("Arial", 9))

    
    def run_search(self):
        if not self.graph:
            messagebox.showwarning("Warning", "Please load a graph file first!")
            return
        
        if self.is_running:
            return
        
        self.is_running = True
        self.is_paused = False
        self.run_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        
        # Reset tree tracking
        self.search_tree = []
        self.node_counter = 0
        self.node_ids = {}
        
        # Run search in separate thread
        thread = threading.Thread(target=self.execute_search)
        thread.daemon = True
        thread.start()
    
    def execute_search(self):
        algorithm = self.algorithm_var.get()
        
        algorithm_map = {
            'bfs': BFS,
            'dfs': DFS,
            'dijkstra': CUS1,
            'gbfs': GBFS,
            'astar': AS,
            'idastar': CUS2
        }
        
        try:
            if algorithm in algorithm_map:
                searcher = algorithm_map[algorithm](self.graph)

                self.current_bound = None

                
                # Run with callback
                number_of_nodes, path, goal = searcher.search(step_callback=self.step_callback)
                
                self.solution_path = path
                
                # Display final results
                self.root.after(0, self.display_results, algorithm, number_of_nodes, path, goal)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.root.after(0, messagebox.showerror, "Error", f"Search failed: {str(e)}")
        finally:
            self.is_running = False
            self.root.after(0, self.run_button.config, {"state": tk.NORMAL})
            self.root.after(0, self.pause_button.config, {"state": tk.DISABLED})
    
    def step_callback(self, current_node, neighbor, path, frontier, is_goal, g_cost=None, h_cost=None, bound=None, pruned=False):
        """Called by search algorithm at each step"""
        # Wait if paused
        while self.is_paused and self.is_running:
            time.sleep(0.1)
        
        if not self.is_running:
            return
        
        # For IDAstar reset step
        if current_node is None and not path:
            # reset internal tree state
            self.search_tree = []
            self.node_counter = 0
            self.node_ids = {}

            # prepare empty step data to update GUI (clears tree_canvas and redraws graph)
            step_data = {
                'current_node': None,
                'neighbor': None,
                'path': [],
                'frontier': frontier or [],
                'is_goal': False,
                'tree_data': [],
                'g_cost': None,
                'h_cost': None,
                'bound': bound,
                'pruned': False
            }
            # update GUI on main thread
            self.root.after(0, self.update_visualization_step, step_data)
            return
        
        # Build tree structure
        self.build_tree_from_path(path, current_node, neighbor, is_goal, g_cost, h_cost, pruned)

        

        # Create step data
        step_data = {
            'current_node': current_node,
            'neighbor': neighbor,
            'path': path,
            'frontier': frontier,
            'is_goal': is_goal,
            'tree_data': [node.copy() for node in self.search_tree],
            'g_cost': g_cost,
            'h_cost': h_cost,
            'bound': bound,
            'pruned': pruned
        }


        # Update GUI in main thread
        self.root.after(0, self.update_visualization_step, step_data)
        
        # Delay for visualization
        time.sleep(self.speed_var.get())
    
    # ...existing code...

    def build_tree_from_path(self, path, current_node, neighbor, is_goal, g_cost=None, h_cost=None, pruned=False):
        """Build/update search tree from current path"""
        
        # Add nodes in path if not already added
        for i, node in enumerate(path):
            
            node_key = (node, i)  # Key is (node_value, depth) to differentiate same nodes in different paths
            
            if node_key not in self.node_ids:
                node_id = self.node_counter
                self.node_counter += 1
                self.node_ids[node_key] = node_id
                
                parent_id = None
                if i > 0:
                    parent_key = (path[i-1], i-1)
                    parent_id = self.node_ids.get(parent_key)
                
                # Determine initial state based on THIS specific path
                if is_goal and node == current_node and i == len(path) - 1:
                    # Only mark as solution if it's the last node in the goal path
                    state = 'solution'
                elif node == current_node and i == len(path) - 1:
                    # Currently being expanded (last node in current path)
                    state = 'current'
                elif node == neighbor and i == len(path) - 1:
                    if pruned:
                        state = 'visited'  # Pruned - exceeds bound  (ONLY FOR IDASTAR)
                    else:
                        state = 'frontier'  # Normal frontier node
                else:
                    # Nodes earlier in the path
                    state = 'visited'
                
                node_g = g_cost if node == neighbor and i == len(path) - 1 else None
                node_h = h_cost if node == neighbor and i == len(path) - 1 else None
                
                self.search_tree.append({
                    'id': node_id,
                    'node': node,
                    'parent': parent_id,
                    'cost': i,
                    'state': state,
                    'g': node_g,
                    'h': node_h,
                    'path_id': id(path)  # Store path identifier
                })
            else:
                # Update state of existing node in THIS specific path position
                node_id = self.node_ids[node_key]
               
                for tree_node in self.search_tree:
                    if tree_node['id'] == node_id:
                        # Only update if it's part of the current operation
                        if is_goal and node in path:
                            tree_node['state'] = 'solution'
                        elif node == neighbor:
                            tree_node['g'] = g_cost
                            tree_node['h'] = h_cost

                            # This is for IDASTAR
                            if pruned:
                                tree_node['state'] = 'visited'
                            else:
                                tree_node['state'] = 'frontier'
                        elif i < len(path) - 1:  # Nodes before current in path
                            tree_node['state'] = 'visited'

                        break
        
        # Mark all nodes in solution path when goal is found
        if is_goal:
            # Only mark nodes in THIS specific path
            for i, node in enumerate(path):
                node_key = (node, i)
                if node_key in self.node_ids:
                    node_id = self.node_ids[node_key]
                    for node_data in self.search_tree:
                        if node_data['id'] == node_id:
                            node_data['state'] = 'solution'
                            break


    
    def update_visualization_step(self, step_data):
        """Update GUI with current step"""
        # Update graph
        if step_data.get('bound') is not None:
            self.current_bound = step_data['bound']

        highlight_path = step_data['path'] if step_data['is_goal'] else None
        self.draw_graph(
            highlight_current=step_data['current_node'],
            highlight_frontier=step_data['frontier'],
            highlight_path=highlight_path
        )
        
        # Update search tree
        self.search_tree = step_data['tree_data']
        self.draw_search_tree()
        
        # Update status
        self.update_status(step_data)
    
    def update_status(self, step_data):
        self.status_text.delete(1.0, tk.END)
        
        status = f"Current Node: {step_data['current_node']}\n"
        status += f"Current Path: {' → '.join(map(str, step_data['path']))}\n"
        status += f"Frontier Size: {len(step_data['frontier'])}\n"
        status += f"Frontier: {step_data['frontier'][:10]}"
        if len(step_data['frontier']) > 10:
            status += f"... (+{len(step_data['frontier']) - 10} more)"
        status += f"\nTree Nodes: {len(step_data['tree_data'])}\n"

        if step_data.get('g_cost') is not None:
            status += f"g(n): {step_data['g_cost']:.2f}\n"
        if step_data.get('h_cost') is not None:
            status += f"h(n): {step_data['h_cost']:.2f}\n"
        if step_data.get('g_cost') is not None and step_data.get('h_cost') is not None:
            status += f"f(n): {step_data['g_cost'] + step_data['h_cost']:.2f}\n"
        
        self.status_text.insert(1.0, status)
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text="▶ Resume")
        else:
            self.pause_button.config(text="⏸ Pause")
    
    def reset_visualization(self):
        self.is_running = False
        self.is_paused = False
        self.search_tree = []
        self.solution_path = None
        self.node_counter = 0
        self.node_ids = {}
        
        self.tree_canvas.delete("all")
        self.status_text.delete(1.0, tk.END)
        self.results_text.delete(1.0, tk.END)
        
        if self.graph:
            self.draw_graph()
        
        self.run_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="⏸ Pause")
        self.reset_button.config(state=tk.DISABLED)
    
    def display_results(self, algorithm, num_nodes, path, goal):
        self.results_text.delete(1.0, tk.END)
        
        result_text = f"Algorithm: {algorithm.upper()}\n"
        result_text += f"Goal Reached: {goal}\n"
        result_text += f"Nodes Created: {num_nodes}\n"
        result_text += f"Path: {' → '.join(map(str, path)) if path else 'Not found'}\n"
        
        if path:
            cost = 0
            for i in range(len(path) - 1):
                from_node = path[i]
                to_node = path[i + 1]
                for neighbor, edge_cost in self.graph['adjacency_list'].get(from_node, []):
                    if neighbor == to_node:
                        cost += edge_cost
                        break
            result_text += f"Path Cost: {cost}\n"
            result_text += f"Path Length: {len(path)} nodes\n"
        
        self.results_text.insert(1.0, result_text)
    
    def draw_search_tree(self):
        if not self.search_tree:
            # Even if tree is empty, draw bound if it exists (for IDA* between iterations)
            if self.current_bound is not None and self.algorithm_var.get() == 'idastar':
                self.tree_canvas.delete("all")
                self.draw_bound_label()
            return
        
        self.tree_canvas.delete("all")
        
        levels = self.organize_tree_by_levels()
        
        if not levels:
            return
        
        level_height = 80  # Increased for labels
        node_spacing = 80  # Increased for labels
        start_y = 40
        
        max_width = max(len(level) for level in levels) * node_spacing
        canvas_width = max(800, max_width + 100)
        canvas_height = len(levels) * level_height + 100
        
        self.tree_canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
        
        node_positions = {}
        
        # Draw tree level by level
        for level_idx, level_nodes in enumerate(levels):
            y = start_y + level_idx * level_height
            num_nodes = len(level_nodes)
            total_width = num_nodes * node_spacing
            start_x = (canvas_width - total_width) / 2
            
            for idx, node_data in enumerate(level_nodes):
                x = start_x + idx * node_spacing
                node_positions[node_data['id']] = (x, y)
                
                # Draw edge to parent with arrow
                if node_data['parent'] is not None and node_data['parent'] in node_positions:
                    px, py = node_positions[node_data['parent']]
                    edge_color = "yellow" if node_data['state'] == 'solution' else "gray"
                    edge_width = 3 if node_data['state'] == 'solution' else 2
                    
                    # Calculate direction vector
                    dx = x - px
                    dy = y - py
                    length = (dx**2 + dy**2)**0.5
                    
                    r = 16  # Node radius
                    
                    if length > 0:
                        # Unit vector
                        ux = dx / length
                        uy = dy / length
                        
                        # Start point (just outside parent node)
                        start_x_edge = px + ux * r
                        start_y_edge = py + uy * r
                        
                        # End point (just at edge of child node)
                        end_x = x - ux * r
                        end_y = y - uy * r
                        
                        # Draw line with arrow pointing to child
                        self.tree_canvas.create_line(start_x_edge, start_y_edge, end_x, end_y, 
                                                    fill=edge_color, width=edge_width,
                                                    arrow=tk.LAST, arrowshape=(10, 12, 5))
                    else:
                        # Fallback if nodes are at same position
                        self.tree_canvas.create_line(px, py, x, y, fill=edge_color, width=edge_width)
                
                # Determine node color based on THIS node's specific state in its path
                state = node_data.get('state', 'frontier')
                if state == 'solution':
                    color = "yellow"
                elif state == 'visited':
                    color = "lightblue"
                elif state == 'frontier':
                    color = "lightyellow"
                elif state == 'current':
                    color = "orange"
                else:
                    # Check if this specific node instance is origin or destination
                    if node_data['node'] == self.graph['origin'] and node_data.get('cost', 0) == 0:
                        color = "green"
                    elif node_data['node'] in self.graph['destinations']:
                        color = "red"
                    else:
                        color = "white"
                
                # Draw node
                r = 16
                self.tree_canvas.create_oval(x - r, y - r, x + r, y + r, 
                                            fill=color, outline="black", width=2)
                self.tree_canvas.create_text(x, y, text=str(node_data['node']), 
                                            font=("Arial", 9, "bold"))
                
                # Draw g, h, f values to the right of the node if they exist
                if node_data.get('g') is not None or node_data.get('h') is not None:
                    value_lines = []
                    
                    if node_data.get('g') is not None:
                        value_lines.append(f"g={node_data['g']:.2f}")
                    
                    if node_data.get('h') is not None:
                        value_lines.append(f"h={node_data['h']:.2f}")
                    
                    if node_data.get('g') is not None and node_data.get('h') is not None:
                        f_val = node_data['g'] + node_data['h']
                        value_lines.append(f"f={f_val:.2f}")
                    
                    # Draw values to the right of node
                    value_text = "\n".join(value_lines)
                    text_x = x + r + 5  # 5 pixels to the right of node
                    
                    # Create background for better readability
                    temp_text = self.tree_canvas.create_text(
                        text_x, y,
                        text=value_text,
                        font=("Arial", 7, "bold"),
                        anchor=tk.W
                    )
                    bbox = self.tree_canvas.bbox(temp_text)
                    self.tree_canvas.delete(temp_text)
                    
                    if bbox:
                        # Draw white background rectangle
                        padding = 2
                        self.tree_canvas.create_rectangle(
                            bbox[0] - padding, bbox[1] - padding,
                            bbox[2] + padding, bbox[3] + padding,
                            fill="white", outline="gray", width=1
                        )
                    
                    # Draw text on top of background
                    self.tree_canvas.create_text(
                        text_x, y,
                        text=value_text,
                        font=("Arial", 7, "bold"),
                        anchor=tk.W,
                        fill="darkblue"
                    )
        
        # Draw IDA* bound at bottom left if applicable
        if self.current_bound is not None and self.algorithm_var.get() == 'idastar':
            self.draw_bound_label()
    
    def draw_bound_label(self):
        """Draw the current bound label at the fixed bottom-left corner of the visible canvas"""
        if self.current_bound is None or self.algorithm_var.get() != 'idastar':
            return
        
        # Get canvas scroll position
        canvas_width = self.tree_canvas.winfo_width()
        canvas_height = self.tree_canvas.winfo_height()
        
        # Get current scroll position (what's visible)
        x_view = self.tree_canvas.xview()
        y_view = self.tree_canvas.yview()
        
        # Calculate the visible region coordinates
        scroll_region = self.tree_canvas.cget('scrollregion').split()
        if scroll_region:
            total_width = float(scroll_region[2])
            total_height = float(scroll_region[3])
            
            # Calculate visible area in canvas coordinates
            visible_left = x_view[0] * total_width
            visible_top = y_view[0] * total_height
            visible_bottom = visible_top + canvas_height
            
            # Position bound label at bottom-left of visible area
            label_x = visible_left + 10
            label_y = visible_bottom - 10
        else:
            # Fallback if no scroll region
            label_x = 10
            label_y = canvas_height - 10
        
        bound_text = f"Current Bound: {self.current_bound:.2f}"
        
        # Create background rectangle
        temp_text = self.tree_canvas.create_text(
            label_x, label_y,
            text=bound_text,
            font=("Arial", 12, "bold"),
            anchor=tk.SW
        )
        bbox = self.tree_canvas.bbox(temp_text)
        self.tree_canvas.delete(temp_text)
        
        if bbox:
            padding = 4
            self.tree_canvas.create_rectangle(
                bbox[0] - padding, bbox[1] - padding,
                bbox[2] + padding, bbox[3] + padding,
                fill="white", outline="darkred", width=2,
                tags="bound_label"
            )
        
        # Draw text on top
        self.tree_canvas.create_text(
            label_x, label_y,
            text=bound_text,
            font=("Arial", 12, "bold"),
            fill="darkred",
            anchor=tk.SW,
            tags="bound_label"
        )
    
    def update_bound_label_position(self, event=None):
        """Update bound label position when canvas is scrolled"""
        if self.current_bound is not None and self.algorithm_var.get() == 'idastar':
            # Delete old bound label
            self.tree_canvas.delete("bound_label")
            # Redraw at new position
            self.draw_bound_label()
    
                
    def organize_tree_by_levels(self):
        if not self.search_tree:
            return []
        
        levels = []
        visited = set()
        queue = deque()
        
        # Find root
        root = None
        for node in self.search_tree:
            if node['parent'] is None:
                root = node
                break
        
        if not root:
            return []
        
        queue.append((root, 0))
        visited.add(root['id'])
        
        while queue:
            node, level = queue.popleft()
            
            if level >= len(levels):
                levels.append([])
            
            levels[level].append(node)
            
            # Find children
            children = []
            for child in self.search_tree:
                if child['parent'] == node['id'] and child['id'] not in visited:
                    children.append(child)
                    visited.add(child['id'])
            
            # For DFS, reverse children order to show right-to-left
            
            if self.algorithm_var.get() == 'dfs':
                children.reverse()
            
            # Add children to queue
            for child in children:
                queue.append((child, level + 1))
        
        return levels


