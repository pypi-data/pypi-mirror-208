import random
import numpy as np
from shapely.geometry import LineString

import mesa
import mesa_geo as mg


class SenderAgent(mg.GeoAgent):

    def __init__(
        self, unique_id, model, geometry, crs, updateTopic, threshold, moveRange, letterRange
    ):
        super().__init__(unique_id, model, geometry, crs)
        self.region_id = 'FR62'
        self.updateTopic = updateTopic
        self.threshold = threshold
        self.moveRange = moveRange
        self.letterRange = letterRange
        self.topicLedger = []
        self.lettersReceived = []
        self.numLettersReceived = 0
        self.lettersSend = []
        self.numLettersSend = 0

    def move(self, neighbors):
        """The agent can randomly move to neighboring positions."""
        if neighbors:
            # Random decision to move or not, weights are 10% moving, 90% staying.
            move = random.choices([0, 1], weights=[0.9, 0.1], k=1)
            if move[0] == 1:
                self.model.movements += 1
                weights = []
                possible_steps = []
                # Weighted random choice to target of moving.
                # Strong receivers are more likely targets.
                for n in neighbors:
                    if n != self:
                        possible_steps.append(n.geometry)
                        weights.append(n.numLettersReceived)
                if sum(weights) > 0:
                    lineEndPoint = random.choices(possible_steps, weights, k=1)
                else:
                    lineEndPoint = random.choices(possible_steps, k=1)
                lineSegment = LineString([self.geometry, lineEndPoint[0]])
                next_position = lineSegment.interpolate(random.random(), normalized=True)
                self.model.space.move_sender(self, next_position)

    @property
    def has_topic(self):
        """Current topic of the agent."""
        return self.topicVec

    def has_letter_contacts(self, neighbors=False):
        """List of already established and potential contacts.

        Implements the ego-reinforcing by allowing mutliple entries
        of the same agent. In neighbourhods agents are added proportional
        to the number of letters they received, thus increasing the reinforcement.
        """
        contacts = []
        senders = self.lettersReceived
        receivers = self.lettersSend
        contacts.extend(senders)
        contacts.extend(receivers)
        if neighbors:
            neighborRec = []
            for n in neighbors:
                if n != self:
                    # TODO: We could here exclude already listed receivers/senders?!
                    if n.numLettersReceived > 0:
                        nMult = [n] * n.numLettersReceived
                        neighborRec.extend(nMult)
                    else:
                        neighborRec.append(n)
            contacts.extend(neighborRec)
        return contacts

    def chooses_topic(self, receiver):
        """Choose the topic to write about in the letter.

        Agents can choose to write a topic from their own ledger or
        in relation to the topics of the receiver. The choice is random."""
        topicChoices = self.topicLedger.copy()
        topicChoices.extend(receiver.topicLedger.copy())
        if topicChoices:
            initTopic = random.choices(topicChoices)
        else:
            initTopic = self.topicVec
        return initTopic

    def sendLetter(self, neighbors):
        """Sending a letter based on an urn model."""
        contacts = self.has_letter_contacts(neighbors)
        if contacts:
            # Randomly choose from the list of possible receivers
            receiver = random.choice(contacts)
            if isinstance(receiver, SenderAgent):
                initTopic = self.chooses_topic(receiver)
                # Calculate distance between own chosen topic 
                # and current topic of receiver.
                # TODO: Rethink this step!
                distance = np.linalg.norm(np.array(receiver.topicVec) - np.array(initTopic))
                # If the calculated distance falls below a threshold,
                # send the letter.
                if distance < self.threshold:
                    receiver.numLettersReceived += 1
                    receiver.lettersReceived.append(self.unique_id)
                    self.numLettersSend += 1
                    self.lettersSend.append(receiver.unique_id)
                    # Update model social network
                    self.model.G.add_edge(self.unique_id, receiver.unique_id)
                    self.model.G.nodes()[self.unique_id]['numLettersSend'] = self.numLettersSend
                    self.model.G.nodes()[receiver.unique_id][
                        'numLettersReceived'
                    ] = receiver.numLettersReceived
                    # Update agents topic vector as a weighted sum
                    # of the original sender topic and a scaled 
                    # random projection of the sender topic towards 
                    # the receiver topic.
                    updateTopicVec = self.topicVec + self.updateTopic * np.random.uniform(0, 1) * (np.array(receiver.topicVec) - np.array(self.topicVec))
                    self.model.letterLedger.append(
                        (
                            self.unique_id, receiver.unique_id, self.geometry, receiver.geometry,
                            updateTopicVec, self.model.schedule.steps
                        )
                    )
                    self.topicLedger.append(
                        self.topicVec
                    )
                    self.topicVec = updateTopicVec
                    self.model.updatedTopic += 1

    def step(self):
        neighborsMove = [
            x for x in self.model.space.get_neighbors_within_distance(
                self,
                distance=self.moveRange * self.model.meandistance,
                center=False
            ) if isinstance(x, SenderAgent)
        ]
        neighborsSend = [
            x for x in self.model.space.get_neighbors_within_distance(
                self,
                distance=self.letterRange * self.model.meandistance,
                center=False
            ) if isinstance(x, SenderAgent)
        ]
        self.sendLetter(neighborsSend)
        self.move(neighborsMove)


class RegionAgent(mg.GeoAgent):
    init_num_people: int
    persons_in_region: list

    def __init__(self, unique_id, model, geometry, crs, init_num_people=0):
        super().__init__(unique_id, model, geometry, crs)
        self.init_num_people = init_num_people
        self.persons_in_region = list()

    def has_main_topic(self):
        if len(self.persons_in_region) > 0:
            topics = [x.topicVec for x in self.persons_in_region]
            total = [x.numLettersReceived for x in self.persons_in_region]
            if sum(total) > 0:
                weight = [x / sum(total) for x in total]
            else:
                weight = [0.1] * len(topics)
            mixed_colors = np.sum([np.multiply(weight[i], topics[i]) for i in range(len(topics))], axis=0)
            colors_inverse = np.subtract((1, 1, 1), mixed_colors)
            return colors_inverse
        else:
            return (0.5, 0.5, 0.5)
    
    def add_person(self, person):
        self.persons_in_region.append(person)

    def remove_person(self, person):
        self.persons_in_region.remove(person)


class SenderNode(mesa.Agent):
    """An agent representing the network node.

    Only necessary for visualization purposes.
    """

    def __init__(
        self,
        unique_id,
        model,
        topicVec
    ):
        """Create letter with position, topic vector and parameters."""
        super().__init__(unique_id, model)
        self.topicVec = topicVec
        self.lettersReceived = 0
        self.lettersSend = 0
