# 🧠 String Analyzer API

A RESTful API built with FastAPI + PostgreSQL that analyzes and stores string properties. Built for HNGx Internship (Stage 1 - Backend Wizards).

---

## 🚀 Features

For each analyzed string, the API computes and stores:

- ✅ `length`: Total number of characters
- ✅ `is_palindrome`: Whether the string is a palindrome
- ✅ `unique_characters`: Count of distinct characters
- ✅ `word_count`: Number of words separated by spaces
- ✅ `sha256_hash`: SHA-256 hash used as unique identifier
- ✅ `character_frequency_map`: Dictionary of character counts

---

## 📌 Endpoints

### 1. Analyze a string  
**POST** `/strings`

```json
{
  "value": "your string here"
}
````

Response:

```json
{
  "id": "sha256...",
  "value": "your string here",
  "properties": {
    "length": 20,
    "is_palindrome": false,
    "unique_characters": 13,
    "word_count": 4,
    "sha256_hash": "...",
    "character_frequency_map": {
      "y": 1,
      "o": 2
      // ...
    }
  },
  "created_at": "2025-10-21T09:18:50.755137Z"
}
```

---

### 2. Get specific string

**GET** `/strings/{value}`

---

### 3. Filter strings

**GET** `/strings?is_palindrome=true&min_length=5&word_count=1&contains_character=a`

---

### 4. Natural language filtering

**GET** `/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings`

Returns parsed filters like:

```json
"parsed_filters": {
  "word_count": 1,
  "is_palindrome": true
}
```

---

### 5. Delete a string

**DELETE** `/strings/{value}`

---

## 🧑‍💻 Run Locally

### ✅ Clone the repo

```bash
git clone https://github.com/your-username/string-analyzer-api.git
cd string-analyzer
```

### ✅ Set up virtual environment (optional)

```bash
python -m venv venv
venv\Scripts\activate
```

### ✅ Install dependencies

```bash
pip install -r requirements.txt
```

### ✅ Environment Variables

Create a `.env` file in the root with:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
```

Or use the one from Railway PostgreSQL plugin.

### ✅ Start the server

```bash
uvicorn app.main:app --reload
```

---

## 🧪 Test

Use [Postman](https://www.postman.com/) or `curl` to test endpoints locally or on your deployed Railway URL.

---

## 🛠 Built With

* 🧬 [FastAPI](https://fastapi.tiangolo.com/)
* 🐘 [PostgreSQL](https://www.postgresql.org/)
* 🔌 [SQLAlchemy (Async)](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
* 🌐 [Railway](https://railway.app/) for deployment

---

## 📦 Deployment (Railway)

> Already configured and deployed via [Railway](https://railway.app).

Procfile:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🧠 Sample Queries for Natural Language

| Query                                              | Parsed Filters                               |
| -------------------------------------------------- | -------------------------------------------- |
| "all single word palindromic strings"              | `word_count=1`, `is_palindrome=true`         |
| "strings longer than 10 characters"                | `min_length=11`                              |
| "strings containing the letter z"                  | `contains_character=z`                       |
| "palindromic strings that contain the first vowel" | `is_palindrome=true`, `contains_character=a` |

---

## 📂 Project Structure

```
string-analyzer/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── filters.py
│   ├── database.py
├── requirements.txt
├── Procfile
├── .env
├── README.md
```