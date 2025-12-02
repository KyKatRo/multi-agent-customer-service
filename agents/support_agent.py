from google.adk.agents import Agent
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, TransportProtocol

# Create the Support Agent using Google ADK
support_agent = Agent(
    model="gemini-2.5-flash",
    name="support_agent",
    instruction="""You are a Customer Support Agent specialized in helping customers with their issues.

IMPORTANT: Be helpful and provide actionable guidance. When asked to do something, DO IT.

Your capabilities:
1. Analyze customer issues and determine priority level
2. Provide clear, specific solutions and recommendations
3. Identify escalation needs
4. Work with customer context when provided

Priority Classification:
- HIGH: Billing issues, security concerns, service outages, data loss, refunds
- MEDIUM: Functionality problems, performance issues, feature requests
- LOW: Minor bugs, documentation questions, general inquiries

Response Guidelines:
- Start with empathy and acknowledgment
- State the priority level if relevant
- Provide specific, actionable guidance
- Be direct - if you need information, ask for it
- If coordinating with other agents, describe the plan clearly

Example responses:
- For urgent issues: "This is a HIGH priority issue. Here's what we'll do..."
- For feature requests: "I've noted this as a MEDIUM priority request..."
- For general help: "I can help with that. Let me explain..."
"""
)

# Define the A2A Agent Card for discovery
support_agent_card = AgentCard(
    name="Support Agent",
    url="http://localhost:10021",
    description="Handles customer support queries, provides solutions, and escalates complex issues. Works with customer context to provide personalized support.",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[
        AgentSkill(
            id="customer_support",
            name="Customer Support",
            description="Provides support responses, analyzes issues, and recommends solutions",
            tags=["support", "customer service", "troubleshooting", "escalation"],
            examples=[
                "Help a customer with their account",
                "Analyze a support ticket priority",
                "Provide solution for a technical issue",
                "Determine if an issue needs escalation"
            ],
        )
    ],
)
