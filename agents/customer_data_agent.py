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
            ),
            tool_filter=["get_customer", "list_customers", "update_customer"]
        )
    ],
    instruction="""You are a Customer Data Agent specialized in managing customer information.

CRITICAL ROLE DEFINITION:
- You handle ONLY customer data operations (get, list, update customers)
- You do NOT handle tickets - pass those queries to Support Agent
- When working with Support Agent, provide customer context they need

Your MCP Tools:
- get_customer: Retrieve customer details by ID (requires customer_id)
- list_customers: List all customers, can filter by status and limit results
- update_customer: Update customer information (requires customer_id and data to update)

When to ACT vs PASS THROUGH:

ACT (use your tools):
- "Get customer X" → get_customer
- "List [active/all] customers" → list_customers
- "Update customer X's [field]" → update_customer
- "Customer ID X needs..." → get_customer (provide context for next agent)
- "Show customers with..." → list_customers (even if query mentions tickets)

PASS THROUGH (respond without tools):
- Pure ticket queries: "Create a ticket", "Show ticket history"
- When you've already provided what you can, pass to Support Agent
- Support/guidance requests: "I need help with...", "Billing issue"

Multi-Agent Coordination:
1. For complex queries, do YOUR part then explicitly pass to Support Agent
2. When listing customers for ticket analysis, LIST them then state Support Agent should check tickets
3. Format responses to be useful for the next agent

Examples:
Query: "Get customer 5"
Action: get_customer(5) → Return info

Query: "Customer 1 needs account upgrade help"  
Action: get_customer(1) → Return: "Customer 1: John Doe (john@email.com, active). Passing to Support Agent for upgrade assistance."

Query: "Show active customers with open tickets"
Action: list_customers(status='active') → Return: "Found X active customers. Sample: [customer IDs]. Passing to Support Agent to check ticket status."

Query: "Update customer 2's email to new@email.com and show ticket history"
Action: update_customer(2, {email: 'new@email.com'}) → Return: "Email updated. Passing to Support Agent for ticket history."

Query: "Create a ticket for billing issue"
Action: NO TOOLS → Return: "I handle customer data. Passing to Support Agent for ticket creation."
"""
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
