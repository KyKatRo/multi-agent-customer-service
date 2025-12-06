# Output of demo.py
```
Starting servers...

=== Starting MCP Server ===
Starting MCP Server on 127.0.0.1:5000
MCP Endpoint: http://127.0.0.1:5000/mcp
Health Check: http://127.0.0.1:5000/health
Available Tools: 5
 * Serving Flask app 'mcp_server'
 * Debug mode: off

=== A2A Agent Servers Started ===
   Customer Data Agent: http://127.0.0.1:10020
   Support Agent: http://127.0.0.1:10021
   Router Agent: http://127.0.0.1:10022

All servers ready!

Running test scenarios...


### SCENARIO 1: Simple Query ###
Query: Get customer information for ID 5
--------------------------------------------------------------------------------
Response:
Here is the information for customer ID 5:
Name: Charlie Brown
Email: charlie.brown@email.com
Phone: +1-555-0105
Status: active
Created At: 2025-12-02 08:11:29
Updated At: 2025-12-02 08:11:29


### SCENARIO 2: Coordinated Query ###
Query: Customer 1 needs help upgrading account
--------------------------------------------------------------------------------
Response:
Thank you for reaching out! I've successfully created a support ticket for your account upgrade request. Your ticket number is #35.

To upgrade your account, please visit the "Account Settings" or "Subscription" section on our website. There, you should find options to view available plans and upgrade your current subscription. If you encounter any issues or have further questions during the upgrade process, please reply to this ticket, and our team will be happy to assist you.



### SCENARIO 3: Complex Query ###
Query: Show all active customers who have open tickets
--------------------------------------------------------------------------------
Response:
Here are the active customers from the sample who have open tickets:

*   **Alice Williams (ID: 4)**:
    *   Ticket ID 2: "Database connection timeout errors" (in progress, high priority)
    *   Ticket ID 24: "Feature request: integration with Slack" (open, low priority)

*   **Charlie Brown (ID: 5)**:
    *   Ticket ID 8: "Email notifications not being received" (open, medium priority)

*   **Diana Prince (ID: 6)**:
    *   Ticket ID 9: "Dashboard loading very slowly" (in progress, medium priority)
    *   Ticket ID 18: "Request for additional language support" (open, low priority)

Please let me know if you need any further details or assistance with these tickets!


### SCENARIO 4: Escalation Query ###
Query: I've been charged twice, please refund immediately!
--------------------------------------------------------------------------------
Response:
This is a HIGH priority billing issue. I understand this is urgent. To create a ticket for you and initiate the refund process, I need your customer ID. Could you please provide it?


### SCENARIO 5: Multi-Intent Query ###
Query: Update my email and show my ticket history
--------------------------------------------------------------------------------
Response:
I've retrieved your complete ticket history, customer ID 2!

Here's a summary of your tickets:
*   **Ticket ID 7:** "Profile image upload fails" - Resolved (medium priority)
*   **Ticket ID 14:** "Billing question about invoice" - Resolved (low priority)
*   **Ticket ID 15:** "Feature request: dark mode" - Open (low priority)

Is there anything else I can help you with regarding these tickets or any other support needs?



Demo complete. Press Ctrl+C to exit.
```