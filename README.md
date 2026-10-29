# Text-to-SQL with OpenRouter

A Streamlit web application that converts natural language into SQL queries and executes them against a SQLite database.

## Demo

![Demo](demo.gif)

*The demo GIF shows the app generating SQL from natural language queries and fetching data from the database.*

## Tech Stack

- Python 3.11+
- Streamlit
- SQLite
- OpenRouter API (free tier)

## How to Run Locally

1. Clone the repo.
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   python setup_db.py
   ```
5. Create a `.streamlit` folder and a `secrets.toml` file inside it. Add the following line:
   ```toml
   OPENROUTER_API_KEY = "your_key_here"
   ```
   *How to get a free key: Go to [openrouter.ai](https://openrouter.ai), sign up, and generate an API key. Keys start with `sk-or-v1-`.*
6. Run the app:
   ```bash
   streamlit run app.py
   ```

## Example

**Natural language query:** "Сколько клиентов из Москвы?"

**Resulting SQL:**
```sql
SELECT COUNT(*) FROM clients WHERE city = 'Москва'
```
 