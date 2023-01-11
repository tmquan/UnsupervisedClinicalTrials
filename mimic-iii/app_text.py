import os
import json
import base64
from io import BytesIO
from PIL import Image

import requests
import lightning as L
import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from functools import partial
from lightning_app.utilities.state import AppState
from lightning.app.components.serve import ServeGradio


class TextVisualizationServeGradio(ServeGradio):
    inputs = []
    inputs.append(
        gr.Textbox(lines=20, label=f"Context", placeholder="Type a sentence or paragraph here.")
    )
    outputs = []
    outputs.append(
        gr.Textbox(lines=20, label=f"Outputs", placeholder="")
        # gr.HighlightedText(
        #     value=[("Hermione", "first_name"), ("Jean Granger", "last_name")],
        #     elem_id="htext",
        #     label=f"Highlight",
        # ),
    )

    # examples = []
    import pandas as pd
    df = pd.read_csv(
        "data/NOTEEVENTS.csv",
        #     na_values=[ '', ' ', '?', '?|?','None', '-NaN', '-nan', '', 'N/A', 'NA', 'NULL', 'NaN', 'n/a', 'nan', 'null']
    )  # .fillna(np.nan)
    examples = df["TEXT"].to_list()[:10]

    def __init__(self, cloud_compute, *args, **kwargs):
        super().__init__(*args, cloud_compute=cloud_compute, **kwargs)
        self.ready = False  # required

    # Override original implementation to pass the custom css highlightedtext
    def run(self, *args, **kwargs):
        # if self._model is None:
        #     self._model = self.build_model()
        fn = partial(self.predict, *args, **kwargs)
        fn.__name__ = self.predict.__name__
        gr.Interface(
            fn=fn,
            # Override here
            css="#htext span {white-space: pre-wrap; word-wrap: normal}",
            inputs=self.inputs,
            outputs=self.outputs,
            examples=self.examples
        ).launch(
            server_name=self.host,
            server_port=self.port,
            enable_queue=self.enable_queue,
        )
    
    def build_model(self):
        pass
    
    def predict(self, text):
        return text

class LitRootFlow(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.textvis = TextVisualizationServeGradio(L.CloudCompute("cpu"), parallel=True)

    def configure_layout(self):
        tabs = []
        tabs.append({"name": "Text Visualization", "content": self.textvis})
        return tabs

    def run(self):
        self.textvis.run()


app = L.LightningApp(LitRootFlow())
