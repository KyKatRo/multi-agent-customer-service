# Multi-Agent Customer Service System

A customer service multi-agent system using A2A and MCP to access database information and reason.

## Components

### 1. MCP Server (`mcp_server.py`)
Exposes 5 tools via Model Context Protocol:
- `get_customer(customer_id)` - Retrieve customer by ID
- `list_customers(status, limit)` - List customers with filtering
- `update_customer(customer_id, data)` - Update customer information
- `create_ticket(customer_id, issue, priority)` - Create support tickets
- `get_customer_history(customer_id)` - Get customer's ticket history

### 2. Customer Data Agent (`agents/customer_data_agent.py`)
- MCP Tools: `get_customer`, `list_customers`, `update_customer`
- Handles customer data operations
- Exposes A2A interface on port 10020

### 3. Support Agent (`agents/support_agent.py`)
- MCP Tools: `create_ticket`, `get_customer_history`
- Handles ticket creation and history retrieval
- Provides support guidance and priority analysis
- Exposes A2A interface on port 10021

### 4. Router Agent (`agents/router_agent.py`)
- Orchestrates the other two agents
- Routes queries to appropriate specialists
- Coordinates multi-step operations
- Exposes A2A interface on port 10022


## Installation

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your Google API key:

```
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Initialize the database

```bash
python database_setup.py
```

When prompted:
- Enter `y` to insert sample data
- Enter `y` to run sample queries (optional)

This creates `support.db` with 15 customers and 25 tickets.

## Running the Demo

Once everything is set up, run the complete demo:

```bash
python demo.py
```

If you see "Address already in use" errors, kill processes on the required ports:

```bash
lsof -ti:5000 | xargs kill -9
lsof -ti:10020 | xargs kill -9
lsof -ti:10021 | xargs kill -9
lsof -ti:10022 | xargs kill -9
```