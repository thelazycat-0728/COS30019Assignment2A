class SearchAlgorithms:
    def __init__(self, graph):
        self.graph = graph
        self.start = graph['origin']
        self.goals = set(graph['destinations'])
        self.coords = graph['nodes']


    def search(self):
        raise NotImplementedError("This method should be overridden by subclasses.")



