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


### SCENARIO 2: Coordinated Query ###
Query: Customer 1 needs help upgrading account
--------------------------------------------------------------------------------
Response:
Thank you for providing the customer information and for creating Ticket #33.

Hello John Doe, I understand you're looking to upgrade your account. I've noted this as a **MEDIUM** priority request, and we'll get this sorted for you.

To help you with your account upgrade, please follow these steps:

1.  **Log In to Your Account:** Go to our website and log in using your current credentials.
2.  **Navigate to Account Settings/Billing:** Once logged in, look for a section typically labeled "Account Settings," "Subscription," "Billing," or "Upgrade Plan." This is usually found in the top-right corner of the page, often under your profile icon or name.
3.  **Select Your Desired Plan:** You'll see a list of available upgrade plans. Review the features and pricing for each, and select the plan that best fits your needs.
4.  **Confirm Upgrade:** Follow the prompts to confirm your new plan and update any necessary payment information. Your upgrade should be processed immediately.

If you encounter any issues during this process, or if you'd like to discuss the different plan options in more detail, please reply to this message or call us directly at +1-555-0101, referencing Ticket #33. We're here to help!


### SCENARIO 3: Complex Query ###
Query: Show all active customers who have open tickets
--------------------------------------------------------------------------------
Response:
I understand you're looking for a list of active customers with open tickets. Based on the information provided by `[customer_operations]`, here are the active customers with open tickets and their respective issue details:

*   **Alice Williams (ID: 4)**
    *   Open Ticket ID: 24
    *   Issue: "Feature request: integration with Slack"
    *   Priority: MEDIUM (Feature request)

*   **Charlie Brown (ID: 5)**
    *   Open Ticket ID: 8
    *   Issue: "Email notifications not being received"
    *   Priority: MEDIUM (Functionality problem)

*   **Diana Prince (ID: 6)**
    *   Open Ticket ID: 18
    *   Issue: "Request for additional language support"
    *   Priority: MEDIUM (Feature request)

Let me know if you need any further details on these tickets or assistance with them!


### SCENARIO 4: Escalation Query ###
Query: I've been charged twice, please refund immediately!
--------------------------------------------------------------------------------
Response:
I understand your frustration with being charged twice, and I apologize for this inconvenience. We'll get this sorted out for you.

This is a **HIGH** priority issue.

To help me investigate and process your refund immediately, please provide the following details:

1.  The last 4 digits of the credit card used for the transaction.
2.  The approximate date and time of both charges.
3.  The amount of each charge.
4.  The service or product these charges are related to.

Once I have this information, I can look into your account and initiate the refund process.


### SCENARIO 5: Multi-Intent Query ###
Query: Update my email and show my ticket history
--------------------------------------------------------------------------------
Response:
Thank you for reaching out!

I see that your email address has been successfully updated to **newemail@example.com**.

Here is your complete ticket history:
*   **Ticket ID 7:** "Profile image upload fails" (Status: resolved)
*   **Ticket ID 14:** "Billing question about invoice" (Status: resolved)
*   **Ticket ID 15:** "Feature request: dark mode" (Status: open)

If you have any questions about these tickets or need further assistance, please let me know!


Demo complete. Press Ctrl+C to exit.
```