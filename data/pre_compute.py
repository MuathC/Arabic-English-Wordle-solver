import sys
import os

# Add the root project directory to sys.path so we can access 'agents'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you should be able to import 'agents'
from agents.entropy_agent import EntropyAgent

# Initialize the agent
agent = EntropyAgent()


if not agent:
    print("Entropy caching failed.")
    
agent = EntropyAgent(language="ar")


if not agent:
    print("Entropy caching failed.")
