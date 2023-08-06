import mesa

from .model import LetterSpace
from .SimpleContinuousModule import SimpleCanvas


def letter_draw(agent):
    colortuple = set(agent.topicVec)
    color = "#" + "".join(format(int(round(val * 255)), "02x") for val in colortuple)
    probDict = {
        "Shape": "circle",
        "r": agent.numLettersReceived,
        "Filled": "true",
        "Color": color
    }
    return probDict


def node_draw(G):
    nodes = []
    node_label_to_node_id = {}
    node_id = 0
    # edge_id = 0
    for node_label, agents in G.nodes.data("agent"):
        node = G.nodes()[node_label]
        agent = agents[0]
        colortuple = set(agent.topicVec)
        nodes.append({
            "size": node["numLettersReceived"],
            "color": "#" + "".join(format(int(round(val * 255)), "02x") for val in colortuple),
            "tooltip": f"id: {agent.unique_id}<br>Topics: {agent.topicVec}",
        })
        node_label_to_node_id[node_label] = node_id
        node_id += 1

    portrayal = dict()
    portrayal["nodes"] = nodes
    edges = []
    for (source, target) in G.edges():
        sourceAgent = [agents for x, agents in G.nodes.data("agent") if x == source]
        agent = sourceAgent[0][0]
        edges.append({
            "source": node_label_to_node_id[source],
            "target": node_label_to_node_id[target],
            "color": '#D3D3D3',
            "width": G.nodes()[source]["numLettersSend"],
        }
        )
    portrayal["edges"] = edges

    return portrayal


letter_canvas = SimpleCanvas(letter_draw, 360, 720)

network_canvas = mesa.visualization.NetworkModule(node_draw, 360, 720)


model_params = {
    "population": mesa.visualization.Slider(
        "Number of persons",
        50,
        10,
        200,
        10,
        description="Choose how many persons to include in the model.",
    ),
    "updateTopic": mesa.visualization.Slider(
        "Strength of adoption",
        0.05,
        0.01,
        0.3,
        0.05,
        description="Choose how strongly letter sending changes ones topics.",
    ),
    "updateHelp": mesa.visualization.StaticText(
        "Higher value:<br/> A letter sender faster adopts to the topic of a receiver."
    ),
    "threshold": mesa.visualization.Slider(
        "Similarity threshold",
        0.5,
        0.0,
        1.0,
        0.1,
        description="Choose how similar two persons topics have to be, to send a letter.",
    ),
    "thresholdHelp": mesa.visualization.StaticText(
        "Higher value:<br/> Sending a letter is less likely."
    ),
    "width": 360,
    "height": 180,
    "moveRange": mesa.visualization.Slider(
        "Range for moving position",
        20,
        0,
        100,
        10,
        description="Choose the visibility range for finding potential locations to move to.",
    ),
    "letterRange": mesa.visualization.Slider(
        "Range for letter sending",
        50,
        0,
        150,
        10,
        description="Choose the visibility range for finding potential receipients.",
    ),
    "minSep": 3
}

server = mesa.visualization.ModularServer(
    LetterSpace, [letter_canvas, network_canvas], "Random Letters", model_params
)
