import tkinter as tk
from tkinter import ttk
import time
import threading
import os
import getpass
import socket

def check_database():
    """Check Config folder and mark_init.inst95 file"""
    config_dir = "Config"
    config_file = os.path.join(config_dir, "mark_init.inst95")
    
    # Create Config directory if it doesn't exist
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)
        except:
            show_config_error()
            return False
    
    # Check if mark_init.inst95 exists and contains "True"
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                content = f.read().strip()
                if content == "True":
                    print("pass")
                    return False  # Don't run installer
                else:
                    show_config_error()
                    return False
        except:
            pass
    
    return True  # Run installer

def show_config_error():
    """Show Windows 95 style error dialog"""
    error_root = tk.Tk()
    error_root.title("Multiapp 95 Professional Setup")
    error_root.geometry("400x150")
    error_root.configure(bg='#c0c0c0')
    error_root.resizable(False, False)
    error_root.overrideredirect(True)
    
    # Center the error window
    error_root.update_idletasks()
    x = (error_root.winfo_screenwidth() // 2) - (400 // 2)
    y = (error_root.winfo_screenheight() // 2) - (150 // 2)
    error_root.geometry(f"400x170+{x}+{y}")
    
    # Main frame
    main_frame = tk.Frame(error_root, bg='#c0c0c0', relief='raised', bd=2)
    main_frame.pack(fill='both', expand=True, padx=2, pady=2)
    
    # Header
    header_frame = tk.Frame(main_frame, bg='#000080', height=30)
    header_frame.pack(fill='x')
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text="Multiapp 95 Professional Setup - Error", bg='#000080', fg='white', 
                          font=('MS Sans Serif', 10, 'bold'))
    title_label.pack(anchor='w', padx=10, pady=5)
    
    # Content
    content_frame = tk.Frame(main_frame, bg='#c0c0c0')
    content_frame.pack(fill='both', expand=True, padx=20, pady=15)
    
    # Error icon and message
    msg_frame = tk.Frame(content_frame, bg='#c0c0c0')
    msg_frame.pack(expand=True)
    
    # Error icon (using text)
    icon_label = tk.Label(msg_frame, text="!", bg='#c0c0c0', fg='red', 
                         font=('MS Sans Serif', 24))
    icon_label.pack(side='left', padx=(0, 15))
    
    # Error message
    error_msg = tk.Label(msg_frame, text="Cannot create configuration for Multiapp 95 Professional.\n\nSetup cannot continue due to\ninsufficient permissions or corrupted files.", 
                        bg='#c0c0c0', font=('MS Sans Serif', 9), justify='left')
    error_msg.pack(side='left')
    
    # Button
    button_frame = tk.Frame(main_frame, bg='#c0c0c0')
    button_frame.pack(side='bottom', fill='x', padx=10, pady=10)
    
    ok_button = tk.Button(button_frame, text='OK', command=error_root.destroy,
                         width=10, height=1, font=('MS Sans Serif', 8))
    ok_button.pack(side='right', padx=5)
    
    # Bind ESC to close
    error_root.bind('<Escape>', lambda e: error_root.destroy())
    
    error_root.mainloop()

def write_completion_flag():
    """Write completion flag to Config/mark_init.inst95"""
    config_dir = "Config"
    config_file = os.path.join(config_dir, "mark_init.inst95")
    
    try:
        # Ensure Config directory exists
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # Write True to mark_init.inst95
        with open(config_file, "w") as f:
            f.write("True")
    except:
        pass

class Windows95Installer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Multiapp 95 Professional Setup")
        self.root.geometry("640x480")
        self.root.configure(bg='#c0c0c0')
        self.root.resizable(False, False)
        
        # Remove title bar
        self.root.overrideredirect(True)
        
        # Center the window
        self.center_window()
        
        # Fullscreen state
        self.is_fullscreen = False
        self.normal_geometry = "640x480"
        
        # Get actual system info
        self.actual_user = getpass.getuser()
        self.actual_computer = socket.gethostname()
        
        # Variables with actual system values
        self.current_step = 0
        self.progress_value = 0
        self.user_name = tk.StringVar(value=self.actual_user)
        self.computer_name = tk.StringVar(value=self.actual_computer)
        self.workgroup = tk.StringVar(value="WORKGROUP")
        self.timezone = tk.StringVar(value="(GMT-08:00) Pacific Time (US & Canada)")
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg='#c0c0c0', relief='raised', bd=2)
        self.main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Start installation
        self.show_welcome_screen()
        
        # Bind escape key to toggle fullscreen
        self.root.bind('<Escape>', self.toggle_fullscreen)
    
    def show_validation_error(self, error_type):
        """Show Windows 95 style validation error dialog"""
        error_root = tk.Tk()
        error_root.title("Multiapp 95 Professional Setup")
        error_root.geometry("450x180")
        error_root.configure(bg='#c0c0c0')
        error_root.resizable(False, False)
        error_root.overrideredirect(True)
        
        # Center the error window
        error_root.update_idletasks()
        x = (error_root.winfo_screenwidth() // 2) - (450 // 2)
        y = (error_root.winfo_screenheight() // 2) - (180 // 2)
        error_root.geometry(f"450x200+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(error_root, bg='#c0c0c0', relief='raised', bd=2)
        main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#000080', height=30)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Multiapp 95 Professional Setup - Validation Error", bg='#000080', fg='white', 
                              font=('MS Sans Serif', 10, 'bold'))
        title_label.pack(anchor='w', padx=10, pady=5)
        
        # Content
        content_frame = tk.Frame(main_frame, bg='#c0c0c0')
        content_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Error icon and message
        msg_frame = tk.Frame(content_frame, bg='#c0c0c0')
        msg_frame.pack(expand=True)
        
        # Error icon
        icon_label = tk.Label(msg_frame, text="X", bg='#c0c0c0', fg='red', 
                             font=('MS Sans Serif', 24))
        icon_label.pack(side='left', padx=(0, 15))
        
        # Error message based on type
        if error_type == "user":
            error_text = f"Invalid user name!\n\nThe entered user name does not match\nthe current system user: {self.actual_user}\n\nPlease enter the correct user name."
        else:  # computer
            error_text = f"Invalid computer name!\n\nThe entered computer name does not match\nthe current system name: {self.actual_computer}\n\nPlease enter the correct computer name."
        
        error_msg = tk.Label(msg_frame, text=error_text, 
                            bg='#c0c0c0', font=('MS Sans Serif', 9), justify='left')
        error_msg.pack(side='left')
        
        # Button
        button_frame = tk.Frame(main_frame, bg='#c0c0c0')
        button_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        
        ok_button = tk.Button(button_frame, text='OK', command=error_root.destroy,
                             width=10, height=1, font=('MS Sans Serif', 8))
        ok_button.pack(side='right', padx=5)
        
        # Bind ESC to close
        error_root.bind('<Escape>', lambda e: error_root.destroy())
        
        error_root.mainloop()
    
    def validate_and_continue_from_user_info(self):
        entered_user = self.user_name.get().strip()
        if entered_user != self.actual_user:
            self.show_validation_error("user")
            return
        self.show_computer_name()
        
    def validate_and_continue_from_computer_name(self):
        entered_computer = self.computer_name.get().strip()
        if entered_computer != self.actual_computer:
            self.show_validation_error("computer")
            return
        self.show_components()
    
    def toggle_fullscreen(self, event=None):
        """Toggle between fullscreen and windowed mode"""
        if self.is_fullscreen:
            # Exit fullscreen - restore to exact original state
            self.root.state('normal')  # First normalize the window
            self.root.geometry(self.normal_geometry)  # Restore size
            self.center_window()  # Center it
            self.is_fullscreen = False
        else:
            # Enter fullscreen - save current state and maximize without title bar
            self.normal_geometry = self.root.geometry()
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            # Set to full screen size without title bar
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.is_fullscreen = True
    
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (640 // 2)
        y = (self.root.winfo_screenheight() // 2) - (480 // 2)
        self.root.geometry(f"640x480+{x}+{y}")
    
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def create_header(self, title, subtitle=""):
        header_frame = tk.Frame(self.main_frame, bg='#000080', height=60)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text=title, bg='#000080', fg='white', 
                              font=('MS Sans Serif', 14, 'bold'))
        title_label.pack(anchor='w', padx=10, pady=(8, 0))
        
        if subtitle:
            subtitle_label = tk.Label(header_frame, text=subtitle, bg='#000080', fg='white', 
                                    font=('MS Sans Serif', 8))
            subtitle_label.pack(anchor='w', padx=10)
    
    def create_buttons(self, buttons_config):
        button_frame = tk.Frame(self.main_frame, bg='#c0c0c0')
        button_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        
        for btn_config in buttons_config:
            btn = tk.Button(button_frame, text=btn_config['text'], 
                           command=btn_config['command'],
                           width=10, height=1,
                           font=('MS Sans Serif', 8))
            btn.pack(side=btn_config.get('side', 'right'), padx=5)
    
    def show_welcome_screen(self):
        self.clear_frame()
        self.create_header("Multiapp 95 Professional Setup", "Welcome to Setup")
        
        content_frame = tk.Frame(self.main_frame, bg='#c0c0c0')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        welcome_text = """Welcome to Multiapp 95 Professional Setup.

This Setup program will configure Multiapp 95 Professional on your computer.

• To continue configuring Multiapp 95 Professional, click Next.
• To learn more about Multiapp 95 Professional before continuing, read the after documentation.
• To quit Setup without configuring Multiapp 95 Professional, click Exit."""
        
        text_label = tk.Label(content_frame, text=welcome_text, bg='#c0c0c0', 
                             font=('MS Sans Serif', 9), justify='left')
        text_label.pack(anchor='w')
        
        # Windows 95 logo simulation
        logo_frame = tk.Frame(content_frame, bg='#c0c0c0', width=200, height=100)
        logo_frame.pack(side='right', anchor='ne', padx=20, pady=20)
        logo_frame.pack_propagate(False)
        
        logo_label = tk.Label(logo_frame, text="Multiapp\n95\nProfessional", bg='#c0c0c0', 
                             font=('Arial', 18, 'bold'), fg='#000080')
        logo_label.pack(expand=True)
        
        self.create_buttons([
            {'text': 'Exit', 'command': self.root.destroy, 'side': 'right'},
            {'text': 'Next >', 'command': self.show_license_agreement, 'side': 'right'}
        ])
    
    def show_license_agreement(self):
        self.clear_frame()
        self.create_header("Multiapp 95 Professional", "Software License Agreement")
        
        content_frame = tk.Frame(self.main_frame, bg='#c0c0c0')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(content_frame, text="Please read the following license agreement carefully:",
                bg='#c0c0c0', font=('MS Sans Serif', 9)).pack(anchor='w', pady=(0, 10))
        
        # Create text widget with scrollbar
        text_frame = tk.Frame(content_frame, bg='#c0c0c0')
        text_frame.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        license_text = tk.Text(text_frame, bg='white', fg='black', 
                              font=('MS Sans Serif', 8),
                              yscrollcommand=scrollbar.set, wrap='word')
        
        license_content = """MULTIAPP 95 PROFESSIONAL SETUP SOFTWARE LICENSE AGREEMENT

IMPORTANT - READ CAREFULLY: This Multiapp 95 Professional Setup End-User License Agreement ("EULA") is a legal agreement between you (either an individual or a single entity) and Retro Computin Division for the Multiapp 95 Professional Setup software product identified above, which includes computer software and may include associated media, printed materials, and "online" or electronic documentation ("SOFTWARE PRODUCT").

By installing, copying, or otherwise using the SOFTWARE PRODUCT, you agree to be bound by the terms of this EULA. If you do not agree to the terms of this EULA, do not install or use the SOFTWARE PRODUCT.

SOFTWARE PRODUCT LICENSE
The SOFTWARE PRODUCT is protected by copyright laws and international copyright treaties, as well as other intellectual property laws and treaties. The SOFTWARE PRODUCT is licensed, not sold.

1. GRANT OF LICENSE. This EULA grants you the following rights:
   • Installation and Use. You may install and use one copy of the SOFTWARE PRODUCT on a single computer.
   • Backup Copy. You may also make one copy of the SOFTWARE PRODUCT for backup or archival purposes.

2. DESCRIPTION OF OTHER RIGHTS AND LIMITATIONS.
   • Limitations on Reverse Engineering, Decompilation, and Disassembly. You may not reverse engineer, decompile, or disassemble the SOFTWARE PRODUCT.
   • Separation of Components. The SOFTWARE PRODUCT is licensed as a single product.
   • Rental. You may not rent, lease, or lend the SOFTWARE PRODUCT.
   • Support Services. Microsoft may provide you with support services related to the SOFTWARE PRODUCT.

3. COPYRIGHT. All title and intellectual property rights in and to the SOFTWARE PRODUCT are owned by Retro Computing Division."""
        
        license_text.insert('1.0', license_content)
        license_text.config(state='disabled')
        license_text.pack(side='left', fill='both', expand=True)
        
        scrollbar.config(command=license_text.yview)
        
        # Agreement checkbox with all buttons
        agreement_frame = tk.Frame(content_frame, bg='#c0c0c0')
        agreement_frame.pack(fill='x', pady=10)
        
        # Left side - checkbox
        left_frame = tk.Frame(agreement_frame, bg='#c0c0c0')
        left_frame.pack(side='left', fill='x', expand=True)
        
        self.agree_var = tk.BooleanVar()
        agree_check = tk.Checkbutton(left_frame, text="I accept the license agreement", 
                                    variable=self.agree_var, bg='#c0c0c0',
                                    font=('MS Sans Serif', 9),
                                    command=self.toggle_next_button)
        agree_check.pack(anchor='w')
        
        # Right side - buttons
        button_frame = tk.Frame(agreement_frame, bg='#c0c0c0')
        button_frame.pack(side='right')
        
        # Create all buttons in the agreement frame
        self.next_button = tk.Button(button_frame, text='Next >', command=self.show_user_info,
                                   width=10, height=1, state='disabled',
                                   font=('MS Sans Serif', 8))
        self.next_button.pack(side='right', padx=2)
        
        tk.Button(button_frame, text='Exit', command=self.root.destroy,
                 width=10, height=1, font=('MS Sans Serif', 8)).pack(side='right', padx=2)
        
        tk.Button(button_frame, text='< Back', command=self.show_welcome_screen,
                 width=10, height=1, font=('MS Sans Serif', 8)).pack(side='right', padx=2)
    
    def toggle_next_button(self):
        if hasattr(self, 'next_button'):
            if self.agree_var.get():
                self.next_button.config(state='normal')
            else:
                self.next_button.config(state='disabled')
    
    def show_user_info(self):
        self.clear_frame()
        self.create_header("Multiapp 95 Professional", "User Information")
        
        content_frame = tk.Frame(self.main_frame, bg='#c0c0c0')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(content_frame, text="Type your name and your company name below:",
                bg='#c0c0c0', font=('MS Sans Serif', 9)).pack(anchor='w', pady=(0, 20))
        
        # Name entry
        name_frame = tk.Frame(content_frame, bg='#c0c0c0')
        name_frame.pack(fill='x', pady=5)
        tk.Label(name_frame, text="Name:", bg='#c0c0c0', 
                font=('MS Sans Serif', 9), width=15).pack(side='left')
        tk.Entry(name_frame, textvariable=self.user_name, 
                font=('MS Sans Serif', 9), width=30).pack(side='left', padx=10)
        
        # Company entry
        company_frame = tk.Frame(content_frame, bg='#c0c0c0')
        company_frame.pack(fill='x', pady=5)
        self.company_name = tk.StringVar(value="")
        tk.Label(company_frame, text="Company:", bg='#c0c0c0', 
                font=('MS Sans Serif', 9), width=15).pack(side='left')
        tk.Entry(company_frame, textvariable=self.company_name, 
                font=('MS Sans Serif', 9), width=30).pack(side='left', padx=10)
        
        self.create_buttons([
            {'text': '< Back', 'command': self.show_license_agreement, 'side': 'right'},
            {'text': 'Next >', 'command': self.validate_and_continue_from_user_info, 'side': 'right'},
            {'text': 'Exit', 'command': self.root.destroy, 'side': 'right'}
        ])
    
    def show_computer_name(self):
        self.clear_frame()
        self.create_header("Multiapp 95 Professional", "Computer Name")
        
        content_frame = tk.Frame(self.main_frame, bg='#c0c0c0')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(content_frame, text="Enter a computer name and workgroup name:",
                bg='#c0c0c0', font=('MS Sans Serif', 9)).pack(anchor='w', pady=(0, 20))
        
        # Computer name
        comp_frame = tk.Frame(content_frame, bg='#c0c0c0')
        comp_frame.pack(fill='x', pady=5)
        tk.Label(comp_frame, text="Computer name:", bg='#c0c0c0', 
                font=('MS Sans Serif', 9), width=15).pack(side='left')
        tk.Entry(comp_frame, textvariable=self.computer_name, 
                font=('MS Sans Serif', 9), width=30).pack(side='left', padx=10)
        
        # Workgroup
        work_frame = tk.Frame(content_frame, bg='#c0c0c0')
        work_frame.pack(fill='x', pady=5)
        tk.Label(work_frame, text="Workgroup:", bg='#c0c0c0', 
                font=('MS Sans Serif', 9), width=15).pack(side='left')
        tk.Entry(work_frame, textvariable=self.workgroup, 
                font=('MS Sans Serif', 9), width=30).pack(side='left', padx=10)
        
        tk.Label(content_frame, text="\nDescription:", bg='#c0c0c0', 
                font=('MS Sans Serif', 9)).pack(anchor='w', pady=(20, 5))
        tk.Text(content_frame, height=3, width=50, font=('MS Sans Serif', 9)).pack(anchor='w')
        
        self.create_buttons([
            {'text': '< Back', 'command': self.show_user_info, 'side': 'right'},
            {'text': 'Next >', 'command': self.validate_and_continue_from_computer_name, 'side': 'right'},
            {'text': 'Exit', 'command': self.root.destroy, 'side': 'right'}
        ])
    
    def show_components(self):
        self.clear_frame()
        self.create_header("Multiapp 95 Professional Setup", "Select Components")
        
        content_frame = tk.Frame(self.main_frame, bg='#c0c0c0')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(content_frame, text="Select the components you want to install:",
                bg='#c0c0c0', font=('MS Sans Serif', 9)).pack(anchor='w', pady=(0, 10))
        
        # Components list
        components_frame = tk.Frame(content_frame, bg='white', relief='sunken', bd=2)
        components_frame.pack(fill='both', expand=True, pady=5)
        
        components = [
            ("Accessories", True, "6.2 MB"),
            ("Communications", True, "3.1 MB"),
            ("Disk Tools", True, "1.8 MB"),
            ("Microsoft Exchange", False, "4.5 MB"),
            ("Microsoft Fax", False, "2.3 MB"),
            ("Multimedia", True, "8.7 MB"),
            ("The Microsoft Network", False, "1.2 MB")
        ]
        
        self.component_vars = {}
        for comp, default, size in components:
            comp_frame = tk.Frame(components_frame, bg='white')
            comp_frame.pack(fill='x', padx=5, pady=2)
            
            var = tk.BooleanVar(value=default)
            self.component_vars[comp] = var
            
            tk.Checkbutton(comp_frame, text=comp, variable=var, bg='white',
                          font=('MS Sans Serif', 8)).pack(side='left')
            tk.Label(comp_frame, text=size, bg='white', fg='blue',
                    font=('MS Sans Serif', 8)).pack(side='right')
        
        # Space info
        space_frame = tk.Frame(content_frame, bg='#c0c0c0')
        space_frame.pack(fill='x', pady=10)
        tk.Label(space_frame, text="Space required: 45.2 MB", bg='#c0c0c0',
                font=('MS Sans Serif', 8)).pack(side='left')
        tk.Label(space_frame, text="Space available: 1.2 GB", bg='#c0c0c0',
                font=('MS Sans Serif', 8)).pack(side='right')
        
        self.create_buttons([
            {'text': '< Back', 'command': self.show_computer_name, 'side': 'right'},
            {'text': 'Next >', 'command': self.show_startup_disk, 'side': 'right'},
            {'text': 'Exit', 'command': self.root.destroy, 'side': 'right'}
        ])
    
    def show_startup_disk(self):
        self.clear_frame()
        self.create_header("Multiapp 95 Professional Setup", "Startup Disk Configuration")
        
        content_frame = tk.Frame(self.main_frame, bg='#c0c0c0')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(content_frame, text="Setup can create a Startup Disk Configuration for you. You should create a Startup Disk or USB\nin case you have problems starting Multiapp 95 Professional from your hard disk.",
                bg='#c0c0c0', font=('MS Sans Serif', 9), justify='left').pack(anchor='w', pady=(0, 20))
        
        self.startup_disk_var = tk.StringVar(value="yes")
        tk.Radiobutton(content_frame, text="Yes, I want a USB Boot Configuration (Recommended)", 
                      variable=self.startup_disk_var, value="yes", bg='#c0c0c0',
                      font=('MS Sans Serif', 9)).pack(anchor='w', pady=5)
        tk.Radiobutton(content_frame, text="No, I do not want a USB Boot Configuration", 
                      variable=self.startup_disk_var, value="no", bg='#c0c0c0',
                      font=('MS Sans Serif', 9)).pack(anchor='w', pady=5)
        
        tk.Label(content_frame, text="\nTo create a Startup Disk Configuration, copy the files from Multiapp directory\non USB or another disk after this Setup was closed.\nThere is a chance that running Multiapp directly from a separate medium, such as a USB stick, may not be feasible.",
                bg='#c0c0c0', font=('MS Sans Serif', 8), fg='#808080').pack(anchor='w', pady=(20, 0))
        
        self.create_buttons([
            {'text': '< Back', 'command': self.show_components, 'side': 'right'},
            {'text': 'Next >', 'command': self.start_copying_files, 'side': 'right'},
            {'text': 'Exit', 'command': self.root.destroy, 'side': 'right'}
        ])
    
    def start_copying_files(self):
        self.clear_frame()
        self.create_header("Multiapp 95 Professional Setup", "Making edits...")
        
        content_frame = tk.Frame(self.main_frame, bg='#c0c0c0')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(content_frame, text="Please wait while Setup makes final edits to your allocated space on disk.",
                bg='#c0c0c0', font=('MS Sans Serif', 9)).pack(anchor='w', pady=(0, 20))
        
        # Progress bar
        progress_frame = tk.Frame(content_frame, bg='#c0c0c0')
        progress_frame.pack(fill='x', pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.pack()
        
        # Current file label
        self.current_file_label = tk.Label(content_frame, text="Configuring: SYSTEM.DAT", 
                                          bg='#c0c0c0', font=('MS Sans Serif', 8))
        self.current_file_label.pack(pady=(10, 0))
        
        # Estimated time
        self.time_label = tk.Label(content_frame, text="Estimated time remaining: 5 seconds", 
                                  bg='#c0c0c0', font=('MS Sans Serif', 8))
        self.time_label.pack(pady=5)
        
        # Start copying simulation
        self.simulate_file_copying()
        
        # Only show exit button during copying
        button_frame = tk.Frame(self.main_frame, bg='#c0c0c0')
        button_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        tk.Button(button_frame, text='Cancel', command=self.root.destroy,
                 width=10, height=1, font=('MS Sans Serif', 8)).pack(side='right', padx=5)
    
    def simulate_file_copying(self):
        files = [
            "SYSTEM.DAT", "USER.DAT", "KERNEL32.DLL", "GDI32.DLL", "USER32.DLL",
            "SHELL32.DLL", "COMCTL32.DLL", "COMDLG32.DLL", "ADVAPI32.DLL", "WINMM.DLL",
            "MSYNC.DLL", "MHASH.DLL", "VERSION.DLL", "SETUPFINAL.DLL", "MCOMLINK.DLL",
            "MTRAY.DLL", "MTASK.DLL", "MDEV.DLL", "MWIN.DLL", "SOL.DLL",
            "MSHEET.DLL", "MSRV.DLL", "ACTIVATOR.DLL", "WRITE.DLL", "TERMINAL.DLL"
        ]
        
        def copy_file(index=0):
            if index < len(files):
                progress = (index + 1) / len(files) * 100
                self.progress_bar['value'] = progress
                
                self.current_file_label.config(text=f"Configuring: {files[index]}")
                
                remaining_time = max(0, (len(files) - index - 1) * 0.2)
                if remaining_time > 1:
                    self.time_label.config(text=f"Estimated time remaining: {int(remaining_time)} seconds")
                else:
                    self.time_label.config(text="Almost finished...")
                
                self.root.after(200, lambda: copy_file(index + 1))
            else:
                self.show_restart_screen()
        
        copy_file()
    
    def show_restart_screen(self):
        self.clear_frame()
        self.create_header("Multiapp 95 Professional Setup", "Setup Complete")
        
        content_frame = tk.Frame(self.main_frame, bg='#c0c0c0')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        success_text = """Congratulations! Multiapp 95 Professional has been successfully configured on your computer.

Setup has finished configuring files and making the necessary configuration to your system.

Click Finish to use Multiapp 95 Professional on your computer."""
        
        tk.Label(content_frame, text=success_text, bg='#c0c0c0', 
                font=('MS Sans Serif', 9), justify='left').pack(expand=True)
        
        # Create finish button
        button_frame = tk.Frame(self.main_frame, bg='#c0c0c0')
        button_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        tk.Button(button_frame, text='Finish', command=self.simulate_restart,
                 width=10, height=1, font=('MS Sans Serif', 8, 'bold')).pack(side='right', padx=5)
    
    def simulate_restart(self):
        self.clear_frame()
        
        # Black screen with restart message
        restart_frame = tk.Frame(self.main_frame, bg='black')
        restart_frame.pack(fill='both', expand=True)
        
        tk.Label(restart_frame, text="Restarting computer...", bg='black', fg='white',
                font=('MS Sans Serif', 12)).pack(expand=True)
        
        # After 2 seconds, show Windows 95 boot screen
        self.root.after(2000, self.show_boot_screen)
    
    def show_boot_screen(self):
        self.clear_frame()
        
        # Windows 95 boot screen
        boot_frame = tk.Frame(self.main_frame, bg='#008080')  # Teal background
        boot_frame.pack(fill='both', expand=True)
        
        # Windows 95 logo
        logo_frame = tk.Frame(boot_frame, bg='#008080')
        logo_frame.pack(expand=True)
        
        tk.Label(logo_frame, text="Multiapp", bg='#008080', fg='white',
                font=('Arial', 24, 'bold')).pack(pady=(50, 0))
        tk.Label(logo_frame, text="95 Professional", bg='#008080', fg='white',
                font=('Arial', 32, 'bold')).pack()
        
        tk.Label(logo_frame, text="Starting Multiapp 95 Professional...", bg='#008080', fg='white',
                font=('MS Sans Serif', 10)).pack(pady=(30, 0))
        
        # After 3 seconds, show welcome message and write completion flag
        self.root.after(3000, self.show_welcome_to_windows)
    
    def show_welcome_to_windows(self):
        self.clear_frame()
        self.create_header("Welcome to Multiapp 95 Professional!", "Setup is now complete")
        
        content_frame = tk.Frame(self.main_frame, bg='#c0c0c0')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        welcome_text = f"""        Welcome to Multiapp 95 Professional, {self.user_name.get()}!

        Your software is now ready to use. This Setup will close as soon as you click Close Setup. Here are some things you can do next:

        Virtual Instance:
        • Click the Start button to run programs or click Shutdown to close Virtual Instance and run Launcher automatically
        • Click the Start button to activate product
        • Click the Start button to check system compatibilities
        • Use the taskbar to switch between programs

        Multiapp 95 Professional has been configured with your settings:
        Computer name: {self.computer_name.get()}
        Workgroup: {self.workgroup.get()}
        Hash: ##/##
        Product ID: 000020250420

        Enjoy using Multiapp 95 Professional!"""
        
        tk.Label(content_frame, text=welcome_text, bg='#c0c0c0', 
                font=('MS Sans Serif', 9), justify='left').pack(expand=True)
        
        self.create_buttons([
            {'text': 'Close Setup', 'command': self.close_and_complete, 'side': 'right'}
        ])
    
    def close_and_complete(self):
        """Close setup and write completion flag"""
        write_completion_flag()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Check database before running installer
    if check_database():
        installer = Windows95Installer()
##############################
        def create_logo(self, parent_frame):
    """Create a 3D retro PC logo similar to Windows 95 style"""
    logo_canvas = tk.Canvas(parent_frame, width=120, height=100, bg='#c0c0c0', 
                           highlightthickness=0)
    logo_canvas.pack(side='right', anchor='ne', padx=(0, 20), pady=10)
    
    # Draw PC case (tower) - 3D effect
    # Main front face
    logo_canvas.create_rectangle(20, 25, 50, 75, fill='#e0e0e0', outline='#808080', width=1)
    # Top face (3D)
    logo_canvas.create_polygon(20, 25, 25, 20, 55, 20, 50, 25, fill='#f0f0f0', outline='#808080')
    # Right face (3D)
    logo_canvas.create_polygon(50, 25, 55, 20, 55, 70, 50, 75, fill='#d0d0d0', outline='#808080')
    
    # Draw floppy drive slot
    logo_canvas.create_rectangle(25, 30, 45, 35, fill='#404040', outline='#202020')
    
    # Draw CD-ROM drive
    logo_canvas.create_rectangle(25, 40, 45, 45, fill='#606060', outline='#404040')
    logo_canvas.create_rectangle(42, 41, 44, 44, fill='#808080', outline='#606060')
    
    # Draw power button
    logo_canvas.create_oval(40, 50, 45, 55, fill='#ff4040', outline='#cc0000')
    
    # Draw some ventilation lines
    for i in range(3):
        y = 60 + i * 3
        logo_canvas.create_line(25, y, 45, y, fill='#a0a0a0', width=1)
    
    # Draw monitor
    # Monitor base/stand
    logo_canvas.create_rectangle(65, 70, 85, 75, fill='#c0c0c0', outline='#808080')
    # Monitor screen (3D)
    logo_canvas.create_rectangle(60, 30, 90, 60, fill='#f0f0f0', outline='#808080', width=1)
    # Top face
    logo_canvas.create_polygon(60, 30, 65, 25, 95, 25, 90, 30, fill='#ffffff', outline='#808080')
    # Right face
    logo_canvas.create_polygon(90, 30, 95, 25, 95, 55, 90, 60, fill='#e0e0e0', outline='#808080')
    
    # Draw screen content (blue desktop)
    logo_canvas.create_rectangle(65, 35, 85, 55, fill='#008080', outline='#008080')
    
    # Draw small window on screen
    logo_canvas.create_rectangle(68, 38, 80, 48, fill='#c0c0c0', outline='#808080')
    logo_canvas.create_rectangle(68, 38, 80, 42, fill='#000080', outline='#000080')
    
    # Draw keyboard (simple 3D)
    logo_canvas.create_rectangle(55, 78, 95, 88, fill='#f0f0f0', outline='#808080')
    logo_canvas.create_polygon(55, 78, 60, 73, 100, 73, 95, 78, fill='#ffffff', outline='#808080')
    logo_canvas.create_polygon(95, 78, 100, 73, 100, 83, 95, 88, fill='#e0e0e0', outline='#808080')
    
    # Draw some keys
    for x in range(4):
        for y in range(2):
            kx = 58 + x * 8
            ky = 80 + y * 3
            logo_canvas.create_rectangle(kx, ky, kx+5, ky+2, fill='#e8e8e8', outline='#c0c0c0')
        installer.run()


În show_welcome_screen() - după content_frame.pack(...):

pythonself.create_logo(content_frame)

În show_user_info() - după content_frame.pack(...):

pythonself.create_logo(content_frame)

În show_computer_name() - după content_frame.pack(...):

pythonself.create_logo(content_frame)

În show_components() - după content_frame.pack(...):

pythonself.create_logo(content_frame)

În show_startup_disk() - după content_frame.pack(...):

pythonself.create_logo(content_frame)

În start_copying_files() - după content_frame.pack(...):

pythonself.create_logo(content_frame)

În show_restart_screen() - după content_frame.pack(...):

pythonself.create_logo(content_frame)

În show_welcome_to_windows() - după content_frame.pack(...):

pythonself.create_logo(content_frame)
3. Adaugă funcția create_logo în clasa Windows95Installer (după center_window()).
