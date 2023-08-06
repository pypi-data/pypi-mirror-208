import unittest
import pytest
from fastforward.__test__.metric.benchmark import benchmark
from fastforward.__test__.metric.profiler import Profiler
from fastforward.engine.listener.onnx_listener import OnnxListener
from fastforward.model_for_summarization import ModelForSummarization

@pytest.mark.skip(reason="no way of currently testing this")
class ModelForSummarizationTest(unittest.TestCase):

    def test_gpu(self):
        text = """Computer Space is a space-combat arcade game released in 1971. Created by Nolan Bushnell and 
        Ted Dabney in partnership as Syzygy Engineering, it was the first arcade video game and the first commercially 
        available video game. In the game the player controls a rocket engaged in a missile battle against a pair of 
        hardware-controlled flying saucers set against a starfield background."""
        text2 = """The goal is to score more hits than the 
        enemy within a set time period.The game is enclosed in a custom fiberglass cabinet, which Bushnell designed to 
        look futuristic. Bushnell and Dabney created the game to be a coin-operated version of Spacewar!, a 1962 
        computer game. They could not economically run the game o a general-purpose minicomputer, so they build 
        specialized hardware for the game."""
        text3 = """They ran their first location test in August 1971, and it was shown to 
        industry press and distributors at the annual Music Operators of America Expo in October. More than one thousand 
        cabinets were sold by mid-1972."""

        model = ModelForSummarization(
            "/home/christian/IdeaProjects/x-and-y/onnx-fabric/onnx_fabric/__tests__/distilbart-cnn-12-6-samsum/cuda-fp32")
        # benchmark("GPU", lambda: model([text, text2, text3], num_beams=2))
        model([text, text2, text3], num_beams=2)

    def test_distilbart_cnn_12_6_samsun(self):
        text = """Please close this task on success with closing reason "Direct solved" or "Solved" otherwise with an 
        other reason (e.g. "Aborted"). Create a new doorplate for room C 205 Start Date: 01.09.2019 Employee: 
        Max Mustermann Comment:"""

        with Profiler():
            listeners = [OnnxListener(enable_cpu_mem_arena=False)]
            model = ModelForSummarization.restore("x-and-y", "distilbart-cnn-12-6-samsum", "1.0.0", "cpu-fp32",
                                                  listeners=listeners)
            benchmark("distilbart", lambda: model(text, num_beams=2))

    def test_pegasus_xsum(self):
        text = """The tower is 324 metres (1,063 ft) tall, about the same height as an 81-storey building, and the 
        tallest structure in Paris. Its base is square, measuring 125 metres (410 ft) on each side. During its 
        construction, the Eiffel Tower surpassed the Washington Monument to become the tallest man-made structure in 
        the world, a title it held for 41 years until the Chrysler Building in New York City was finished in 1930. 
        It was the first structure to reach a height of 300 metres. Due to the addition of a broadcasting aerial at 
        the top of the tower in 1957, it is now taller than the Chrysler Building by 5.2 metres (17 ft). Excluding 
        transmitters, the Eiffel Tower is the second tallest free-standing structure in France after the Millau 
        Viaduct."""

        with Profiler():
            onnx_model = ModelForSummarization.restore("x-and-y", "pegasus-xsum", "1.0.0")
            print(onnx_model(text))

    def test_t5_small(self):
        text = """summarize: The tower is 324 metres (1,063 ft) tall, about the same height as an 81-storey building, and the 
        tallest structure in Paris. Its base is square, measuring 125 metres (410 ft) on each side. During its 
        construction, the Eiffel Tower surpassed the Washington Monument to become the tallest man-made structure in 
        the world, a title it held for 41 years until the Chrysler Building in New York City was finished in 1930. 
        It was the first structure to reach a height of 300 metres. Due to the addition of a broadcasting aerial at 
        the top of the tower in 1957, it is now taller than the Chrysler Building by 5.2 metres (17 ft). Excluding 
        transmitters, the Eiffel Tower is the second tallest free-standing structure in France after the Millau 
        Viaduct."""

        with Profiler():
            onnx_model = ModelForSummarization.restore("x-and-y", "t5-small", "1.0.0")
            print(onnx_model(text))
