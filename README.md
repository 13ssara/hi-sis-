# HiSis - Reddit-like Thread Discussion Platform

A simple Reddit-like website built with Flask and SQLite, where users can create threads and post comments.

## Features

- 🧵 Create and view discussion threads
- 💬 Add comments/posts to threads
- 🗄️ Local SQLite database storage
- 📱 Clean, dark-themed UI similar to Reddit
- ⚡ Real-time thread and post loading via API

## Project Structure

```
HiSis/
├── app.py                 # Flask application and routes
├── database.py            # Database models and setup
├── requirements.txt       # Python dependencies
├── templates/
│   ├── index.html        # Main page with thread list
│   └── thread.html       # Individual thread view
└── reddit.db             # SQLite database (created on first run)
```

## Installation & Setup

### 1. Create a Python Virtual Environment

```bash
# Navigate to the project directory
cd HiSis

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## How to Use

### Creating a Thread
1. Enter your name in the "Your Name" field
2. Enter a thread title in the "Thread Title" field
3. (Optional) Add more details in the "Content" field
4. Click "Create Thread"

### Viewing Threads
- The home page displays all threads sorted by newest first
- Click on any thread to view its full content and comments
- Each thread shows the author, creation date, and number of comments

### Adding Comments
1. Open a thread
2. Enter your name and comment text
3. Click "Post Comment"
4. Your comment will appear in the thread

## Database

The application uses **SQLite** for local data storage. The database file (`reddit.db`) is automatically created in the project directory when you first run the application.

### Database Tables

**threads** table:
- `id` (Primary Key)
- `title` (Thread title)
- `content` (Thread description)
- `author` (Username)
- `created_at` (Timestamp)

**posts** table:
- `id` (Primary Key)
- `thread_id` (Foreign Key to threads)
- `content` (Post/comment content)
- `author` (Username)
- `created_at` (Timestamp)

## API Endpoints

### Threads
- `GET /api/threads` - Get all threads
- `POST /api/threads` - Create a new thread
- `GET /thread/<id>` - View a specific thread (HTML)

### Posts/Comments
- `GET /api/threads/<thread_id>/posts` - Get all comments in a thread
- `POST /api/threads/<thread_id>/posts` - Create a new comment

## Technical Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Design**: Dark theme inspired by Reddit

## Notes

- The application runs in debug mode by default
- All data is stored locally in the SQLite database
- No authentication is required - any name can be used
- The database persists between application restarts

## Future Enhancements

- User authentication and accounts
- Upvoting/downvoting system
- User profiles
- Search functionality
- Thread categories/tags
- Edit and delete functionality
- Pagination for large thread lists
