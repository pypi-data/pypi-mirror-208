import mesa
import numpy as np
import networkx as nx

from .agents import LetterAgent, LetterNode


class LetterSpace(mesa.Model):
    """
    Letter sending model class. Handles agent creation, placement and scheduling.

    Each agent has a personal topic vector representing
    the shares the agent has of topics 1 to 3 with values
    between 0 and 1.
    Each agent has two different ranges, moveRange for deciding
    to move to another agents position, and letterRange to find
    potential correspondence partners. In addition a threshold
    value determines the necessary similarity between topic vectors
    to send a letter or not.

    Received and send letters are kept track of with two additional
    internal variables.
    """

    def __init__(
        self,
        population=100,
        width=360,
        height=180,
        moveRange=20,
        letterRange=30,
        threshold=0.5,
        updateTopic=0.1,
        minSep=5
    ):
        """Create a new Letter model."""
        self.population = population
        self.letterLedger = list()
        self.schedule = mesa.time.RandomActivation(self)
        self.G = nx.DiGraph()
        self.G.add_nodes_from([x for x in range(self.population)])
        self.space = mesa.space.ContinuousSpace(width, height, True)
        self.grid = mesa.space.NetworkGrid(self.G)
        self.factors = dict(minSep=minSep, updateTopic=updateTopic, threshold=threshold, moveRange=moveRange, letterRange=letterRange)
        self.make_agents()
        self.running = True

    def make_agents(self):
        """
        Create self.population agents, with random positions and starting headings.
        """
        for i, node in enumerate(self.G.nodes()):
            x = self.random.random() * self.space.x_max
            y = self.random.random() * self.space.y_max
            pos = np.array((x, y))
            topicVec = np.array([np.random.random() for x in range(3)])  # Agent has random shares of topics 1 - 3 between 0 and 1.
            letter = LetterAgent(
                i,
                self,
                pos,
                topicVec,
                **self.factors
            )
            nx.set_node_attributes(self.G, {i: {'numLettersSend': 0, 'numLettersReceived': 0}})
            letterNode = LetterNode(
                i,
                self,
                topicVec,
            )
            self.space.place_agent(letter, pos)
            self.grid.place_agent(letterNode, node)
            self.schedule.add(letter)

    def step(self):
        self.schedule.step()
        nx.spring_layout(self.G)
    
    def run(self, n):
        """Run the model for n steps."""
        for _ in range(n):
            self.step()
