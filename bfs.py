from search_algorithms import SearchAlgorithms
from collections import deque

class BFS(SearchAlgorithms):
    def search(self, step_callback=None):
        visited = set()
        
        number_of_nodes = 1  # Count the origin node
        queue = deque([(self.start, [self.start])])  # (current_node, path_to_current_node)

        while queue:
            
            current_node, path = queue.popleft()

            if current_node in visited:
                self.frontier.remove(current_node)
                continue 
            
            self.frontier.remove(current_node)
            visited.add(current_node)
            
            # Check if goal is reached
            is_goal = current_node in self.goals
            
           
            # If goal is found, return immediately after showing the solution
            if is_goal:
                for node in queue:
                    if node[0] not in self.frontier:
                      
                        self.frontier.append(node[0])
                step_callback(current_node, path, self.frontier, visited, is_goal)
                return [number_of_nodes, path, current_node]
            
            # Explore neighbors
            for neighbor, cost in self.graph['adjacency_list'][current_node]:
                if neighbor not in visited:
                   
                    number_of_nodes += 1
                    new_path = path + [neighbor]
                    for node in queue:
                        if node[0] not in self.frontier:
                            self.frontier.append(node[0])

                    step_callback(current_node, new_path, self.frontier, visited, is_goal)
                    queue.append((neighbor, new_path))

    

        # If no path found, still show final state
        if step_callback:
            step_callback(current_node, path, [], visited, False)
            
        return [number_of_nodes, None, None]  # No path found