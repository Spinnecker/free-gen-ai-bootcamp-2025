Business Goal: 
A language learning school wants to build a prototype of learning portal which will act as three things:
Inventory of possible vocabulary that can be learned
Act as a  Learning record store (LRS), providing correct and wrong score on practice vocabulary
A unified launchpad to launch different learning apps


Technical Specifications:

# English to Spanish Vocabulary Quiz API Specifications

## Technology Stack
- **Framework**: Flask 3.0.0
- **Database**: SQLite with Flask-SQLAlchemy 3.1.1
- **Python Version**: 3.x

## Database Schema

### Vocabulary Table
- `id`: Integer (Primary Key)
- `english`: String(100) (Not Null)
- `spanish`: String(100) (Not Null)

## API Endpoints

### 1. Get All Vocabulary
- **Endpoint**: `/vocab`
- **Method**: GET
- **Response Format**: JSON
- **Response Example**:
```json
[
    {
        "id": 1,
        "english": "hello",
        "spanish": "hola"
    }
]
```

### 2. Add New Vocabulary
- **Endpoint**: `/vocab`
- **Method**: POST
- **Request Format**: JSON
- **Required Fields**:
  - english: string
  - spanish: string
- **Request Example**:
```json
{
    "english": "hello",
    "spanish": "hola"
}
```
- **Response**: Created vocabulary entry with status 201

### 3. Generate Quiz
- **Endpoint**: `/quiz`
- **Method**: GET
- **Query Parameters**:
  - count: integer (optional, default=5)
- **Response Format**: JSON
- **Response Example**:
```json
[
    {
        "id": 1,
        "english": "hello"
    }
]
```

### 4. Check Answer
- **Endpoint**: `/check/<vocab_id>`
- **Method**: POST
- **Request Format**: JSON
- **Required Fields**:
  - answer: string
- **Request Example**:
```json
{
    "answer": "hola"
}
```
- **Response Example**:
```json
{
    "correct": true,
    "correct_answer": "hola"
}
```

## Error Handling
- 400: Bad Request (Missing required fields)
- 404: Not Found (Vocabulary ID not found)
- 500: Internal Server Error

## Data Initialization
- Database automatically creates initial vocabulary entries on first run
- Initial vocabulary includes basic Spanish words and phrases