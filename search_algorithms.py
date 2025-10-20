from collections import deque
class SearchAlgorithms:
    def __init__(self, graph):
        self.graph = graph

    def bfs(self):
      
      start = self.graph['origin']
      goals = set(self.graph['destinations'])
      visited = set()
      number_of_nodes = 0
      queue = deque([(start, [start])])  # (current_node, path_to_current_node)

      while queue:
        current_node, path = queue.popleft()

        if current_node in goals:
          return [number_of_nodes, path, current_node]  # Return the path to the goal

        if current_node not in visited:
          visited.add(current_node)

          for (from_node, to_node), cost in self.graph['edges'].items():
            if from_node == current_node and to_node not in visited:

              number_of_nodes += 1
              new_path = path + [to_node]
              queue.append((to_node, new_path))

      return None  # No path found