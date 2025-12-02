import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, Response, jsonify
from flask_cors import CORS

DB_PATH = "support.db"

app = Flask(__name__)
CORS(app)

MCP_TOOLS = [
    {
        "name": "get_customer",
        "description": "Retrieve a specific customer by their ID. Returns customer details including name, email, phone, and status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The unique ID of the customer to retrieve"
                }
            },
            "required": ["customer_id"]
        }
    },
    {
        "name": "list_customers",
        "description": "List all customers in the database. Can optionally filter by status (active or disabled) and limit results.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["active", "disabled"],
                    "description": "Optional filter by customer status"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of customers to return (default: all)"
                }
            }
        }
    },
    {
        "name": "update_customer",
        "description": "Update an existing customer's information. Provide the customer ID and the fields to update (name, email, phone, or status).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The unique ID of the customer to update"
                },
                "data": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "status": {"type": "string", "enum": ["active", "disabled"]}
                    },
                    "description": "Fields to update"
                }
            },
            "required": ["customer_id", "data"]
        }
    },
    {
        "name": "create_ticket",
        "description": "Create a new support ticket for a customer. Requires customer ID, issue description, and priority level.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The customer ID for whom the ticket is being created"
                },
                "issue": {
                    "type": "string",
                    "description": "Description of the issue"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Priority level of the ticket"
                }
            },
            "required": ["customer_id", "issue", "priority"]
        }
    },
    {
        "name": "get_customer_history",
        "description": "Get all support tickets for a specific customer, showing their complete ticket history.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The customer ID to get ticket history for"
                }
            },
            "required": ["customer_id"]
        }
    }
]


def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a SQLite row to a dictionary."""
    return {key: row[key] for key in row.keys()}


# Tool Implementations

def get_customer(customer_id: int) -> Dict[str, Any]:
    """Retrieve a specific customer by ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'success': True,
                'customer': row_to_dict(row)
            }
        else:
            return {
                'success': False,
                'error': f'Customer with ID {customer_id} not found'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }


def list_customers(status: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
    """List all customers, optionally filtered by status."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM customers'
        params = []
        
        if status:
            if status not in ['active', 'disabled']:
                return {
                    'success': False,
                    'error': 'Status must be "active" or "disabled"'
                }
            query += ' WHERE status = ?'
            params.append(status)
        
        query += ' ORDER BY name'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        customers = [row_to_dict(row) for row in rows]
        
        return {
            'success': True,
            'count': len(customers),
            'customers': customers
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }


def update_customer(customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update customer information."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if customer exists
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        if not cursor.fetchone():
            conn.close()
            return {
                'success': False,
                'error': f'Customer with ID {customer_id} not found'
            }
        
        # Build update query
        updates = []
        params = []
        
        for field in ['name', 'email', 'phone', 'status']:
            if field in data:
                updates.append(f'{field} = ?')
                params.append(data[field])
        
        if not updates:
            conn.close()
            return {
                'success': False,
                'error': 'No fields to update'
            }
        
        # Always update timestamp
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(customer_id)
        
        update_clause = ', '.join(updates)
        query = f'UPDATE customers SET {update_clause} WHERE id = ?'
        cursor.execute(query, params)
        conn.commit()
        
        # Fetch updated customer
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        row = cursor.fetchone()
        conn.close()
        
        return {
            'success': True,
            'message': f'Customer {customer_id} updated successfully',
            'customer': row_to_dict(row)
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }


def create_ticket(customer_id: int, issue: str, priority: str) -> Dict[str, Any]:
    """Create a new support ticket."""
    try:
        if priority not in ['low', 'medium', 'high']:
            return {
                'success': False,
                'error': 'Priority must be "low", "medium", or "high"'
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if customer exists
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        if not cursor.fetchone():
            conn.close()
            return {
                'success': False,
                'error': f'Customer with ID {customer_id} not found'
            }
        
        # Create ticket
        cursor.execute('''
            INSERT INTO tickets (customer_id, issue, status, priority)
            VALUES (?, ?, 'open', ?)
        ''', (customer_id, issue, priority))
        
        ticket_id = cursor.lastrowid
        conn.commit()
        
        # Fetch the created ticket
        cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
        row = cursor.fetchone()
        conn.close()
        
        return {
            'success': True,
            'message': f'Ticket #{ticket_id} created successfully',
            'ticket': row_to_dict(row)
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }


def get_customer_history(customer_id: int) -> Dict[str, Any]:
    """Get all tickets for a customer."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if customer exists
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        customer_row = cursor.fetchone()
        
        if not customer_row:
            conn.close()
            return {
                'success': False,
                'error': f'Customer with ID {customer_id} not found'
            }
        
        # Get all tickets for this customer
        cursor.execute('''
            SELECT * FROM tickets
            WHERE customer_id = ?
            ORDER BY created_at DESC
        ''', (customer_id,))
        
        ticket_rows = cursor.fetchall()
        conn.close()
        
        tickets = [row_to_dict(row) for row in ticket_rows]
        
        return {
            'success': True,
            'customer': row_to_dict(customer_row),
            'ticket_count': len(tickets),
            'tickets': tickets
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }


# MCP Protocol Implementation

def create_sse_message(data: Dict[str, Any]) -> str:
    """Format a message for Server-Sent Events (SSE)."""
    return f"data: {json.dumps(data)}\n\n"


def handle_initialize(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP initialize request."""
    return {
        "jsonrpc": "2.0",
        "id": message.get("id"),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
            },
            "serverInfo": {
                "name": "customer-management-mcp-server",
                "version": "1.0.0"
            }
        }
    }


def handle_tools_list(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tools/list request."""
    return {
        "jsonrpc": "2.0",
        "id": message.get("id"),
        "result": {
            "tools": MCP_TOOLS
        }
    }


def handle_tools_call(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tools/call request."""
    params = message.get("params", {})
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    # Map tool names to functions
    tool_functions = {
        "get_customer": lambda: get_customer(**arguments),
        "list_customers": lambda: list_customers(**arguments),
        "update_customer": lambda: update_customer(**arguments),
        "create_ticket": lambda: create_ticket(**arguments),
        "get_customer_history": lambda: get_customer_history(**arguments),
    }
    
    if tool_name not in tool_functions:
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {
                "code": -32601,
                "message": f"Tool not found: {tool_name}"
            }
        }
    
    try:
        result = tool_functions[tool_name]()
        
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {
                "code": -32603,
                "message": f"Tool execution error: {str(e)}"
            }
        }


def process_mcp_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Process an MCP message and route to appropriate handler."""
    method = message.get("method")
    
    if method == "initialize":
        return handle_initialize(message)
    elif method == "tools/list":
        return handle_tools_list(message)
    elif method == "tools/call":
        return handle_tools_call(message)
    else:
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }


# Flask Routes

@app.route('/mcp', methods=['POST'])
def mcp_endpoint():
    """Main MCP endpoint for communication."""
    message = request.get_json()
    
    def generate():
        try:
            response = process_mcp_message(message)
            yield create_sse_message(response)
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            yield create_sse_message(error_response)
    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "server": "customer-management-mcp-server",
        "version": "1.0.0",
        "tools": len(MCP_TOOLS)
    })


def start_mcp_server(host='127.0.0.1', port=5000):
    """Start the MCP server."""
    print(f"Starting MCP Server on {host}:{port}")
    print(f"MCP Endpoint: http://{host}:{port}/mcp")
    print(f"Health Check: http://{host}:{port}/health")
    print(f"Available Tools: {len(MCP_TOOLS)}")
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    start_mcp_server()
