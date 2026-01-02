import ctypes
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001

ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.frequency_agent import FrequencyAgent
from agents.CSP_agent import CSP_agent
from agents.entropy_agent import EntropyAgent
from agents.bayesian_agent import BayesianAgent



from benchmark.benchmark import main,avg

if __name__ == "__main__":

    tested_agents = [BayesianAgent,CSP_agent,FrequencyAgent,BayesianAgent]
    
    
    avg(100,100,tested_agents,'ar')
