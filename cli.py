from bfs import BFS
from dfs import DFS
from dijkstra import CUS1
from gbfs import GBFS
from astar import AS
from idastar import CUS2
import gc
import time
import tracemalloc

class CLI:
    def __init__ (self, file_path, method):
        self.graph = self.open_file(file_path)
        self.file_path = file_path
        self.method = method
        self.algorithm_map = {
            'bfs': BFS,
            'dfs': DFS,
            'dijkstra': CUS1,
            'gbfs': GBFS,
            'astar': AS,
            'a*': AS,
            'idastar': CUS2,
            'ida*': CUS2
        }

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
            
        # Skip empty lines
        if not line:
            continue
        
        # Identify sections
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
        
        # Parse based on current section
        if current_section == "nodes":
            # Format: "1: (4,1)"
            parts = line.split(': ')
            node_id = int(parts[0])
            coords = parts[1].strip('()').split(',')
            x, y = int(coords[0]), int(coords[1])
            graph['nodes'][node_id] = (x, y)
            # Initialize empty adjacency list for each node
            graph['adjacency_list'][node_id] = []
        
        elif current_section == "edges":
            # Format: "(2,1): 4"
            parts = line.split(': ')
            edge = parts[0].strip('()').split(',')
            from_node = int(edge[0])
            to_node = int(edge[1])
            cost = int(parts[1])
            
            # Build adjacency list: store (neighbor, cost)
            if from_node not in graph['adjacency_list']:
                graph['adjacency_list'][from_node] = []
            graph['adjacency_list'][from_node].append((to_node, cost))
        
        elif current_section == "origin":
            graph['origin'] = int(line)
        
        elif current_section == "destinations":
            # Format: "5; 4"
            dest_list = line.split(';')
            graph['destinations'] = [int(d.strip()) for d in dest_list]
      
      for node in graph['adjacency_list']:
          graph['adjacency_list'][node].sort(key=lambda x: x[0])

      return graph
    

    def search(self):
        try:
            searcher = self.algorithm_map[self.method](self.graph)
        except KeyError:
            raise SystemExit(f"Unknown method: {self.method}")
        
        gc.collect() # Force garbage collection before starting the timer
        start_time = time.perf_counter()
        tracemalloc.start()

        initial_mem = tracemalloc.get_traced_memory()[0]
        number_of_nodes, path, goal = searcher.search() 

        end_time = time.perf_counter()
        memory_used, peak_mem = tracemalloc.get_traced_memory()

        tracemalloc.stop()

        if self.method not in self.algorithm_map:
            raise SystemExit(f"Unknown method: {self.method}")


        if path is None:
            path = "Not found"
        
        print("Finished execution of search.py")
        print(f"Results: \n\n Filename: {self.file_path} \n Method: {self.algorithm_map[self.method].__name__} \n Goal: {goal} \n Number of Nodes: {number_of_nodes} \n Path: {path}")

        print(f"Total memory usage: {memory_used / 1024} KB")
        print(f"Peak memory usage: {peak_mem / 1024} KB")
        print(f"Execution time: {(end_time - start_time) * 1000} milliseconds")

       



  
        