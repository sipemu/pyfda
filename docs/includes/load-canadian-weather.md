<!-- docs/includes/load-canadian-weather.md — FND-04 shared preamble snippet.
     Plain Python lines only: no fence delimiters, no markdown-exec attributes.
     The consuming fence provides the ```python ... ``` delimiters and
     attributes; the --8<-- line goes inside that fence body. -->
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather

day, X, meta = load_canadian_weather("temperature")
