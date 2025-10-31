from search_algorithms import SearchAlgorithms
from utils import make_heuristics
import math

# IDA* Algorithm Implementation
class CUS2(SearchAlgorithms):
    def __init__(self, graph):
        super().__init__(graph)
        self.total_generated_nodes = 0
        self.h = make_heuristics(self.coords, self.goals)

    def iterate(self, current_node, g, bound, path, frontier=None, step_callback=None):
        
        """Recursive DFS with f-cost bound"""
        frontier.remove(current_node)
        f = g + self.h(current_node)

        

        if current_node in self.goals:
            return True, current_node, path

        # Exceeds bound - return new threshold
        if f > bound:
            return f, None, None
        
      
        min_excess = math.inf
        neighbor_list = []
        # Explore neighbors
        for neighbor, cost in self.graph['adjacency_list'][current_node]:

            if neighbor in path:
                continue
            
            neighbor_list.append(neighbor)
            self.total_generated_nodes += 1

            if neighbor not in self.frontier:
                self.frontier.append(neighbor)
            if step_callback:
                step_callback(current_node, neighbor, path + [neighbor], self.frontier, False, g + cost, self.h(neighbor), bound)

        
        for neighbor in neighbor_list:
            result, goal_node, goal_path = self.iterate(
                neighbor, 
                g + cost, 
                bound, 
                path + [neighbor],
                frontier=self.frontier,
                step_callback=step_callback
            )


            # Goal found
            if result is True:
                return True, goal_node, goal_path
            
            # Track minimum f-cost that exceeded bound
            if isinstance(result, (int, float)) and result < min_excess:
                min_excess = result
            
            
        return min_excess, None, None

    def search(self, step_callback=None):
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
            
            
            outcome, goal_node, goal_path = self.iterate(
                self.start, 
                0.0, 
                bound, 
                path,
                frontier=[self.start],
                step_callback=step_callback
            )
            
            # Goal found
            is_goal = goal_node in self.goals

            # If goal is found, return immediately after showing the solution
            if is_goal:
                cost = 0

                # Calculate g cost of the found path
                for i in range(len(goal_path) - 1):
                    from_node = goal_path[i]
                    to_node = goal_path[i + 1]
                    for neighbor, edge_cost in self.graph['adjacency_list'].get(from_node, []):
                        if neighbor == to_node:
                            cost += edge_cost
                            break

                if step_callback:
                    step_callback(goal_node, None, goal_path, self.frontier,  is_goal, cost, self.h(goal_node), bound)
                return [self.total_generated_nodes, goal_path, goal_node]

            # No solution exists
            if outcome == math.inf:
                return [self.total_generated_nodes, None, None]
            
            # Increase bound and try again
            bound = outcome

            self.frontier = []
            
            if step_callback:
                step_callback(None, [], self.frontier, False, None, None, bound)
