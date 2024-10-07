import os
import shutil
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter import ttk
from ttkthemes import ThemedStyle
import threading

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class FolderMonitorGUI:
    def __init__(self, master):
        self.master = master
        master.title("BO3 Custom Map Fixer")
        master.geometry("500x300")
        master.resizable(False, False)  # Make window not resizable
        icon_path = get_resource_path("icon.png")
        icon_image = Image.open(icon_path)
        icon_image_resized = icon_image.resize((32, 32), Image.ANTIALIAS)
        icon_photo = ImageTk.PhotoImage(icon_image_resized)

        # Set window icon
        master.iconphoto(True, icon_photo)
        bg_image_path = get_resource_path("background.png")
        original_image = Image.open(bg_image_path)
        resized_image = original_image.resize((500, 300), Image.ANTIALIAS)
        self.bg_image = ImageTk.PhotoImage(resized_image)

        bg_label = tk.Label(master, image=self.bg_image)
        bg_label.place(relwidth=1, relheight=1)

        self.label_text = 'Enter the path to folder "311210" in your Steam libraries:'
        self.label = tk.Label(master, text=self.label_text)
        self.label_width = len(self.label_text) * 5.25  # Adjust factor as needed
        self.label_x = (500 - self.label_width) // 2
        self.label.place(x=self.label_x, y=140)

        self.entry_width = 45
        self.entry_x = (500 - (self.entry_width * 7.45)) // 2  # Calculate x position to center the entry field
        self.folder_path_entry = tk.Entry(master, width=self.entry_width)
        self.folder_path_entry.place(x=self.entry_x, y=180)  # Place the entry field at the calculated x position



        self.region_var = tk.StringVar(master)
        self.region_var.set("Region")  # Default value
        self.regions = {"Region": "", "English": "en", "English Arabic": "ea", "French": "fr", "German": "ge", "Italian": "it", "Japanese": "ja", "Polish": "po", "Portuguese": "bp", "Russian": "ru", "Simplified Chinese": "sc", "Spanish": "es", "Traditional Chinese": "tc"}
        self.region_menu = tk.OptionMenu(master, self.region_var, *self.regions)
        self.region_menu.place(x=self.entry_x + self.entry_width*6.5, y=172.5)  # Place the dropdown menu next to the entry field

        style = ThemedStyle(master)
        style.set_theme("arc")
        style.configure('TMenubutton', foreground='black', background='white', padding=5, relief='flat')  # Customize the appearance of the dropdown button
        style.configure('TMenubutton', arrowcolor='black')  # Customize the color of the dropdown arrow
        style.map('TMenubutton', background=[('active', 'white')])  # Customize the background color when active

        # Use the custom style for the dropdown menu
        self.region_menu = ttk.OptionMenu(master, self.region_var, *self.regions.keys())
        self.region_menu.place(x=self.entry_x + self.entry_width*6.5, y=172.5)  # Place the dropdown menu next to the entry field

        
        self.button_width = len("Fix Custom Maps") + 4  
        self.button_x = (500 - (self.button_width * 8)) // 2  
        self.monitor_button = tk.Button(master, text="Fix Custom Maps", command=self.monitor_folder, bg="white", fg="black", width=self.button_width)
        self.monitor_button.place(x=(self.button_x)+2, y=225) 

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width // 2) - (500 // 2)  # Calculate x position
        y = (screen_height // 2) - (300 // 2)  # Calculate y position
        master.geometry(f"500x300+{x}+{y}")

    def start_monitoring(self):
        threading.Thread(target=self.monitor_folder).start()

    def monitor_folder(self):
        folder_path = self.folder_path_entry.get().strip()
        region = self.region_var.get()
        if not os.path.isdir(folder_path):
            messagebox.showerror("Error", "Invalid folder path: {}".format(folder_path))
            return


        file_region = self.regions.get(region, "")  # Get the file region based on the selected region
        if not file_region:
            messagebox.showerror("Error", "Please select a valid region.")
            return

        self.monitor_button.config(state=tk.DISABLED)
        try:
            self.process_folder(folder_path, file_region)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.monitor_button.config(state=tk.NORMAL)

    def process_folder(self, folder_path, file_region):
        # Assuming the structure: main_folder -> sub_folder -> deeper_folder
        if not file_region:
            messagebox.showerror("Error", "Please select a valid region.")
            return
        print("Processing folder:", folder_path)

        # Iterate over all subdirectories of folder_path
        for subdir in os.listdir(folder_path):
            subfolder_path = os.path.join(folder_path, subdir)
            print("Subfolder:", subfolder_path)

            # Create "ea" folder inside "snd" folder for each subdirectory
            snd_path = os.path.join(subfolder_path, "snd")
            if os.path.exists(snd_path):
                ea_path = os.path.join(snd_path, file_region)
                os.makedirs(ea_path, exist_ok=True)
                print("Created " + file_region + " folder:", ea_path)

                # Traverse through "all" or "en" folder and copy files
                for language_folder in ["en", "all"]:
                    language_path = os.path.join(snd_path, language_folder)
                    if os.path.exists(language_path):
                        for root, dirs, files in os.walk(language_path):
                            for file in files:
                                if file.endswith(".sabl") or file.endswith(".sabs"):
                                    new_filename = file.replace(".all.", "."+file_region+".") if language_folder == "all" else file.replace(".en.", "."+file_region+".")
                                    source_file = os.path.join(root, file)
                                    dest_file = os.path.join(ea_path, new_filename)
                                    if not os.path.exists(dest_file):
                                        shutil.copyfile(source_file, dest_file)
                                        print("Copied file:", source_file, "->", dest_file)
                                    else:
                                        print("File already exists, skipping:", source_file)

            for file in os.listdir(subfolder_path):
                if file.startswith("en_zm_") and (file.endswith(".xpak") or file.endswith(".ff")):
                    new_filename = file.replace("en_", file_region+"_")
                    source_file = os.path.join(subfolder_path, file)
                    dest_file = os.path.join(subfolder_path, new_filename)
                    if not os.path.exists(dest_file):
                        shutil.copyfile(source_file, dest_file)
                        print("Copied and renamed file:", source_file, "->", dest_file)
                    else:
                        print("File already exists, skipping:", source_file)
                elif file.startswith("zm_") and (file.endswith(".xpak") or file.endswith(".ff")):
                    new_filename = file_region+"_"+ file
                    source_file = os.path.join(subfolder_path, file)
                    dest_file = os.path.join(subfolder_path, new_filename)
                    if not os.path.exists(dest_file):
                        shutil.copyfile(source_file, dest_file)
                        print("Copied and renamed file:", source_file, "->", dest_file)
                    else:
                        print("File already exists, skipping:", source_file)
        messagebox.showinfo("Success", "Region fix completed successfully.")
                  
def main():
    root = tk.Tk()
    gui = FolderMonitorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

