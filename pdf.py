# Complete PDF Viewer Application
# File: pdf_viewer_complete.py

# importing everything from tkinter
from tkinter import *
# importing ttk for styling widgets from tkinter
from tkinter import ttk
# importing filedialog from tkinter
from tkinter import filedialog as fd
# importing messagebox for error handling
from tkinter import messagebox
# importing os module
import os
# importing required libraries for PDF processing
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import io


# Windows 95 theme colors and styling
class Win95Theme:
    # Classic Windows 95 colors
    BG_COLOR = "#c0c0c0"  # Light gray background
    BUTTON_COLOR = "#c0c0c0"  # Button background
    BUTTON_ACTIVE = "#dfdfdf"  # Button when pressed
    TEXT_COLOR = "#000000"  # Black text
    DISABLED_TEXT = "#808080"  # Gray disabled text
    HIGHLIGHT_COLOR = "#000080"  # Navy blue for selection
    HIGHLIGHT_TEXT = "#ffffff"  # White text on selection
    WINDOW_BG = "#c0c0c0"  # Window background
    CANVAS_BG = "#ffffff"  # Canvas background (white for PDF)
    MENU_BG = "#c0c0c0"  # Menu background
    
    @staticmethod
    def configure_widget(widget, widget_type="default"):
        """Apply Windows 95 styling to widgets"""
        if widget_type == "button":
            widget.configure(
                relief="raised",
                borderwidth=2,
                background=Win95Theme.BUTTON_COLOR,
                foreground=Win95Theme.TEXT_COLOR,
                font=("MS Sans Serif", 8)
            )
        elif widget_type == "label":
            widget.configure(
                background=Win95Theme.BG_COLOR,
                foreground=Win95Theme.TEXT_COLOR,
                font=("MS Sans Serif", 8)
            )
        elif widget_type == "frame":
            widget.configure(
                background=Win95Theme.BG_COLOR,
                relief="sunken",
                borderwidth=2
            )
        elif widget_type == "canvas":
            widget.configure(
                background=Win95Theme.CANVAS_BG,
                relief="sunken",
                borderwidth=2,
                highlightthickness=0
            )


# PDFMiner class for handling PDF operations
class PDFMiner:
    def __init__(self, filepath):
        """
        Initialize PDFMiner with a PDF file path
        """
        self.filepath = filepath
        self.pdf_document = None
        self.load_document()
    
    def load_document(self):
        """
        Load the PDF document using PyMuPDF
        """
        try:
            self.pdf_document = fitz.open(self.filepath)
        except Exception as e:
            print(f"Error loading PDF: {e}")
            messagebox.showerror("Error", f"Failed to load PDF: {e}")
            self.pdf_document = None
    
    def get_metadata(self):
        """
        Extract metadata and number of pages from the PDF
        Returns: (metadata_dict, number_of_pages)
        """
        if not self.pdf_document:
            return {}, 0
        
        try:
            # Get metadata
            metadata = self.pdf_document.metadata
            
            # Get number of pages
            num_pages = len(self.pdf_document)
            
            return metadata, num_pages
        except Exception as e:
            print(f"Error getting metadata: {e}")
            return {}, 0
    
    def get_page(self, page_number, zoom_level=1.0):
        """
        Convert a PDF page to a PhotoImage for tkinter display
        Args:
            page_number: Page index (0-based)
            zoom_level: Zoom factor for the page
        Returns:
            PhotoImage object for tkinter
        """
        if not self.pdf_document:
            return None
        
        try:
            # Get the page
            page = self.pdf_document[page_number]
            
            # Create a transformation matrix with zoom
            base_scale = 1.5
            mat = fitz.Matrix(base_scale * zoom_level, base_scale * zoom_level)
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat)
            
            # Convert pixmap to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            # Convert PIL Image to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            return photo
            
        except Exception as e:
            print(f"Error rendering page {page_number}: {e}")
            return None
    
    def close(self):
        """
        Close the PDF document
        """
        if self.pdf_document:
            self.pdf_document.close()
    
    def __del__(self):
        """
        Cleanup when object is destroyed
        """
        self.close()


# creating a class called PDFViewer
class PDFViewer:
    # initializing the __init__ / special method
    def __init__(self, master):
        # path for the pdf doc
        self.path = None
        # state of the pdf doc, open or closed
        self.fileisopen = None
        # author of the pdf doc
        self.author = None
        # name for the pdf doc
        self.name = None
        # the current page for the pdf
        self.current_page = 0
        # total number of pages for the pdf doc
        self.numPages = None    
        # creating the window
        self.master = master
        # Apply Windows 95 theme to main window
        self.master.configure(bg=Win95Theme.WINDOW_BG)
        # gives title to the main window
        self.master.title('PDF Viewer - Windows 95 Style')
        # gives dimensions to main window
        self.master.geometry('800x700+200+100')
        # enable window resizing
        self.master.resizable(width = 1, height = 1)
        # set minimum window size
        self.master.minsize(600, 500)
        
        # Try to load icon, but continue if file not found
        try:
            self.master.iconbitmap('pdf_file_icon.ico')
        except:
            pass  # Icon file not found, continue without it
        
        # creating the menu
        self.menu = Menu(self.master)
        # adding it to the main window
        self.master.config(menu=self.menu)
        # creating a sub menu
        self.filemenu = Menu(self.menu)
        # giving the sub menu a label
        self.menu.add_cascade(label="File", menu=self.filemenu)
        # adding a two buttons to the sub menus
        self.filemenu.add_command(label="Open File", command=self.open_file)
        self.filemenu.add_command(label="Exit", command=self.master.destroy)
        
        # Configure grid weights for resizing
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        
        # creating the top frame
        self.top_frame = ttk.Frame(self.master)
        # placing the frame using inside main window using grid()
        self.top_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        # Configure grid weights for top frame
        self.top_frame.grid_rowconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(0, weight=1)
        
        # creating the bottom frame
        self.bottom_frame = ttk.Frame(self.master, height=60)
        # placing the frame using inside main window using grid()
        self.bottom_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        # Configure grid weights for bottom frame
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(4, weight=1)
        
        # creating a vertical scrollbar
        self.scrolly = Scrollbar(self.top_frame, orient=VERTICAL)
        # adding the scrollbar
        self.scrolly.grid(row=0, column=1, sticky="ns")
        
        # creating a horizontal scrollbar
        self.scrollx = Scrollbar(self.top_frame, orient=HORIZONTAL)
        # adding the scrollbar
        self.scrollx.grid(row=1, column=0, sticky="ew")
        
        # creating the canvas for display the PDF pages
        self.output = Canvas(self.top_frame, bg='#ECE8F3')
        # inserting both vertical and horizontal scrollbars to the canvas
        self.output.configure(yscrollcommand=self.scrolly.set, xscrollcommand=self.scrollx.set)
        # adding the canvas
        self.output.grid(row=0, column=0, sticky="nsew")
        # configuring the scrollbars to the canvas
        self.scrolly.configure(command=self.output.yview)
        self.scrollx.configure(command=self.output.xview)
        
        # Bind mouse wheel to canvas for scrolling
        self.output.bind("<MouseWheel>", self.on_mousewheel)
        self.output.bind("<Button-4>", self.on_mousewheel)  # Linux
        self.output.bind("<Button-5>", self.on_mousewheel)  # Linux
        self.output.bind("<Shift-MouseWheel>", self.on_horizontal_mousewheel)
        
        # Bind canvas resize event
        self.output.bind("<Configure>", self.on_canvas_configure)
        
        # Try to load button icons, create text buttons if images not found
        try:
            self.uparrow_icon = PhotoImage(file='uparrow.png')
            self.downarrow_icon = PhotoImage(file='downarrow.png')
            # resizing the icons to fit on buttons
            self.uparrow = self.uparrow_icon.subsample(3, 3)
            self.downarrow = self.downarrow_icon.subsample(3, 3)
            # creating buttons with icons
            self.upbutton = ttk.Button(self.bottom_frame, image=self.uparrow, command=self.previous_page)
            self.downbutton = ttk.Button(self.bottom_frame, image=self.downarrow, command=self.next_page)
        except:
            # If image files not found, create text buttons
            self.upbutton = ttk.Button(self.bottom_frame, text="↑ Prev", command=self.previous_page)
            self.downbutton = ttk.Button(self.bottom_frame, text="Next ↓", command=self.next_page)
        
        # adding the buttons with better positioning
        self.upbutton.grid(row=0, column=1, padx=5, pady=8)
        self.downbutton.grid(row=0, column=2, padx=5, pady=8)
        
        # label for displaying page numbers
        self.page_label = ttk.Label(self.bottom_frame, text='No PDF loaded')
        # adding the label
        self.page_label.grid(row=0, column=3, padx=10, pady=8)
        
        # Add zoom controls
        self.zoom_in_button = ttk.Button(self.bottom_frame, text="Zoom +", command=self.zoom_in)
        self.zoom_in_button.grid(row=0, column=5, padx=2, pady=8)
        
        self.zoom_out_button = ttk.Button(self.bottom_frame, text="Zoom -", command=self.zoom_out)
        self.zoom_out_button.grid(row=0, column=6, padx=2, pady=8)
        
        # Zoom level
        self.zoom_level = 1.0
        self.zoom_label = ttk.Label(self.bottom_frame, text="100%")
        self.zoom_label.grid(row=0, column=7, padx=5, pady=8)
        
        # Add welcome message to canvas
        self.output.create_text(400, 300, text="PDF Viewer\n\nClick File > Open File to load a PDF", 
                               font=("Arial", 16), fill="gray", justify=CENTER)
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if self.fileisopen:
            # Windows and MacOS
            if event.delta:
                delta = -1 * (event.delta / 120)
            # Linux
            else:
                if event.num == 4:
                    delta = -1
                else:
                    delta = 1
            
            self.output.yview_scroll(int(delta), "units")
    
    def on_horizontal_mousewheel(self, event):
        """Handle horizontal mouse wheel scrolling"""
        if self.fileisopen:
            if event.delta:
                delta = -1 * (event.delta / 120)
            else:
                if event.num == 4:
                    delta = -1
                else:
                    delta = 1
            
            self.output.xview_scroll(int(delta), "units")
    
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        if self.fileisopen:
            # Update scroll region when canvas is resized
            self.output.configure(scrollregion=self.output.bbox("all"))
    
    def zoom_in(self):
        """Increase zoom level"""
        if self.fileisopen:
            self.zoom_level *= 1.2
            self.update_zoom()
    
    def zoom_out(self):
        """Decrease zoom level"""
        if self.fileisopen:
            self.zoom_level /= 1.2
            if self.zoom_level < 0.1:
                self.zoom_level = 0.1
            self.update_zoom()
    
    def update_zoom(self):
        """Update the display with new zoom level"""
        if self.fileisopen:
            self.display_page()
            self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        
    # function for opening pdf files
    def open_file(self):
        # open the file dialog
        filepath = fd.askopenfilename(
            title='Select a PDF file', 
            initialdir=os.getcwd(), 
            filetypes=(('PDF', '*.pdf'), ('All files', '*.*'))
        )
        # checking if the file exists
        if filepath:
            try:
                # declaring the path
                self.path = filepath
                # extracting the pdf file from the path
                filename = os.path.basename(self.path)
                # passing the path to PDFMiner 
                self.miner = PDFMiner(self.path)
                # getting data and numPages
                data, numPages = self.miner.get_metadata()
                # setting the current page to 0
                self.current_page = 0
                # checking if numPages exists
                if numPages:
                    # getting the title
                    self.name = data.get('title', filename[:-4])
                    # getting the author
                    self.author = data.get('author', None)
                    self.numPages = numPages
                    # setting fileopen to True
                    self.fileisopen = True
                    # calling the display_page() function
                    self.display_page()
                    # replacing the window title with the PDF document name
                    self.master.title(f"PDF Viewer - {self.name}")
                else:
                    messagebox.showerror("Error", "Could not load PDF file. Please check if the file is valid.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open PDF file:\n{str(e)}")
    
    # the function to display the page  
    def display_page(self):
        # checking if numPages is less than current_page and if current_page is less than
        # or equal to 0
        if 0 <= self.current_page < self.numPages:
            try:
                # Clear the canvas
                self.output.delete("all")
                # getting the page using get_page() function from miner with zoom
                self.img_file = self.miner.get_page(self.current_page, self.zoom_level)
                if self.img_file:
                    # inserting the page image inside the Canvas
                    self.output.create_image(0, 0, anchor='nw', image=self.img_file)
                    # the variable to be stringified
                    self.stringified_current_page = self.current_page + 1
                    # updating the page label with number of pages 
                    self.page_label['text'] = str(self.stringified_current_page) + ' of ' + str(self.numPages)
                    # creating a region for inserting the page inside the Canvas
                    self.output.configure(scrollregion=self.output.bbox("all"))
                else:
                    self.output.create_text(400, 300, text="Error loading page", 
                                          font=("Arial", 16), fill="red", justify=CENTER)
            except Exception as e:
                print(f"Error displaying page: {e}")
                self.output.create_text(400, 300, text="Error displaying page", 
                                      font=("Arial", 16), fill="red", justify=CENTER)

    # function for displaying next page
    def next_page(self):
        # checking if file is open
        if self.fileisopen:
            # checking if current_page is less than numPages-1
            if self.current_page < self.numPages - 1:
                # updating the page with value 1
                self.current_page += 1
                # displaying the new page
                self.display_page()
                            
    # function for displaying the previous page        
    def previous_page(self):
        # checking if fileisopen
        if self.fileisopen:
            # checking if current_page is greater than 0
            if self.current_page > 0:
                # decrementing the current_page by 1
                self.current_page -= 1
                # displaying the previous page
                self.display_page()

    def __del__(self):
        """
        Cleanup when the viewer is destroyed
        """
        if hasattr(self, 'miner') and self.miner:
            self.miner.close()


# Main execution
if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import fitz
        from PIL import Image, ImageTk
    except ImportError as e:
        messagebox.showerror("Missing Dependencies", 
                           "Please install required packages:\n\n"
                           "pip install PyMuPDF Pillow\n\n"
                           f"Error: {e}")
        exit(1)
    
    # creating the rootpdfreaderroot window using Tk() class
    rootpdfreaderroot = Tk()
    # instantiating/creating object app for class PDFViewer
    app = PDFViewer(rootpdfreaderroot)
    # calling the mainloop to run the app infinitely until user closes it
    rootpdfreaderroot.mainloop()