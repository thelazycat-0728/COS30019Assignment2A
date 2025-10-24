from search_algorithms import SearchAlgorithms
from utils import make_heuristics
import math

# IDA* Algorithm Implementation
class CUS2(SearchAlgorithms):
    def __init__(self, graph):
        super().__init__(graph)
        self.total_generated_nodes = 0
        self.h = make_heuristics(self.coords, self.goals)

    def iterate(self, node, g, bound, path, visited):
        """Recursive DFS with f-cost bound"""
        f = g + self.h(node)

        
        # Exceeds bound - return new threshold
        if f > bound:
            return f, None, None
        
      
        min_excess = math.inf
        
        # Explore neighbors
        for neighbor, cost in self.graph['adjacency_list'][node]:
            if neighbor in visited:
                continue
            
            if neighbor in self.goals:
                return [True, neighbor, path + [neighbor]]
            
            visited.add(neighbor)
            self.total_generated_nodes += 1
            
            result, goal_node, goal_path = self.iterate(
                neighbor, 
                g + cost, 
                bound, 
                path + [neighbor],
                visited
            )
            
            # Goal found
            if result is True:
                return True, goal_node, goal_path
            
            # Track minimum f-cost that exceeded bound
            if isinstance(result, (int, float)) and result < min_excess:
                min_excess = result
            
            visited.remove(neighbor)  # Backtrack
        
        return min_excess, None, None

    def search(self):
        """IDA* search with iterative deepening"""
        # Initial bound is heuristic estimate from start
        bound = self.h(self.start)
        self.total_generated_nodes = 1
        path = [self.start]

        if self.start in self.goals:
            return [self.total_generated_nodes, path, self.start]
        
        while True:
            
            if self.total_generated_nodes != 1:
                self.total_generated_nodes += 1
            
            visited = {self.start}
            
            outcome, goal_node, goal_path = self.iterate(
                self.start, 
                0.0, 
                bound, 
                path,
                visited
            )
            
            # Goal found
            if outcome is True:
                return [self.total_generated_nodes, goal_path, goal_node]
            
            # No solution exists
            if outcome == math.inf:
                return [self.total_generated_nodes, None, None]
            
            # Increase bound and try again
            bound = outcome