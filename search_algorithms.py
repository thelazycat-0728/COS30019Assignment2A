class SearchAlgorithms:
    def __init__(self, graph):
        self.graph = graph
        self.start = graph['origin']
        self.goals = set(graph['destinations'])
        self.coords = graph['nodes']
        self.frontier = [self.start]  # Initialize frontier with start node


    def search(self):
        raise NotImplementedError("This method should be overridden by subclasses.")
    

 
