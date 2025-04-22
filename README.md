# Notes App

A modern, feature-rich notes application with AI-powered summarization, built with Flask and JavaScript.

![Notes App Screenshot](static/img/screenshot.png)

## Features

- **User Authentication**: Secure login and registration system
- **Note Management**: Create, edit, and delete notes
- **Categorization**: Organize notes by categories (Work, Personal, Ideas)
- **AI-Powered Summaries**: Automatic note summarization using Google's Gemini AI
- **Drag and Drop**: Intuitive reordering of notes
- **Search Functionality**: Quickly find notes by title, content, or summary
- **Dark/Light Mode**: Toggle between themes for comfortable viewing
- **Voice Transcription**: Record your notes using speech recognition
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **AI Integration**: Google Gemini API
- **Authentication**: Flask session-based auth with password hashing

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/notes-app.git
   cd notes-app
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following content:
   ```
   SECRET_KEY=your-secret-key-here
   GEMINI_API_KEY=your-gemini-api-key
   ```

5. Run the database migration:
   ```
   python migrate_db.py
   ```

6. Start the application:
   ```
   python app.py
   ```

7. Open your browser and navigate to `http://127.0.0.1:5000`

## Usage

### Creating Notes

1. Click the "Add New Note" button
2. Enter a title and content for your note
3. Select a category (Work, Personal, or Ideas)
4. Optionally, use the voice recording feature to transcribe your note
5. Click "Save Note"

### Managing Notes

- **Edit**: Click on a note to view it, then click the edit button
- **Delete**: Click the delete button on any note
- **Reorder**: Drag and drop notes to change their order
- **Search**: Use the search bar to find specific notes
- **Filter**: Click on category buttons to filter notes by category

### AI Summarization

- Each note automatically gets an AI-generated summary
- Click the "Regenerate Summary" button to create a new summary

### Theme Toggle

- Click the sun/moon icon in the top right to switch between light and dark modes

## Project Structure

```
notes-app/
├── app.py                  # Main Flask application
├── migrate_db.py           # Database migration script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── static/                 # Static assets
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── img/                # Images
└── templates/              # HTML templates
    ├── index.html          # Main application page
    └── login.html          # Login page
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Google Gemini AI for providing the summarization API
- Flask and SQLAlchemy for the backend framework
- All open-source libraries used in this project 