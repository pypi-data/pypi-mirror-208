import random
from pathlib import Path
from statistics import mean

import mesa
import networkx as nx
import mesa_geo as mg

from .util import createData

from .agents import SenderAgent, RegionAgent
from .space import Nuts2Eu

datafolder = Path(__file__).parent.parent.resolve()


def getComponents(model):
    return nx.number_connected_components(model.G.to_undirected())


def getMoves(model):
    return model.movements


class HistoricalLetters(mesa.Model):
    """A letter sending model with historical informed initital positions.
    
    Each agent has an initial topic vector, expressed as a RGB value. The 
    initial positions of the agents is based on a weighted random draw
    based on data from [1]
    
    Each step, agents generate two neighbourhoods for sending letters and 
    potential targets to move towards. The probability to send letters is 
    a self-reinforcing process. During each sending the internal topic of 
    the sender is updated as a random rotation towards the receivers topic.

    [1] J. Lobo et al, Population-Area Relationship for Medieval European Cities,
        PLoS ONE 11(10): e0162678.
    """
    def __init__(
        self, population=100, moveRange=0.5, letterRange=0.5,
        threshold=0.5, updateTopic=0.1,
    ):
        super().__init__()

        self.schedule = mesa.time.RandomActivation(self)
        self.space = Nuts2Eu()
        self.population = population
        self.letterLedger = list()
        self.G = nx.DiGraph()
        self.G.add_nodes_from([x for x in range(self.population)])
        self.nodeindex = {i: node for i, node in enumerate(self.G.nodes())}
        self.grid = mesa.space.NetworkGrid(self.G)
        self.movements = 0
        self.updatedTopic = 0
        self.personRegionMap = dict()

        createData(population)

        self.factors = dict(
            updateTopic=updateTopic,
            threshold=threshold,
            moveRange=moveRange,
            letterRange=letterRange,
        )

        # Set up the grid with patches for every NUTS region
        ac = mg.AgentCreator(RegionAgent, model=self)
        self.regions = ac.from_file(
            Path(datafolder, "data/nuts_rg_60M_2013_lvl_2.geojson"),
            unique_id="NUTS_ID"
        )
        self.space.add_regions(self.regions)

        # Set up agent creator for senders
        ac_senders = mg.AgentCreator(
            SenderAgent,
            model=self,
            agent_kwargs=self.factors
        )

        # Create agents based on random coordinates.
        senders = ac_senders.from_file(
            Path(datafolder, "data/agentsCoordinates.geojson"),
            unique_id="unique_id"
        )

        # Create random set of initial topic vectors.
        topics = [
            tuple(
                [random.random() for x in range(3)]
            ) for x in range(self.population)
        ]

        # Attach topic to each agent.
        for idx, sender in enumerate(senders):
            sender.topicVec = topics[idx]

        for agent in senders:
            self.space.add_sender(agent)
            self.schedule.add(agent)

        # Calculate mean of mean distances for each agent. 
        # This is used as a measure for the range of exchanges.
        borderAgent = self.population - 1
        agentsp = self.space.get_agents_as_GeoDataFrame()[-borderAgent:]
        distances = []
        for source in agentsp.geometry.values:
            agentdistances = [source.distance(x) for x in agentsp.geometry.values]
            meanDist = mean(agentdistances)
            distances.append(meanDist)
        self.meandistance = mean(distances)

        # TODO: What comparitive values are useful for visualizations?
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Movements": getMoves,
                "Graph components": getComponents,
            },
        )

    def step(self):
        self.schedule.step()
        nx.spring_layout(self.G)
        self.datacollector.collect(self)

    def run(self, n):
        """Run the model for n steps."""
        for _ in range(n):
            self.step()
