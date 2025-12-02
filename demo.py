import os
import sys
import time
import asyncio
import threading
import logging
import warnings
from typing import Any, Dict
from dotenv import load_dotenv

warnings.filterwarnings('ignore', category=FutureWarning, module='google.api_core._python_version_support')
warnings.filterwarnings('ignore', category=FutureWarning, module='google.cloud.aiplatform.models')
warnings.filterwarnings('ignore', message='.*EXPERIMENTAL.*')

logging.getLogger('google.adk').setLevel(logging.ERROR)
logging.getLogger('google.genai').setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.basicConfig(level=logging.ERROR)

# Workaround for google-adk==1.9.0 compatibility with a2a-sdk==0.3.0
from a2a.client import client as real_client_module
from a2a.client.card_resolver import A2ACardResolver

class PatchedClientModule:
    def __init__(self, real_module) -> None:
        for attr in dir(real_module):
            if not attr.startswith('_'):
                setattr(self, attr, getattr(real_module, attr))
        self.A2ACardResolver = A2ACardResolver

patched_module = PatchedClientModule(real_client_module)
sys.modules['a2a.client.client'] = patched_module

import httpx
import nest_asyncio
import uvicorn

from a2a.client import ClientConfig, ClientFactory, create_text_message_object
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, TransportProtocol
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor, A2aAgentExecutorConfig
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService

from agents.customer_data_agent import customer_data_agent, customer_data_agent_card
from agents.support_agent import support_agent, support_agent_card
from agents.router_agent import router_agent, router_agent_card

import mcp_server

load_dotenv()
nest_asyncio.apply()


def start_mcp_server():
    """Start MCP server in background thread."""
    print("\n=== Starting MCP Server ===")
    mcp_server.start_mcp_server(host='127.0.0.1', port=5000)


def create_agent_a2a_server(agent, agent_card):
    """Create an A2A server for an ADK agent."""
    runner = Runner(
        app_name=agent.name,
        agent=agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )

    config = A2aAgentExecutorConfig()
    executor = A2aAgentExecutor(runner=runner, config=config)

    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )

    return A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )


async def run_agent_server(agent, agent_card, port):
    """Run a single agent A2A server."""
    app = create_agent_a2a_server(agent, agent_card)
    
    config = uvicorn.Config(
        app.build(),
        host='127.0.0.1',
        port=port,
        log_level='error',
        loop='none',
    )
    
    server = uvicorn.Server(config)
    await server.serve()


async def start_all_agent_servers():
    """Start all three agent servers."""
    tasks = [
        asyncio.create_task(
            run_agent_server(customer_data_agent, customer_data_agent_card, 10020)
        ),
        asyncio.create_task(
            run_agent_server(support_agent, support_agent_card, 10021)
        ),
        asyncio.create_task(
            run_agent_server(router_agent, router_agent_card, 10022)
        ),
    ]
    
    await asyncio.sleep(3)
    
    print("\n=== A2A Agent Servers Started ===")
    print("   Customer Data Agent: http://127.0.0.1:10020")
    print("   Support Agent: http://127.0.0.1:10021")
    print("   Router Agent: http://127.0.0.1:10022")
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("Shutting down agent servers...")


def run_agent_servers_in_background():
    """Run agent servers in background thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_all_agent_servers())


class A2ATestClient:
    """A2A client for testing."""
    
    def __init__(self, default_timeout: float = 60.0):
        self._agent_info_cache: Dict[str, Dict[str, Any] | None] = {}
        self.default_timeout = default_timeout
    
    async def send_query(self, agent_url: str, message: str) -> str:
        """Send a message to an A2A agent and return the response."""
        timeout_config = httpx.Timeout(
            timeout=self.default_timeout,
            connect=10.0,
            read=self.default_timeout,
            write=10.0,
            pool=5.0,
        )
        
        async with httpx.AsyncClient(timeout=timeout_config) as httpx_client:
            if agent_url in self._agent_info_cache and self._agent_info_cache[agent_url] is not None:
                agent_card_data = self._agent_info_cache[agent_url]
            else:
                agent_card_response = await httpx_client.get(
                    f'{agent_url}{AGENT_CARD_WELL_KNOWN_PATH}'
                )
                agent_card_data = self._agent_info_cache[agent_url] = agent_card_response.json()
            
            agent_card = AgentCard(**agent_card_data)
            
            config = ClientConfig(
                httpx_client=httpx_client,
                supported_transports=[
                    TransportProtocol.jsonrpc,
                    TransportProtocol.http_json,
                ],
                use_client_preference=True,
            )
            
            factory = ClientFactory(config)
            client = factory.create(agent_card)
            
            message_obj = create_text_message_object(content=message)
            
            responses = []
            async for response in client.send_message(message_obj):
                responses.append(response)
            
            if responses and isinstance(responses[0], tuple) and len(responses[0]) > 0:
                task = responses[0][0]
                try:
                    return task.artifacts[0].parts[0].root.text
                except (AttributeError, IndexError):
                    return str(task)
            
            return "No response received"


async def run_test_scenarios():
    """Run all 5 test scenarios."""
    client = A2ATestClient()
    
    # Scenario 1
    print("\n\n### SCENARIO 1: Simple Query ###")
    print("Query: Get customer information for ID 5")
    print("-" * 80)
    
    response = await client.send_query(
        "http://localhost:10020",
        "Get customer information for ID 5"
    )
    print("Response:")
    print(response)
    
    # Scenario 2
    print("\n\n### SCENARIO 2: Coordinated Query ###")
    print("Query: Customer 1 needs help upgrading account")
    print("-" * 80)
    
    response = await client.send_query(
        "http://localhost:10022",
        "Customer ID 1 needs help with account upgrade. Please: 1) Get customer info, 2) Create a support ticket for 'Account upgrade request' with MEDIUM priority, 3) Provide upgrade guidance."
    )
    print("Response:")
    print(response)
    
    # Scenario 3
    print("\n\n### SCENARIO 3: Complex Query ###")
    print("Query: Show all active customers who have open tickets")
    print("-" * 80)
    
    response = await client.send_query(
        "http://localhost:10022",
        "Show me all active customers who have open tickets"
    )
    print("Response:")
    print(response)
    
    # Scenario 4
    print("\n\n### SCENARIO 4: Escalation Query ###")
    print("Query: I've been charged twice, please refund immediately!")
    print("-" * 80)
    
    response = await client.send_query(
        "http://localhost:10021",
        "Customer says: I've been charged twice, please refund immediately! This is urgent. Analyze the priority and provide an appropriate response."
    )
    print("Response:")
    print(response)
    
    # Scenario 5
    print("\n\n### SCENARIO 5: Multi-Intent Query ###")
    print("Query: Update my email and show my ticket history")
    print("-" * 80)
    
    response = await client.send_query(
        "http://localhost:10022",
        "I'm customer ID 2. Please update my email to newemail@example.com and then show me my complete ticket history."
    )
    print("Response:")
    print(response)


def main():
    """Main entry point."""
    
    print("\nStarting servers...")
    
    mcp_thread = threading.Thread(target=start_mcp_server, daemon=True)
    mcp_thread.start()
    time.sleep(2)
    
    agent_thread = threading.Thread(target=run_agent_servers_in_background, daemon=True)
    agent_thread.start()
    time.sleep(5)
    
    print("\nAll servers ready!")
    print("\nRunning test scenarios...")
    
    try:
        asyncio.run(run_test_scenarios())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n\nDemo complete. Press Ctrl+C to exit.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
