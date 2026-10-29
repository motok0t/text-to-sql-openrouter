#!/usr/bin/env python3
"""Streamlit app for generating and executing SQL queries against demo.db.

Uses OpenRouter API to convert natural language queries to SQL.
API key should be set in .streamlit/secrets.toml as OPENROUTER_API_KEY.
"""

import sqlite3
from typing import Any, Dict, List

import openai
import streamlit as st

# Page config
st.set_page_config(page_title="Text-to-SQL Demo", layout="centered")

st.title("Text-to-SQL with OpenRouter")
st.markdown(
    "Enter a natural language query, and I will convert it into SQL "
    "to run against the demo.db database."
)

# Sidebar for API key configuration
with st.sidebar:
    st.header("Settings")
    model_name = "openrouter/free"

# Database schema information
DB_SCHEMA = """Database schema for demo.db:

Table clients:
- id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- name (TEXT)
- city (TEXT)
- email (TEXT, UNIQUE)

Table products:
- id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- name (TEXT)
- price (REAL, CHECK price > 0)

Table orders:
- id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- client_id (INTEGER, FOREIGN KEY REFERENCES clients(id))
- product_id (INTEGER, FOREIGN KEY REFERENCES products(id))
- quantity (INTEGER, CHECK quantity > 0)
- order_date (TEXT, DEFAULT date('now'))
"""

# Available tables for the LLM
TABLES_INFO = """Available tables: clients, products, orders.
Columns: clients - id, name, city, email
Columns: products - id, name, price
Columns: orders - id, client_id, product_id, quantity, order_date
"""


def get_sql_from_llm(user_query: str, model: str, api_key: str) -> str:
    """Send query to OpenRouter LLM and get SQL response."""
    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    messages = [
        {
            "role": "system",
            "content": f"""You are an SQL query generation assistant.
Task: Convert natural language into SQL for the demo.db database.
{DB_SCHEMA}
{TABLES_INFO}

Important rules:
1. Return ONLY the SQL query, without explanations and code markers
2. Use correct table and column names from the schema above
3. Use WHERE parameters for filtering
4. Use GROUP BY for aggregations when needed
5. SQL must be safe and work for SQLite
6. If the query is unclear, ask a clarifying question, but try to generate SQL

Examples:
- "How many clients are from New York?" -> SELECT COUNT(*) FROM clients WHERE city = 'New York'
- "Which products cost more than 1000?" -> SELECT * FROM products WHERE price > 1000
- "Show all orders for client #1" -> SELECT * FROM orders WHERE client_id = 1
""",
        },
        {
            "role": "user",
            "content": user_query,
        },
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
        )
        sql_query = response.choices[0].message.content.strip()

        # Clean up potential code block markers
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:].strip()
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3].strip()

        return sql_query
    except Exception as e:
        st.error(f"Error connecting to OpenRouter: {str(e)}")
        return ""


def execute_sql(db_path: str, sql: str) -> List[Dict[str, Any]]:
    """Execute SQL query against SQLite database and return results."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

        # Convert rows to list of dicts
        results = [dict(row) for row in rows]
        conn.close()

        return results
    except Exception as e:
        st.error(f"SQL Error: {str(e)}")
        return []


# Main app
st.subheader("Your Query")
user_input = st.text_area(
    "Enter your query:",
    placeholder="For example: How many clients are from New York?",
    height=100,
)

col1, col2 = st.columns([1, 1])
with col1:
    run_button = st.button("Generate SQL", type="primary")
with col2:
    clear_button = st.button("Clear")

if clear_button:
    st.rerun()

if run_button or user_input:
    # Check for API key from secrets.toml
    has_key = False
    if st.secrets.get("OPENROUTER_API_KEY"):
        has_key = True
        api_key = st.secrets.get("OPENROUTER_API_KEY")

    if not has_key:
        st.warning(
            "Enter OpenRouter API key in sidebar or via "
            "st.secrets OPENROUTER_API_KEY"
        )
    else:
        with st.spinner("Generating SQL..."):
            sql_query = get_sql_from_llm(user_input, model_name, api_key)

        if sql_query:
            st.subheader("Generated SQL:")
            st.code(sql_query, language="sql")

            st.subheader("Execution Results:")

            # Use demo.db relative to the app file
            db_path = "demo.db"

            with st.spinner("Executing SQL..."):
                results = execute_sql(db_path, sql_query)

            if results:
                st.success(f"Found {len(results)} result(s):")
                st.dataframe(results)
            else:
                st.info("Query executed, but no results found.")
        else:
            st.error("Failed to generate SQL query")
else:
    st.info("Enter a query above and click 'Generate SQL'")
