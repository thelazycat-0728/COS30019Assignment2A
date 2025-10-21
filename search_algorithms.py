from collections import deque
import heapq

class SearchAlgorithms:
    def __init__(self, graph):
        self.graph = graph
        self.start = graph['origin']
        self.goals = set(graph['destinations'])

    def bfs(self):
        visited = set()
        number_of_nodes = 1  # Count the origin node
        visited.add(self.start)

        if self.start in self.goals:
            return [number_of_nodes, [self.start], self.start]

        queue = deque([(self.start, [self.start])])  # (current_node, path_to_current_node)

        while queue:
            current_node, path = queue.popleft()

            if (current_node in self.goals):
                return [number_of_nodes, path, current_node]  # Return the path to the goal
        
            # Use adjacency list instead of edges dictionary
            for neighbor, cost in self.graph['adjacency_list'][current_node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    number_of_nodes += 1
                    
                    new_path = path + [neighbor]
                    
                    queue.append((neighbor, new_path))

        return [number_of_nodes, None, None]  # No path found
    


    def dfs(self):
        visited = set()
        number_of_nodes = 1  # Count the origin node
        visited.add(self.start)

        # LIFO stack for DFS
        stack = [(self.start, [self.start])]  # (current_node, path_to_current_node)

        while stack:
            current_node, path = stack.pop()

            if current_node in self.goals:
                return [number_of_nodes, path, current_node]  # Return the path to the goal
            
           
            # Ensure first node not entered twice
            if (number_of_nodes != 1 ):
                visited.add(current_node)

            # Smaller valued nodes are processed first
            for neighbor, cost in reversed(self.graph['adjacency_list'][current_node]):
                if neighbor not in visited:
                    number_of_nodes += 1

                    
                    new_path = path + [neighbor]
                    stack.append((neighbor, new_path))

        return [number_of_nodes, None, None]  # No path found
    
    def dijkstra(self):
        visited = set()
        number_of_nodes = 1  # Count the origin node
        distances = {self.start: 0}
        min_heap = [(0, self.start, [self.start])]  # (cost, current_node, path_to_current_node)

        while min_heap:


          
            cost, current_node, path = heapq.heappop(min_heap)

            if current_node in self.goals:
                visited.add(current_node)
                return [number_of_nodes, path, current_node]  # Return the path to the goal

            if current_node not in visited:
                visited.add(current_node)

                for neighbor, edge_cost in self.graph['adjacency_list'][current_node]:
                    if neighbor not in visited:
                        number_of_nodes += 1
                        new_cost = cost + edge_cost
                        if neighbor not in distances or new_cost < distances[neighbor]:
                            new_path = path + [neighbor]
                            distances[neighbor] = new_cost
                            heapq.heappush(min_heap, (new_cost, neighbor, new_path))

        return [number_of_nodes, None, None]  # No path found