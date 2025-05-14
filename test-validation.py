sqllvar = 22222
if sqllvar == 22222:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    import os
    
    # Definirea folderului și fișierului
    FOLDER_NAME = "Serial"
    FILE_NAME = "product_key.lic95"
    cale_fis = "file_paths.txt"
    cale_fldr = "folder_paths.txt"
    
    # Definirea cheii de validare
    KEY = "R46BX-JHR2J-PG7ER-24QFG-MWKVR"
    
    # Verifică și creează folderul Serial dacă nu există
    if not os.path.exists(FOLDER_NAME):
        try:
            os.makedirs(FOLDER_NAME)
            print(f"Folder '{FOLDER_NAME}' creat cu succes.")
        except Exception as e:
            print(f"Eroare la crearea folderului '{FOLDER_NAME}': {e}")
    
    def validate_key(event=None):
        # Funcția pentru validarea cheii
        global xx
        if text_box.get("1.0", "end-1c").strip() == KEY:
            xx = 2
            validate_button.config(state=tk.NORMAL)
            no_key_button.config(state=tk.DISABLED)
            
            # Calea completă către fișier în folderul Serial
            file_path = os.path.join(FOLDER_NAME, FILE_NAME)
            
            # Salvarea cheii în fișier text în folderul Serial
            with open(file_path, "w") as file:
                file.write(KEY)
            try:
                if not os.path.exists("file_paths.txt"):
                    with open("file_paths.txt", "w") as file:
                        file.write("")
            except Exception as e:
                print(f"An error occurred while creating the file file_paths.txt: {e}")
            try:
                if not os.path.exists("folder_paths.txt"):
                    with open("folder_paths.txt", "w") as file:
                        file.write("")
            except Exception as e:
                print(f"An error occurred while creating the file folder_paths.txt: {e}")
        else:
            xx = 0
            validate_button.config(state=tk.DISABLED)
            no_key_button.config(state=tk.NORMAL)
    
    def load_key():
        try:
            # Calea completă către fișier în folderul Serial
            file_path = os.path.join(FOLDER_NAME, FILE_NAME)
            
            # Încărcarea cheii din fișier text
            with open(file_path, "r") as file:
                key = file.read().strip()
                text_box.delete("1.0", "end")
                text_box.insert("1.0", key)
                validate_key()  # Validarea automată a cheii încărcate
        except FileNotFoundError:
            pass

    def nokey():
        messagebox.showinfo(title="Unlicensed Product", message="Secure connection.\nWelcome to the muap.ro domain!\nFor full access, please contact the administrator (Tudor Marmureanu).")
        sys.exit()

    def valkey():
        messagebox.showinfo(title="Licensed Product (professional version)", message="Secure connection.\nWelcome to the muap.ro domain!")
        validation.destroy()

    def on_closing():
        #pass
        messagebox.showwarning("Warning", "Close the program from the Command Prompt to stop all processes!")

    # Crearea ferestrei principale pentru validare
    validation = tk.Tk()
    validation.protocol("WM_DELETE_WINDOW", on_closing)
    validation.title("Product key validation")
    validation.geometry("260x260")  # Setarea dimensiunilor ferestrei principale
    validation.config(bg="gray20")
    #image_icon80 = PhotoImage(file = "img/keylogo.png")
    #validation.iconphoto(False, image_icon80)

    # Crearea obiectului Text editabil
    text_box = tk.Text(validation, height=1, width=30)  # Setarea wrap="none" pentru a face obiectul Text dreptunghiular
    text_box.config(bd=4)
    text_box.pack(pady=10)
    text_box.bind("<KeyRelease>", validate_key)  # Legarea funcției validate_key() de evenimentul de eliberare a tastelor

    # Crearea butonului "I don't have a product key"
    no_key_button = tk.Button(validation, text="I don't have a product key", bg="black", fg="lime green", bd=5, command=nokey)
    no_key_button.pack(pady=5)

    # Crearea butonului "Validate key"
    validate_button = tk.Button(validation, text="Validate key" ,bg="black", fg="lime green", bd=5, command=valkey, state=tk.DISABLED)
    validate_button.pack(pady=5)

    # Încărcarea cheii la deschiderea programului (dacă există)
    load_key()

    # Rularea buclei principale
    validation.mainloop()