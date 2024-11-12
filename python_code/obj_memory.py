import networkx as nx
import pickle
import os
import shutil
import time
from flask_socketio import emit
from python_code.parsers import *
from python_code.prompts import *
from python_code.keys import *
import numpy as np
import faiss

class obj_node_class:
    def __init__(self):
        return 
class rela_node_class:
    def __init__(self):
        return
    
class memory:
    def __init__(self, name):
        self.filename = name
        self.G = nx.DiGraph()
        self.history = []
        self.dim = 256

        self.instance_embedding = np.zeros((0, self.dim), dtype='float32')
        return 

    def save(self):
        with open(self.filename, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as file:
            return pickle.load(file)
    