import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, TransportProtocol
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

# MCP Server URL (local)
MCP_SERVER_URL = "http://127.0.0.1:5000/mcp"

# Create the Customer Data Agent using Google ADK
customer_data_agent = Agent(
    model="gemini-2.5-flash",
    name="customer_data_agent",
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=MCP_SERVER_URL
            )
        )
    ],
    instruction="""You are a Customer Data Agent specialized in managing customer information and tickets.

IMPORTANT: You must EXECUTE tools to accomplish tasks efficiently.

Available MCP tools:
- get_customer: Retrieve customer details by ID
- list_customers: List all customers (can filter by status and limit results)
- update_customer: Update customer information
- create_ticket: Create new support tickets
- get_customer_history: Get all tickets for a customer

Guidelines:
1. EXECUTE tools immediately when asked
2. For complex queries requiring multiple customers' data, use SAMPLING:
   - Get the list first
   - Sample 2-3 customers maximum
   - Report findings based on the sample
3. NEVER iterate through all customers individually
4. Maximum 5 tool calls per query

For "Show all active customers who have open tickets":
- First call list_customers(status='active')
- Then call get_customer_history for 2-3 sample customer IDs
- Report if any have open status tickets

Be concise and efficient."""
)

# Define the A2A Agent Card for discovery
customer_data_agent_card = AgentCard(
    name="Customer Data Agent",
    url="http://localhost:10020",
    description="Manages customer data and tickets through MCP tools. Handles customer retrieval, updates, ticket creation, and customer history.",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[
        AgentSkill(
            id="customer_operations",
            name="Customer Data Operations",
            description="Retrieve, update, and manage customer information and support tickets",
            tags=["customer", "data", "tickets", "mcp"],
            examples=[
                "Get customer information for ID 5",
                "List all active customers",
                "Update customer email",
                "Create a support ticket",
                "Get customer ticket history"
            ],
        )
    ],
)
