import random
from typing import Dict, DefaultDict, Set
from collections import defaultdict

import mesa
import mesa_geo as mg
from shapely.geometry import Point

from .agents import RegionAgent, SenderAgent


class Nuts2Eu(mg.GeoSpace):
    _id_region_map: Dict[str, RegionAgent]
    _senders_pos_map: DefaultDict[mesa.space.FloatCoordinate, Set[SenderAgent]]
    _sender_id_map: Dict[int, SenderAgent]
    num_people: int

    def __init__(self):
        super().__init__(warn_crs_conversion=False)
        self._id_region_map = {}
        self._senders_pos_map = defaultdict(set)
        self._sender_id_map = dict()
        self.num_people = 0

    def add_regions(self, agents):
        super().add_agents(agents)
        total_area = 0
        for agent in agents:
            self._id_region_map[agent.unique_id] = agent
            total_area += agent.SHAPE_AREA
        for _, agent in self._id_region_map.items():
            agent.SHAPE_AREA = agent.SHAPE_AREA / total_area * 100.0

    def add_person_to_region(self, person, region_id):
        person.region_id = region_id
        self._id_region_map[region_id].add_person(person)
        self.num_people += 1

    def remove_person_from_region(self, person):
        self._id_region_map[person.region_id].remove_person(person)
        person.region_id = None
        self.num_people -= 1

    def add_sender(self, agent: SenderAgent) -> None:
        super().add_agents([agent])
        localregion = [x for x in self._id_region_map.values() if x.geometry.contains(agent.geometry)]
        # FIXME: Some new geometries are not contained in the nuts regions. 
        try:
            next_region = localregion[0].unique_id
        except:
            next_region = self.get_random_region_id()
        self.add_person_to_region(agent, next_region)
        self._senders_pos_map[(agent.geometry.x, agent.geometry.y)].add(agent)
        self._sender_id_map[agent.unique_id] = agent
        
    def move_sender(
        self, agent: SenderAgent, pos: mesa.space.FloatCoordinate
    ) -> None:
        self.__remove_sender(agent)
        agent.geometry = pos
        self.add_sender(agent)

    def __remove_sender(self, agent: SenderAgent) -> None:
        super().remove_agent(agent)
        del self._sender_id_map[agent.unique_id]
        self.remove_person_from_region(agent)
        self._senders_pos_map[(agent.geometry.x, agent.geometry.y)].remove(
            agent
        )

    def get_random_region_id(self) -> str:
        return random.choice(list(self._id_region_map.keys()))

    def get_region_by_id(self, region_id) -> RegionAgent:
        return self._id_region_map.get(region_id)
