import matplotlib.colors as colors

import mesa
import mesa_geo as mg

from .agents import SenderAgent, RegionAgent
from .model import HistoricalLetters

model_params = {
    "population": 100,
    # "population": mesa.visualization.Slider(
    #     "Number of persons",
    #     100, 10, 200, 10,
    #     description="Choose how many persons to include in the model.",
    # ),
    "updateTopic": mesa.visualization.Slider(
        "Strength of adoption",
        0.05, 0.01, 0.3, 0.05,
        description="Choose how strongly letter sending changes ones topics.",
    ),
    "threshold": mesa.visualization.Slider(
        "Similarity threshold",
        0.5, 0.0, 1.0, 0.5,
        description="Choose how similar two persons topics have to be, to send a letter.",
    ),
    "moveRange": mesa.visualization.Slider(
        "Range for moving position</br>(% of mean agent distances)",
        0.5, 0, 1, 0.1,
        description="Choose the visibility range for finding potential locations to move to.",
    ),
    "letterRange": mesa.visualization.Slider(
        "Range for letter sending</br>(% of mean agent distances)",
        0.5, 0, 1, 0.1,
        description="Choose the visibility range for finding potential receipients.",
    ),
}


def topic_draw(agent):
    portrayal = {}
    if isinstance(agent, RegionAgent):
        try:
            color = colors.to_hex(agent.has_main_topic())
        except: 
            print(agent.has_main_topic())
            raise
        portrayal["color"] = color
    elif isinstance(agent, SenderAgent):
        colortuple = set(agent.topicVec)
        portrayal["radius"] = 5
        portrayal["shape"] = "circle"
        portrayal["color"] = colors.to_hex(colortuple)
        portrayal["description"] = str(agent.unique_id)
    return portrayal


map_element = mg.visualization.MapModule(
    portrayal_method=topic_draw,
    view=[52, 12],
    zoom=4,
    map_width=500,
    map_height=300,
)

chart = mesa.visualization.ChartModule(
    [
        {"Label": "Movements", "Color": "Red"},
        {"Label": "Graph components", "Color": "Orange"}
    ],
    data_collector_name='datacollector',
)


server = mesa.visualization.ModularServer(
    HistoricalLetters,
    [map_element, chart],
    "Historical Letters",
    model_params,
)
