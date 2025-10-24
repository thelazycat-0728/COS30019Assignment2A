import sys
from bfs import BFS
from dfs import DFS
from dijkstra import CUS1
from gbfs import GBFS
from astar import AS
from idastar import CUS2

def open_file(fname):
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

if __name__ == "__main__":

    if len(sys.argv) != 3:
        raise SystemExit("Usage: python search.py <filename> <method>")
    
    filename = sys.argv[1]
    method = sys.argv[2]      

    graph = open_file(filename)
    print(graph)
    
    algorithm_map = {
        'bfs': BFS,
        'dfs': DFS,
        'dijkstra': CUS1,
        'gbfs': GBFS,
        'astar': AS,
        'a*': AS,
        'idastar': CUS2,
        'ida*': CUS2
    }



    # spelling must be correct ya... (or else it won't run :D)
    try:
        searcher = algorithm_map[method](graph)
    except KeyError:
        raise SystemExit(f"Unknown method: {method}")
    
    number_of_nodes, path, goal = searcher.search() 

    if method not in algorithm_map:
        raise SystemExit(f"Unknown method: {method}")


    if path is None:
        path = "Not found"
        
    print("Finished execution of search.py")
    print(f"Results: \n\n Filename: {filename} \n Method: {algorithm_map[method].__name__} \n Goal: {goal} \n Number of Nodes: {number_of_nodes} \n Path: {path}")