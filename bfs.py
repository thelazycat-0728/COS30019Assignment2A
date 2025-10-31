from search_algorithms import SearchAlgorithms
from collections import deque

class BFS(SearchAlgorithms):
    def search(self, step_callback=None):
        
        number_of_nodes = 1  # Count the origin node
        queue = deque([(self.start, [self.start])])  # (current_node, path_to_current_node)

        while queue:
            
            current_node, path = queue.popleft()

           
            self.frontier.remove(current_node)
       
            
            # Check if goal is reached
            is_goal = current_node in self.goals
            
           
            # If goal is found, return immediately after showing the solution
            if is_goal:
                for node in queue:
                    if node[0] not in self.frontier:               
                        self.frontier.append(node[0])
                if step_callback:
                    step_callback(current_node, None, path, self.frontier, is_goal)
                return [number_of_nodes, path, current_node]
            
            # Explore neighbors
            for neighbor, cost in self.graph['adjacency_list'][current_node]:
                if neighbor not in path:     
                    number_of_nodes += 1
                    

                    new_path = path + [neighbor]
                    queue.append((neighbor, new_path))
                    for node in queue:
                        if node[0] not in self.frontier:
                            self.frontier.append(node[0])
                    if step_callback:
                        step_callback(current_node, neighbor, new_path, self.frontier, is_goal)
                 
        # If no path found, still show final state
        if step_callback:
            step_callback(current_node, None, path, [], False)
            
        return [number_of_nodes, None, None]  # No path found