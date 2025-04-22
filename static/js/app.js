document.addEventListener('DOMContentLoaded', () => {
    // Speech Recognition Setup
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    const startRecordingBtn = document.getElementById('start-recording');
    const stopRecordingBtn = document.getElementById('stop-recording');
    const noteContent = document.getElementById('note-content');

    startRecordingBtn.addEventListener('click', () => {
        recognition.start();
        startRecordingBtn.style.display = 'none';
        stopRecordingBtn.style.display = 'inline-flex';
    });

    stopRecordingBtn.addEventListener('click', () => {
        recognition.stop();
        startRecordingBtn.style.display = 'inline-flex';
        stopRecordingBtn.style.display = 'none';
    });

    recognition.addEventListener('result', (e) => {
        const transcript = Array.from(e.results)
            .map(result => result[0])
            .map(result => result.transcript)
            .join('');
        
        noteContent.value = transcript;
    });

    // Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });

    // DOM Elements
    const addNoteBtn = document.getElementById('add-note-btn');
    const noteModal = document.getElementById('note-modal');
    const noteForm = document.getElementById('note-form');
    const cancelBtn = document.getElementById('cancel-btn');
    const searchInput = document.getElementById('search-input');
    const notesContainer = document.getElementById('notes-container');
    const categoryButtons = document.querySelectorAll('.category-item');

    let currentNoteId = null;
    let currentCategory = 'all';

    // Load initial notes
    fetchNotes();

    // Event Listeners
    addNoteBtn.addEventListener('click', () => showModal());
    cancelBtn.addEventListener('click', hideModal);
    noteForm.addEventListener('submit', handleSubmit);
    searchInput.addEventListener('input', handleSearch);
    
    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            currentCategory = button.dataset.category;
            fetchNotes();
        });
    });

    // Add event listener for edit and delete buttons using event delegation
    document.addEventListener('click', async (e) => {
        const editBtn = e.target.closest('.edit-btn');
        const deleteBtn = e.target.closest('.delete-btn');
        
        if (editBtn) {
            e.stopPropagation(); // Prevent event bubbling
            const noteId = editBtn.dataset.id;
            const note = await fetchNoteById(noteId);
            if (note) showModal(note);
        } else if (deleteBtn) {
            e.stopPropagation(); // Prevent event bubbling
            if (confirm('Are you sure you want to delete this note?')) {
                const noteId = deleteBtn.dataset.id;
                try {
                    await fetch(`/notes/${noteId}`, { method: 'DELETE' });
                    fetchNotes();
                } catch (error) {
                    console.error('Error deleting note:', error);
                    alert('Error deleting note. Please try again.');
                }
            }
        }
    });

    // Add this new function to fetch a single note
    async function fetchNoteById(noteId) {
        try {
            const response = await fetch(`/notes/search?q=id:${noteId}`);
            const notes = await response.json();
            return notes.length > 0 ? notes[0] : null;
        } catch (error) {
            console.error('Error fetching note:', error);
            return null;
        }
    }

    // Functions
    function showModal(note = null) {
        const modalTitle = document.getElementById('modal-title');
        const titleInput = document.getElementById('note-title');
        const contentInput = document.getElementById('note-content');
        const categorySelect = document.getElementById('note-category');
        const form = document.getElementById('note-form');

        if (note) {
            modalTitle.textContent = 'Edit Note';
            titleInput.value = note.title;
            contentInput.value = note.content;
            categorySelect.value = note.category || 'work';
            form.dataset.noteId = note.id;
        } else {
            modalTitle.textContent = 'Add New Note';
            form.reset();
            delete form.dataset.noteId;
        }

        noteModal.classList.add('active');
    }

    function hideModal() {
        noteModal.classList.remove('active');
        noteForm.reset();
        currentNoteId = null;
        // Reset modal content to its original state
        const modalContent = document.querySelector('.modal-content');
        if (modalContent.style.maxWidth) {
            modalContent.style.maxWidth = '';
        }
    }

    function showExpandedNote(note) {
        const modalContent = document.querySelector('.modal-content');
        // Remove any inline styles that might have been set
        modalContent.removeAttribute('style');
        
        modalContent.innerHTML = `
            <div class="expanded-note">
                <div class="expanded-header">
                    <div class="header-left">
                        <span class="note-category category-${note.category}">${note.category}</span>
                        <h2>${note.title}</h2>
                    </div>
                    <div class="expanded-actions">
                        <button class="action-btn edit-btn" data-id="${note.id}" title="Edit">✏️</button>
                        <button class="action-btn close-btn" title="Close">✕</button>
                    </div>
                </div>
                <div class="expanded-content">
                    <p>${note.content}</p>
                    <div class="note-summary">
                        <div class="summary-header">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                <polyline points="14 2 14 8 20 8"></polyline>
                                <line x1="16" y1="13" x2="8" y2="13"></line>
                                <line x1="16" y1="17" x2="8" y2="17"></line>
                                <line x1="10" y1="9" x2="8" y2="9"></line>
                            </svg>
                            <span>Summary</span>
                        </div>
                        ${note.summary ? `<p>${note.summary}</p>` : '<p class="no-summary">No summary available.</p>'}
                    </div>
                    <div class="note-footer">
                        <span class="note-timestamp">${formatDate(note.created_at)}</span>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners
        const closeBtn = modalContent.querySelector('.close-btn');
        const editBtn = modalContent.querySelector('.edit-btn');

        closeBtn.addEventListener('click', hideModal);
        editBtn.addEventListener('click', () => {
            hideModal();
            showModal(note);
        });

        // Show the modal
        noteModal.classList.add('active');

        // Close expanded note when clicking outside
        noteModal.addEventListener('click', (e) => {
            if (e.target === noteModal) {
                hideModal();
            }
        }, { once: true });

        // Handle keyboard shortcuts
        const handleKeyPress = (e) => {
            if (e.key === 'Escape') {
                hideModal();
            }
        };

        document.addEventListener('keydown', handleKeyPress);
        noteModal.addEventListener('hide', () => {
            document.removeEventListener('keydown', handleKeyPress);
        }, { once: true });
    }

    async function handleSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const noteId = form.dataset.noteId;

        const formData = {
            title: document.getElementById('note-title').value.trim(),
            content: document.getElementById('note-content').value.trim(),
            category: document.getElementById('note-category').value
        };

        if (!formData.title || !formData.content) {
            alert('Title and content are required!');
            return;
        }

        try {
            const url = noteId ? `/notes/${noteId}` : '/notes';
            const method = noteId ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('Failed to save note');
            }

            hideModal();
            fetchNotes();
        } catch (error) {
            console.error('Error saving note:', error);
            alert('Error saving note. Please try again.');
        }
    }

    async function fetchNotes() {
        try {
            const response = await fetch('/notes/search' + (searchInput.value ? `?q=${searchInput.value}` : ''));
            const notes = await response.json();
            displayNotes(notes);
            updateCategoryCounts(notes);
        } catch (error) {
            console.error('Error fetching notes:', error);
            notesContainer.innerHTML = '<p class="error">Error loading notes. Please try again.</p>';
        }
    }

    function displayNotes(notes) {
        const filteredNotes = currentCategory === 'all' 
            ? notes 
            : notes.filter(note => note.category === currentCategory);

        notesContainer.innerHTML = filteredNotes.length === 0 
            ? '<p class="no-notes">No notes found</p>'
            : filteredNotes.map(note => createNoteCard(note)).join('');

        // Add drag and drop functionality
        setupDragAndDrop();

        // Add click event listeners to note cards
        document.querySelectorAll('.note-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.closest('.note-actions')) {
                    const noteId = card.querySelector('.edit-btn').dataset.id;
                    const note = notes.find(n => n.id === parseInt(noteId));
                    showExpandedNote(note);
                }
            });
        });

        // Add event listeners to action buttons
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const noteId = btn.dataset.id;
                const note = notes.find(n => n.id === parseInt(noteId));
                if (note) showModal(note);
            });
        });

        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                if (confirm('Are you sure you want to delete this note?')) {
                    const noteId = btn.dataset.id;
                    try {
                        await fetch(`/notes/${noteId}`, { method: 'DELETE' });
                        fetchNotes();
                    } catch (error) {
                        console.error('Error deleting note:', error);
                        alert('Error deleting note. Please try again.');
                    }
                }
            });
        });
    }

    function setupDragAndDrop() {
        const cards = document.querySelectorAll('.note-card');
        let draggedCard = null;

        cards.forEach(card => {
            card.setAttribute('draggable', true);
            
            card.addEventListener('dragstart', (e) => {
                draggedCard = card;
                card.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
            });

            card.addEventListener('dragend', () => {
                draggedCard.classList.remove('dragging');
                document.querySelectorAll('.note-card').forEach(card => {
                    card.classList.remove('drag-over');
                });
                draggedCard = null;
            });

            card.addEventListener('dragover', (e) => {
                e.preventDefault();
                if (draggedCard !== card) {
                    card.classList.add('drag-over');
                }
            });

            card.addEventListener('dragleave', () => {
                card.classList.remove('drag-over');
            });

            card.addEventListener('drop', (e) => {
                e.preventDefault();
                if (draggedCard !== card) {
                    const allCards = [...document.querySelectorAll('.note-card')];
                    const draggedIndex = allCards.indexOf(draggedCard);
                    const droppedIndex = allCards.indexOf(card);

                    // Update the order in the DOM
                    if (draggedIndex < droppedIndex) {
                        card.parentNode.insertBefore(draggedCard, card.nextSibling);
                    } else {
                        card.parentNode.insertBefore(draggedCard, card);
                    }

                    // Save the new order to the server
                    saveNotesOrder();
                }
                card.classList.remove('drag-over');
            });
        });
    }

    async function saveNotesOrder() {
        const cards = document.querySelectorAll('.note-card');
        const order = Array.from(cards).map(card => {
            const noteId = card.querySelector('.edit-btn').dataset.id;
            return parseInt(noteId);
        });

        try {
            await fetch('/notes/reorder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ order })
            });
        } catch (error) {
            console.error('Error saving notes order:', error);
        }
    }

    function createNoteCard(note) {
        return `
            <div class="note-card">
                <div class="note-content-wrapper">
                    <span class="note-category category-${note.category}">${note.category}</span>
                    <h3 class="note-title">${note.title}</h3>
                    <p class="note-content">${note.content}</p>
                    <div class="note-summary">
                        <div class="summary-header">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                <polyline points="14 2 14 8 20 8"></polyline>
                                <line x1="16" y1="13" x2="8" y2="13"></line>
                                <line x1="16" y1="17" x2="8" y2="17"></line>
                                <line x1="10" y1="9" x2="8" y2="9"></line>
                            </svg>
                            <span>Summary</span>
                        </div>
                        ${note.summary ? `<p>${note.summary}</p>` : '<p class="no-summary">No summary yet. Click to generate one.</p>'}
                    </div>
                </div>
                <div class="note-footer">
                    <span class="note-timestamp">${formatDate(note.created_at)}</span>
                    <div class="note-actions">
                        <button class="action-btn edit-btn" data-id="${note.id}" title="Edit">✏️</button>
                        <button class="action-btn delete-btn" data-id="${note.id}" title="Delete">🗑️</button>
                    </div>
                </div>
            </div>
        `;
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function updateCategoryCounts(notes) {
        const counts = {
            all: notes.length,
            work: notes.filter(note => note.category === 'work').length,
            personal: notes.filter(note => note.category === 'personal').length,
            ideas: notes.filter(note => note.category === 'ideas').length
        };

        Object.entries(counts).forEach(([category, count]) => {
            const countElement = document.getElementById(`${category}-count`);
            if (countElement) countElement.textContent = count;
        });
    }

    let searchTimeout;
    function handleSearch() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(fetchNotes, 300);
    }
});