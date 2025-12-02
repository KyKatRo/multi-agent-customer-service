from google.adk.agents import SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, TransportProtocol
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

# Create RemoteA2aAgent references to the specialist agents
remote_customer_data_agent = RemoteA2aAgent(
    name="customer_operations",
    description="Manages customer data and tickets through MCP tools",
    agent_card=f"http://localhost:10020{AGENT_CARD_WELL_KNOWN_PATH}",
)

remote_support_agent = RemoteA2aAgent(
    name="customer_support",
    description="Provides support responses and solutions",
    agent_card=f"http://localhost:10021{AGENT_CARD_WELL_KNOWN_PATH}",
)

# Create the Router Agent as a SequentialAgent
# SequentialAgent will automatically pass queries through sub-agents in sequence
router_agent = SequentialAgent(
    name="router_agent",
    sub_agents=[remote_customer_data_agent, remote_support_agent],
)

# Define the A2A Agent Card for the Router
router_agent_card = AgentCard(
    name="Router Agent",
    url="http://localhost:10022",
    description="Orchestrates customer service requests by analyzing queries and coordinating between Customer Data Agent and Support Agent using A2A protocol.",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[
        AgentSkill(
            id="orchestration",
            name="Multi-Agent Orchestration",
            description="Analyzes customer queries and coordinates between specialized agents to provide comprehensive responses",
            tags=["orchestration", "routing", "coordination", "a2a"],
            examples=[
                "Get customer information and help with their issue",
                "Update customer data and create a support ticket",
                "List customers and analyze their tickets",
                "Coordinate complex multi-step customer service tasks"
            ],
        )
    ],
)
