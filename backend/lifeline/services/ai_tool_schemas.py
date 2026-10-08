TOOLS = [
    {
        "name": "lookup_product",
        "description": "Search the product catalog by name, SKU, barcode, category, nickname or alias.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "check_inventory",
        "description": "Check the current stock level of a product.",
        "parameters": {
            "type": "object",
            "properties": {"product_query": {"type": "string"}},
            "required": ["product_query"],
        },
    },
    {
        "name": "lookup_customer",
        "description": "Find a customer by name or partial phone number.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "lookup_transaction",
        "description": "Look up a past sale by receipt number or sale id.",
        "parameters": {
            "type": "object",
            "properties": {
                "receipt_number": {"type": "string"},
                "sale_id": {"type": "string"},
            },
        },
    },
    {
        "name": "get_sales_summary",
        "description": "Get total sales, transaction count and payment breakdown for a period.",
        "parameters": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "enum": [
                        "today",
                        "yesterday",
                        "this_week",
                        "last_week",
                        "this_month",
                        "last_month",
                    ],
                }
            },
        },
    },
    {
        "name": "get_profit_summary",
        "description": "Get revenue, estimated cost and gross profit for a period. Requires the view_profit permission.",
        "parameters": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "enum": [
                        "today",
                        "yesterday",
                        "this_week",
                        "last_week",
                        "this_month",
                        "last_month",
                    ],
                }
            },
        },
    },
    {
        "name": "get_low_stock_products",
        "description": "List products at or below their configured minimum stock level.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_top_products",
        "description": "List best (or worst) selling products for a period, ranked by quantity, revenue, or profit.",
        "parameters": {
            "type": "object",
            "properties": {
                "period": {"type": "string"},
                "by": {"type": "string", "enum": ["quantity", "revenue", "profit"]},
                "limit": {"type": "integer"},
            },
        },
    },
    {
        "name": "get_cash_drawer_status",
        "description": "Get how much cash should currently be in the drawer for the caller's open shift.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_business_health",
        "description": "Get an overall snapshot: today's sales/profit, top products, low stock, outstanding credit and supplier balances.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "calculate_cart",
        "description": "Resolve a list of product names/quantities into prices and a total WITHOUT recording a sale. Always call this before create_sale so the user can review the total.",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "product_name": {"type": "string"},
                            "product_id": {"type": "string"},
                            "quantity": {"type": "integer"},
                        },
                    },
                }
            },
            "required": ["items"],
        },
    },
    {
        "name": "create_customer",
        "description": "Create a new customer record.",
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "phone": {"type": "string"}},
            "required": ["name"],
        },
    },
    {
        "name": "adjust_inventory",
        "description": "Manually adjust a product's stock (restock, damage, write-off, correction). Not for recording a sale.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_query": {"type": "string"},
                "quantity_changed": {
                    "type": "integer",
                    "description": "Positive to add stock, negative to remove.",
                },
                "reason": {
                    "type": "string",
                    "enum": [
                        "restock",
                        "damage",
                        "write_off",
                        "correction",
                        "initial_stock",
                    ],
                },
                "note": {"type": "string"},
            },
            "required": ["product_query", "quantity_changed", "reason"],
        },
    },
    {
        "name": "create_expense",
        "description": "Record a business expense.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "amount": {"type": "number"},
                "note": {"type": "string"},
                "payment_method": {"type": "string"},
            },
            "required": ["category", "amount"],
        },
    },
    {
        "name": "create_sale",
        "description": "Finalize and record a completed sale. HIGH RISK: only call this after the user has explicitly confirmed the total and payment method — never guess or call this speculatively.",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "string"},
                            "product_name": {"type": "string"},
                            "quantity": {"type": "integer"},
                            "unit_price": {"type": "number"},
                        },
                        "required": ["quantity"],
                    },
                },
                "payments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "enum": [
                                    "cash",
                                    "card",
                                    "mpesa",
                                    "qr",
                                    "wallet",
                                    "store_credit",
                                    "custom",
                                ],
                            },
                            "amount": {"type": "number"},
                            "amount_tendered": {"type": "number"},
                            "transaction_reference": {"type": "string"},
                        },
                        "required": ["method", "amount"],
                    },
                },
                "customer_id": {"type": "string"},
                "note": {"type": "string"},
            },
            "required": ["items", "payments"],
        },
    },
    {
        "name": "create_return",
        "description": "HIGH RISK: process a refund/return against a past sale. Only after explicit user confirmation.",
        "parameters": {
            "type": "object",
            "properties": {
                "sale_id": {"type": "string"},
                "sale_item_ids_quantities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sale_item_id": {"type": "string"},
                            "quantity": {"type": "integer"},
                        },
                    },
                },
                "reason": {"type": "string"},
            },
            "required": ["sale_id", "sale_item_ids_quantities", "reason"],
        },
    },
]
