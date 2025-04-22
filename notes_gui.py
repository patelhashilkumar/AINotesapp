import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime
from ttkthemes import ThemedTk
from PIL import Image, ImageTk  # Add PIL import for handling images

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notes App")
        self.root.geometry("1000x600")
        
        # Initialize notes data
        self.notes = []
        self.filename = "notes.json"
        self.load_notes()
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('Sidebar.TFrame', background='#2d2d2d')
        self.style.configure('Main.TFrame', background='#1e1e1e')
        self.style.configure('Search.TEntry', fieldbackground='#333333', foreground='white')
        self.style.configure('Note.TFrame', background='#333333')
        self.style.configure('Dragging.TFrame', background='#444444')  # Style for dragging state
        
        # Track focused note
        self.focused_note = None
        self.focused_note_frame = None
        
        # Configure logout button style
        self.style.configure('Logout.TButton',
                           background='#2d2d2d',
                           foreground='white',
                           font=('Helvetica', 11),
                           padding=10)
        
        # Create main layout
        self.create_layout()
        
        # Load initial notes
        self.display_notes()

    def create_layout(self):
        # Main container
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = ttk.Frame(self.main_container, style='Sidebar.TFrame', width=200)
        self.main_container.add(self.sidebar, weight=1)
        
        # Top section of sidebar
        sidebar_top = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        sidebar_top.pack(fill=tk.X, expand=False)
        
        # Sidebar title
        title_label = ttk.Label(sidebar_top, text="Notes App", 
                              font=('Helvetica', 16, 'bold'), 
                              foreground='white', 
                              background='#2d2d2d')
        title_label.pack(pady=20, padx=10)

        # Add Note button
        self.add_button = ttk.Button(sidebar_top, text="+ Add New Note", 
                                   command=self.show_add_note_dialog)
        self.add_button.pack(pady=10, padx=10, fill=tk.X)

        # Create a frame that will expand to push the logout button to the bottom
        spacer_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        spacer_frame.pack(fill=tk.BOTH, expand=True)

        # Logout button with icon
        logout_button = tk.Button(
            self.sidebar,
            text="↪ Logout",  # Using an arrow icon
            command=self.root.quit,
            font=('Helvetica', 11),
            fg='white',
            bg='#8B3E3E',  # Reddish background color
            activebackground='#A04444',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=10,
            cursor='hand2'
        )
        logout_button.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)

        # Main content area
        self.main_content = ttk.Frame(self.main_container, style='Main.TFrame')
        self.main_container.add(self.main_content, weight=4)

        # Search frame
        search_frame = ttk.Frame(self.main_content, style='Main.TFrame')
        search_frame.pack(fill=tk.X, padx=20, pady=20)

        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.search_entry = ttk.Entry(search_frame, 
                                    textvariable=self.search_var,
                                    style='Search.TEntry',
                                    font=('Helvetica', 11))
        self.search_entry.pack(fill=tk.X)
        self.search_entry.insert(0, "Search notes...")
        self.search_entry.bind('<FocusIn>', self.on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self.on_search_focus_out)

        # Notes container (scrollable)
        self.canvas = tk.Canvas(self.main_content, bg='#1e1e1e', 
                              highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_content, 
                                     orient=tk.VERTICAL, 
                                     command=self.canvas.yview)
        self.notes_frame = ttk.Frame(self.canvas, style='Main.TFrame')

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollbar and canvas
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window in canvas for notes
        self.canvas_frame = self.canvas.create_window((0, 0), 
                                                    window=self.notes_frame, 
                                                    anchor='nw', 
                                                    width=self.canvas.winfo_width())
        
        # Configure canvas scrolling
        self.notes_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

    def load_notes(self):
        """Load notes from JSON file if it exists"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as file:
                    self.notes = json.load(file)
            except json.JSONDecodeError:
                self.notes = []

    def save_notes(self):
        """Save notes to JSON file"""
        with open(self.filename, 'w') as file:
            json.dump(self.notes, file, indent=4)

    def create_note_frame(self, note, parent):
        """Create a frame for a single note"""
        # Create main note frame with fixed width
        note_frame = ttk.Frame(parent, style='Note.TFrame')
        note_frame.pack(fill=tk.X, padx=20, pady=10)
        note_frame.pack_propagate(False)  # Prevent frame from auto-resizing
        note_frame.configure(height=200)  # Set fixed height for note cards
        
        # Make the frame draggable
        note_frame.bind('<Button-1>', lambda e: self.start_drag(e, note_frame))
        note_frame.bind('<B1-Motion>', lambda e: self.drag(e, note_frame))
        note_frame.bind('<ButtonRelease-1>', lambda e: self.stop_drag(e, note_frame))
        
        # Content frame to hold all note elements
        content_frame = ttk.Frame(note_frame, style='Note.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Category label (WORK, etc)
        category_label = ttk.Label(
            content_frame,
            text="WORK",
            background='#e74c4c',
            foreground='white',
            padding=(10, 5)
        )
        category_label.pack(anchor='w', pady=(0, 10))

        # Title
        title_label = ttk.Label(
            content_frame,
            text=note['title'],
            font=('Helvetica', 12, 'bold'),
            foreground='white',
            background='#333333',
            wraplength=400
        )
        title_label.pack(anchor='w', pady=(0, 10))

        # Content preview with ellipsis
        content_text = note['content']
        if len(content_text) > 100:
            content_text = content_text[:100] + "..."
            
        content_label = ttk.Label(
            content_frame,
            text=content_text,
            wraplength=400,
            foreground='#cccccc',
            background='#333333',
            justify=tk.LEFT
        )
        content_label.pack(anchor='w', pady=(0, 10))

        # Bottom frame for timestamp and buttons
        bottom_frame = ttk.Frame(content_frame, style='Note.TFrame')
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Timestamp on the left
        time_label = ttk.Label(
            bottom_frame,
            text=note['timestamp'],
            font=('Helvetica', 8),
            foreground='#888888',
            background='#333333'
        )
        time_label.pack(side=tk.LEFT)

        # Action buttons on the right
        button_frame = ttk.Frame(bottom_frame, style='Note.TFrame')
        button_frame.pack(side=tk.RIGHT)

        # Edit button
        edit_button = tk.Button(
            button_frame,
            text="✏️",
            font=('Helvetica', 10),
            fg='#cccccc',
            bg='#333333',
            activebackground='#444444',
            activeforeground='white',
            relief=tk.FLAT,
            borderwidth=0,
            cursor='hand2',
            command=lambda: self.edit_note(note)
        )
        edit_button.pack(side=tk.LEFT, padx=2)

        # Delete button
        delete_button = tk.Button(
            button_frame,
            text="🗑️",
            font=('Helvetica', 10),
            fg='#cccccc',
            bg='#333333',
            activebackground='#444444',
            activeforeground='white',
            relief=tk.FLAT,
            borderwidth=0,
            cursor='hand2',
            command=lambda: self.delete_note(note['id'])
        )
        delete_button.pack(side=tk.LEFT, padx=2)

        # Make the note clickable for focus view
        for widget in [note_frame, content_frame, title_label, content_label]:
            widget.bind('<Button-1>', lambda e, n=note: self.show_note_in_focus(n))
            widget.configure(cursor='hand2')

    def start_drag(self, event, widget):
        """Start dragging a note card"""
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y
        widget._drag_start_pos = widget.winfo_y()
        widget.configure(style='Dragging.TFrame')
        
    def drag(self, event, widget):
        """Handle dragging of a note card"""
        if hasattr(widget, '_drag_start_y'):
            # Calculate new position
            new_y = widget._drag_start_pos + (event.y - widget._drag_start_y)
            
            # Get all note frames
            all_notes = [w for w in widget.master.winfo_children() 
                        if isinstance(w, ttk.Frame) and w != widget]
            
            # Find the note we're hovering over
            for note in all_notes:
                note_y = note.winfo_y()
                if abs(new_y - note_y) < 50:  # If we're close to another note
                    # Swap positions
                    if new_y < note_y:
                        note.pack_forget()
                        note.pack(fill=tk.X, padx=20, pady=10, before=widget)
                    else:
                        note.pack_forget()
                        note.pack(fill=tk.X, padx=20, pady=10, after=widget)
                    break
            
            # Update the dragged widget's position
            widget.pack_forget()
            widget.pack(fill=tk.X, padx=20, pady=10)
            
    def stop_drag(self, event, widget):
        """Stop dragging a note card"""
        if hasattr(widget, '_drag_start_y'):
            del widget._drag_start_x
            del widget._drag_start_y
            del widget._drag_start_pos
            widget.configure(style='Note.TFrame')
            
    def display_notes(self, filter_text=""):
        """Display all notes or filtered notes"""
        # Clear existing notes
        for widget in self.notes_frame.winfo_children():
            widget.destroy()

        # Filter and display notes
        for note in self.notes:
            if (filter_text.lower() in note['title'].lower() or 
                filter_text.lower() in note['content'].lower()):
                self.create_note_frame(note, self.notes_frame)

    def show_add_note_dialog(self):
        """Show dialog to add a new note"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Note")
        dialog.geometry("500x400")
        dialog.configure(bg='#2d2d2d')

        # Title entry
        title_label = ttk.Label(dialog, text="Title:", 
                              foreground='white', background='#2d2d2d')
        title_label.pack(padx=20, pady=(20, 5))
        
        title_entry = ttk.Entry(dialog, width=50)
        title_entry.pack(padx=20, pady=(0, 20))

        # Content text
        content_label = ttk.Label(dialog, text="Content:", 
                                foreground='white', background='#2d2d2d')
        content_label.pack(padx=20, pady=(0, 5))
        
        content_text = scrolledtext.ScrolledText(dialog, width=50, height=10)
        content_text.pack(padx=20, pady=(0, 20))

        def save():
            title = title_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            
            if not title or not content:
                messagebox.showerror("Error", "Both title and content are required!")
                return

            note = {
                'id': len(self.notes) + 1,
                'title': title,
                'content': content,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.notes.append(note)
            self.save_notes()
            self.display_notes()
            dialog.destroy()

        # Save button
        save_btn = ttk.Button(dialog, text="Save Note", command=save)
        save_btn.pack(pady=20)

    def edit_note(self, note):
        """Show dialog to edit an existing note"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Note")
        dialog.geometry("500x400")
        dialog.configure(bg='#2d2d2d')

        # Title entry
        title_label = ttk.Label(dialog, text="Title:", 
                              foreground='white', background='#2d2d2d')
        title_label.pack(padx=20, pady=(20, 5))
        
        title_entry = ttk.Entry(dialog, width=50)
        title_entry.insert(0, note['title'])
        title_entry.pack(padx=20, pady=(0, 20))

        # Content text
        content_label = ttk.Label(dialog, text="Content:", 
                                foreground='white', background='#2d2d2d')
        content_label.pack(padx=20, pady=(0, 5))
        
        content_text = scrolledtext.ScrolledText(dialog, width=50, height=10)
        content_text.insert("1.0", note['content'])
        content_text.pack(padx=20, pady=(0, 20))

        def save():
            title = title_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            
            if not title or not content:
                messagebox.showerror("Error", "Both title and content are required!")
                return

            # Update note
            note['title'] = title
            note['content'] = content
            note['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.save_notes()
            self.display_notes()
            dialog.destroy()

        # Save button
        save_btn = ttk.Button(dialog, text="Save Changes", command=save)
        save_btn.pack(pady=20)

    def delete_note(self, note_id):
        """Delete a note"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this note?"):
            self.notes = [note for note in self.notes if note['id'] != note_id]
            self.save_notes()
            self.display_notes()

    def on_search_change(self, *args):
        """Handle search input changes"""
        search_text = self.search_var.get()
        if search_text != "Search notes...":
            self.display_notes(search_text)

    def on_search_focus_in(self, event):
        """Clear placeholder text when search entry is focused"""
        if self.search_var.get() == "Search notes...":
            self.search_var.set("")

    def on_search_focus_out(self, event):
        """Restore placeholder text when search entry loses focus"""
        if not self.search_var.get():
            self.search_var.set("Search notes...")

    def on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """When canvas is resized, resize the inner frame to match"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def show_note_in_focus(self, note):
        """Show a single note in focus/detail view"""
        # Create a new dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title(note['title'])
        dialog.geometry("800x600")
        dialog.configure(bg='#1e1e1e')
        
        # Make it modal (user must interact with this window first)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main content frame
        main_frame = ttk.Frame(dialog, style='Note.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Category label (WORK, etc)
        category_label = ttk.Label(
            main_frame,
            text="WORK",
            background='#e74c4c',  # Red background
            foreground='white',
            padding=(10, 5)
        )
        category_label.pack(anchor='w', pady=(0, 10))
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=note['title'],
            font=('Helvetica', 16, 'bold'),
            foreground='white',
            background='#333333'
        )
        title_label.pack(anchor='w', pady=(0, 20))
        
        # Content
        content_label = ttk.Label(
            main_frame,
            text=note['content'],
            wraplength=700,
            justify=tk.LEFT,
            foreground='#cccccc',
            background='#333333'
        )
        content_label.pack(anchor='w', pady=(0, 20))
        
        # Summary section
        summary_frame = ttk.Frame(main_frame, style='Note.TFrame')
        summary_frame.pack(fill=tk.X, pady=(20, 0))
        
        summary_label = ttk.Label(
            summary_frame,
            text="Summary",
            font=('Helvetica', 12),
            foreground='#888888',
            background='#333333'
        )
        summary_label.pack(anchor='w')
        
        # Add timestamp at the bottom
        time_label = ttk.Label(
            main_frame,
            text=note['timestamp'],
            font=('Helvetica', 8),
            foreground='#888888',
            background='#333333'
        )
        time_label.pack(anchor='w', pady=(20, 0))
        
        # Bind Escape key to close the dialog
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Center the dialog on screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

def main():
    root = ThemedTk(theme="equilux")
    app = NotesApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 