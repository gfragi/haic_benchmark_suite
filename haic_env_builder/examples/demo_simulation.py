import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.agent import Agent
from components.profile import Profile
from components.task import Task
from components.environment import Environment

def main():
    # Define agents
    agent1 = Agent(name="RadiologistAssistant", capabilities=["classify", "highlight", "summarize"], modality="text")
    agent2 = Agent(name="VoiceSupportBot", capabilities=["speak", "respond"], modality="audio")

    # Define user profiles
    profile1 = Profile(profile_id="user123", skill_level="expert", role="radiologist")
    profile2 = Profile(profile_id="user456", skill_level="novice", role="technician")

    # Define task
    task = Task(
        name="CT Scan Diagnosis",
        description="Review and diagnose CT scan results with AI assistance.",
        parameters={
            "image_type": "CT",
            "urgency": "high",
            "report_required": True
        }
    )

    # Create environment
    env = Environment(task=task, agents=[agent1, agent2], profiles=[profile1, profile2])

    # Run the mock simulation and print result
    result = env.run_simulation()
    print("=== Simulation Result ===")
    print(result)

if __name__ == "__main__":
    main()
