import PyPDF2
import pyttsx3
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox, Frame
import threading
import time


class PDFReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Reader with TTS")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")  # Set a light background color

        # Variables
        self.pdf_path = None
        self.tts_thread = None
        self.engine = pyttsx3.init()
        self.is_paused = False
        self.stop_reading = False

        # GUI Elements
        self.create_widgets()

    def create_widgets(self):
        # Title Frame
        title_frame = Frame(self.root, bg="#3c4f76", height=60)
        title_frame.pack(fill="x")

        title_label = Label(
            title_frame,
            text="PDF Reader with Text-to-Speech",
            font=("Arial", 16, "bold"),
            bg="#3c4f76",
            fg="white",
        )
        title_label.pack(pady=10)

        # Content Frame
        content_frame = Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)

        # File Selection Section
        Label(
            content_frame, text="Select a PDF File:", font=("Arial", 12), bg="#f0f0f0"
        ).grid(row=0, column=0, sticky="w", pady=5)

        Button(
            content_frame,
            text="Browse",
            command=self.browse_file,
            bg="#3c4f76",
            fg="white",
            font=("Arial", 10, "bold"),
        ).grid(row=0, column=1, padx=10, pady=5)

        # Page Range Section
        Label(
            content_frame,
            text="Enter Page Range (e.g., 1-3):",
            font=("Arial", 12),
            bg="#f0f0f0",
        ).grid(row=1, column=0, sticky="w", pady=5)

        self.page_range_entry = Entry(content_frame, width=20, font=("Arial", 12))
        self.page_range_entry.grid(row=1, column=1, pady=5)

        # Control Buttons Section
        button_frame = Frame(content_frame, bg="#f0f0f0", pady=20)
        button_frame.grid(row=2, column=0, columnspan=2)

        Button(
            button_frame,
            text="Read PDF",
            command=self.start_reading_thread,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
        ).grid(row=0, column=0, padx=10)

        Button(
            button_frame,
            text="Pause",
            command=self.pause_tts,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
        ).grid(row=0, column=1, padx=10)

        Button(
            button_frame,
            text="Resume",
            command=self.resume_tts,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
        ).grid(row=1, column=0, pady=10)

        Button(
            button_frame,
            text="Quit",
            command=self.quit_application,
            bg="#F44336",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
        ).grid(row=1, column=1, pady=10)

    def browse_file(self):
        """Open a file dialog to select a PDF."""
        self.pdf_path = filedialog.askopenfilename(
            title="Select a PDF file",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if self.pdf_path:
            messagebox.showinfo("File Selected", f"Selected: {self.pdf_path}")

    def start_reading_thread(self):
        """Start a separate thread for reading the PDF."""
        if not self.pdf_path:
            messagebox.showerror("Error", "Please select a PDF file first!")
            return

        # Get the page range from the user
        page_range = self.page_range_entry.get().strip()
        if not page_range:
            messagebox.showerror("Error", "Please enter a page range!")
            return

        try:
            # Parse the page range
            start_page, end_page = map(int, page_range.split('-'))
            start_page -= 1  # Convert to zero-based index

            # Open the PDF and validate page range
            with open(self.pdf_path, 'rb') as file:
                pdfReader = PyPDF2.PdfReader(file)
                total_pages = len(pdfReader.pages)
                if start_page < 0 or end_page > total_pages or start_page >= end_page:
                    messagebox.showerror("Error", "Invalid page range!")
                    return

                # Extract text from the selected pages
                text = ""
                for page_num in range(start_page, end_page):
                    text += pdfReader.pages[page_num].extract_text()

                if not text.strip():
                    messagebox.showinfo("Info", "No text found in the selected page range!")
                    return

                # Start TTS in a separate thread
                self.stop_reading = False
                self.tts_thread = threading.Thread(target=self.text_to_speech, args=(text,))
                self.tts_thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def text_to_speech(self, text):
        """Convert the given text to speech."""
        try:
            words = text.split()
            for word in words:
                if self.stop_reading:
                    break

                while self.is_paused:
                    time.sleep(0.1)  # Wait while paused

                self.engine.say(word)
                self.engine.runAndWait()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during text-to-speech: {e}")

    def pause_tts(self):
        """Pause the text-to-speech."""
        if not self.stop_reading:
            self.is_paused = True
            messagebox.showinfo("Paused", "Speech has been paused.")

    def resume_tts(self):
        """Resume the text-to-speech."""
        if not self.stop_reading and self.is_paused:
            self.is_paused = False
            messagebox.showinfo("Resumed", "Speech has resumed.")

    def quit_application(self):
        """Stop the TTS and quit the application."""
        self.stop_reading = True
        self.engine.stop()
        self.root.quit()


# Run the GUI Application
if __name__ == "__main__":
    root = Tk()
    app = PDFReaderApp(root)
    root.mainloop()
