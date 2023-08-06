import mesa
import numpy as np


class LetterAgent(mesa.Agent):
    """An agent with fixed initial start position.
  
    Each agent has a personal topic vector representing
    the shares the agent has of topics 1 to 10 with values
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
        unique_id,
        model,
        pos,
        topicVec,
        updateTopic,
        moveRange,
        letterRange,
        minSep,
        threshold
    ):
        """Create letter with position, topic vector and parameters."""
        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.topicVec = topicVec
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
            weights = []
            possible_steps = []
            for n in neighbors:
                possible_steps.append(n.pos)
                weights.append(n.lettersReceived)
            move = np.random.choice([0, 0, 0, 0, 0, 0, 0, 1])
            if move == 1:
                new_position = self.random.choice(possible_steps)
                self.model.space.move_agent(self, new_position)
  
    def sendLetter(self, neighbors):
        """Sending a letter based on an urn model."""
        possibleRec = []
        senders = self.lettersReceived
        receivers = self.lettersSend
        possibleRec.extend(senders)
        possibleRec.extend(receivers)
        if neighbors:
            neighborRec = []
            for n in neighbors:
                if n.numLettersReceived > 0:
                    nMult = [n.unique_id] * n.numLettersReceived
                    neighborRec.extend(nMult)
                else:
                    neighborRec.append(n.unique_id)
            possibleRec.extend(neighborRec)
        if possibleRec:
            recipientNr = np.random.choice(possibleRec)
            recipient = self.model.schedule.agents[recipientNr]
            topicChoices = self.topicLedger.copy()
            topicChoices.extend(recipient.topicLedger.copy())
            if topicChoices:
                randix = np.random.choice(list(range(len(topicChoices))))
                initTopic = topicChoices[randix]
            else:
                initTopic = self.topicVec
            distance = np.linalg.norm(recipient.topicVec - initTopic)
            if distance < self.threshold:
                recipient.numLettersReceived += 1
                recipient.lettersReceived.append(self.unique_id)
                self.numLettersSend += 1
                self.lettersSend.append(recipient.unique_id)
                # Update model social network
                self.model.G.add_edge(self.unique_id, recipient.unique_id)
                self.model.G.nodes()[self.unique_id]['numLettersSend'] = self.numLettersSend
                self.model.G.nodes()[recipient.unique_id]['numLettersReceived'] = recipient.numLettersReceived
                # Update agents topic vector
                updateTopicVec = self.topicVec + self.updateTopic * np.random.uniform(0, 1) * (recipient.topicVec - self.topicVec)
                self.model.letterLedger.append(
                    (self.unique_id, recipient.unique_id, self.pos, recipient.pos, updateTopicVec, self.model.schedule.steps)
                )
                self.topicLedger.append(
                    self.topicVec
                )
                self.topicVec = updateTopicVec
               
    def step(self):
        neighborsMove = self.model.space.get_neighbors(self.pos, self.moveRange, False)
        neighborsSend = self.model.space.get_neighbors(self.pos, self.letterRange, False)
        self.sendLetter(neighborsSend)
        self.move(neighborsMove)


class LetterNode(mesa.Agent):
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
