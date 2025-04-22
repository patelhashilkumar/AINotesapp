import os
import json
from datetime import datetime

class NotesApp:
    def __init__(self):
        self.notes = []
        self.filename = "notes.json"
        self.load_notes()

    def load_notes(self):
        """Load notes from JSON file if it exists"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as file:
                    self.notes = json.load(file)
            except json.JSONDecodeError:
                print("Error reading notes file. Starting with empty notes.")
                self.notes = []

    def save_notes(self):
        """Save notes to JSON file"""
        with open(self.filename, 'w') as file:
            json.dump(self.notes, file, indent=4)

    def add_note(self, title, content):
        """Add a new note"""
        note = {
            'id': len(self.notes) + 1,
            'title': title,
            'content': content,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.notes.append(note)
        self.save_notes()
        print(f"Note '{title}' added successfully!")

    def view_notes(self):
        """View all notes"""
        if not self.notes:
            print("\nNo notes found!")
            return

        print("\nYour Notes:")
        print("-" * 50)
        for note in self.notes:
            print(f"\nNote ID: {note['id']}")
            print(f"Title: {note['title']}")
            print(f"Created: {note['timestamp']}")
            print(f"Content:\n{note['content']}")
            print("-" * 50)

    def delete_note(self, note_id):
        """Delete a note by ID"""
        for note in self.notes:
            if note['id'] == note_id:
                self.notes.remove(note)
                self.save_notes()
                print(f"Note {note_id} deleted successfully!")
                return
        print(f"Note with ID {note_id} not found!")

    def search_notes(self, keyword):
        """Search notes by keyword"""
        found_notes = []
        for note in self.notes:
            if (keyword.lower() in note['title'].lower() or 
                keyword.lower() in note['content'].lower()):
                found_notes.append(note)
        
        if not found_notes:
            print(f"\nNo notes found matching '{keyword}'")
            return

        print(f"\nFound {len(found_notes)} matching notes:")
        print("-" * 50)
        for note in found_notes:
            print(f"\nNote ID: {note['id']}")
            print(f"Title: {note['title']}")
            print(f"Created: {note['timestamp']}")
            print(f"Content:\n{note['content']}")
            print("-" * 50)

def main():
    app = NotesApp()
    
    while True:
        print("\n=== Notes App ===")
        print("1. Add Note")
        print("2. View Notes")
        print("3. Delete Note")
        print("4. Search Notes")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            title = input("Enter note title: ")
            print("Enter note content (press Enter twice to finish):")
            content_lines = []
            while True:
                line = input()
                if line == "":
                    break
                content_lines.append(line)
            content = "\n".join(content_lines)
            app.add_note(title, content)

        elif choice == '2':
            app.view_notes()

        elif choice == '3':
            try:
                note_id = int(input("Enter note ID to delete: "))
                app.delete_note(note_id)
            except ValueError:
                print("Please enter a valid note ID!")

        elif choice == '4':
            keyword = input("Enter search keyword: ")
            app.search_notes(keyword)

        elif choice == '5':
            print("Thank you for using Notes App!")
            break

        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 