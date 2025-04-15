import os
import re
from tkinter import Tk, Label, Entry, Button, Checkbutton, filedialog, Listbox, END, messagebox, StringVar, IntVar, Scrollbar, Frame
import tkinter.font as tkFont


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


class FileRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AC File Number Re-Namer")
        self.root.config(bg="#1e1e1e")
        self.root.geometry("850x500")
        self.root.resizable(False, False)

        label_font = tkFont.Font(family="Segoe UI", size=10, weight="bold")
        entry_font = tkFont.Font(family="Segoe UI", size=10)

        self.folder_path = StringVar()
        self.start_counter = IntVar()
        self.fixed_numbering = IntVar(value=0)

        input_frame = Frame(root, bg="#1e1e1e", highlightbackground="#3a3a3a", highlightthickness=1)
        input_frame.grid(row=0, column=0, pady=10, padx=10, sticky="w")

        Label(input_frame, text="Ordner Pfad:", font=label_font, bg="#1e1e1e", fg="#ffffff").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        folder_entry = Entry(input_frame, textvariable=self.folder_path, width=40, font=entry_font, bg="#2d2d2d", fg="#ffffff", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#3a3a3a")
        folder_entry.grid(row=0, column=1, padx=5, pady=5)
        folder_entry.bind("<KeyRelease>", lambda e: self.preview_renaming())
        Button(input_frame, text="Durchsuchen", command=self.browse_folder, bg="#007acc", fg="white", font=entry_font, relief="flat", activebackground="#005f99", activeforeground="white").grid(row=0, column=2, padx=5, pady=5)

        Label(input_frame, text="Startnummer:", font=label_font, bg="#1e1e1e", fg="#ffffff").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        start_entry = Entry(input_frame, textvariable=self.start_counter, font=entry_font, bg="#2d2d2d", fg="#ffffff", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#3a3a3a")
        start_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        start_entry.bind("<KeyRelease>", lambda e: self.preview_renaming())

        fixed_cb = Checkbutton(input_frame, text="Feste Nummer verwenden", variable=self.fixed_numbering, font=entry_font, bg="#1e1e1e", fg="#ffffff", selectcolor="#2d2d2d", activebackground="#1e1e1e", activeforeground="#ffffff", command=self.preview_renaming)
        fixed_cb.grid(row=1, column=2, sticky='w', padx=5, pady=5)

        Button(input_frame, text="Dateien umbenennen", command=self.rename_files, bg="#28a745", fg="white", font=entry_font, relief="flat", activebackground="#218838", activeforeground="white").grid(row=2, column=2, pady=10)

        preview_frame = Frame(root, bg="#1e1e1e", highlightbackground="#3a3a3a", highlightthickness=1)
        preview_frame.grid(row=1, column=0, padx=10, pady=(0, 10))

        Label(preview_frame, text="Originaler Name", font=label_font, bg="#1e1e1e", fg="#ffffff", anchor="w").grid(row=0, column=0, sticky="w", padx=5)
        Label(preview_frame, text="Neuer Name", font=label_font, bg="#1e1e1e", fg="#ffffff", anchor="w").grid(row=0, column=1, sticky="w", padx=5)

        self.listbox_original = Listbox(preview_frame, width=50, height=15, font=entry_font, bg="#2d2d2d", fg="#ffffff", selectbackground="#007acc", relief="flat", highlightthickness=1, highlightbackground="#3a3a3a")
        self.listbox_new = Listbox(preview_frame, width=50, height=15, font=entry_font, bg="#2d2d2d", fg="#ffffff", selectbackground="#007acc", relief="flat", highlightthickness=1, highlightbackground="#3a3a3a")

        self.listbox_original.grid(row=1, column=0, sticky="nsew", padx=5)
        self.listbox_new.grid(row=1, column=1, sticky="nsew", padx=5)

        scrollbar = Scrollbar(preview_frame)
        scrollbar.grid(row=1, column=2, sticky="ns")
        self.listbox_original.config(yscrollcommand=scrollbar.set)
        self.listbox_new.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.sync_scroll)

        self.listbox_original.bind("<MouseWheel>", self.on_mousewheel)
        self.listbox_new.bind("<MouseWheel>", self.on_mousewheel)

    def sync_scroll(self, *args):
        self.listbox_original.yview(*args)
        self.listbox_new.yview(*args)

    def on_mousewheel(self, event):
        self.listbox_original.yview("scroll", int(-1 * (event.delta / 120)), "units")
        self.listbox_new.yview("scroll", int(-1 * (event.delta / 120)), "units")
        return "break"

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.preview_renaming()

    def preview_renaming(self):
        self.listbox_original.delete(0, END)
        self.listbox_new.delete(0, END)

        folder_path = self.folder_path.get()
        counter = self.start_counter.get()
        fixed_numbering = self.fixed_numbering.get()

        if not os.path.isdir(folder_path):
            return

        files = sorted(
            (entry.name for entry in os.scandir(folder_path) if entry.is_file()),
            key=natural_sort_key
        )

        for file_name in files:
            try:
                match = re.match(r"^(\d+)(_-_)(.*)$", file_name)
                if match:
                    new_name = f"{counter}_-_" + match.group(3)
                else:
                    new_name = f"{counter}_-_" + file_name

                self.listbox_original.insert(END, file_name)
                self.listbox_new.insert(END, new_name)

                if not fixed_numbering:
                    counter += 1
            except Exception as e:
                messagebox.showerror("Fehler", f"Konnte Vorschau für {file_name} nicht anzeigen: {e}")

    def rename_files(self):
        folder_path = self.folder_path.get()
        counter = self.start_counter.get()
        fixed_numbering = self.fixed_numbering.get()

        if not os.path.isdir(folder_path):
            messagebox.showerror("Fehler", "Ungültiger Ordnerpfad")
            return

        files = sorted(
            (entry.name for entry in os.scandir(folder_path) if entry.is_file()),
            key=natural_sort_key
        )

        if not files:
            messagebox.showinfo("Keine Dateien", "Keine Dateien im ausgewählten Ordner gefunden.")
            return

        if not messagebox.askyesno("Bestätigung", "Sind Sie sicher, dass Sie die Dateien umbenennen möchten?"):
            return

        for file_name in files:
            try:
                old_path = os.path.join(folder_path, file_name)
                match = re.match(r"^(\d+)(_-_)(.*)$", file_name)
                if match:
                    new_name = f"{counter}_-_" + match.group(3)
                else:
                    new_name = f"{counter}_-_" + file_name

                new_path = os.path.join(folder_path, new_name)
                os.rename(old_path, new_path)

                if not fixed_numbering:
                    counter += 1
            except Exception as e:
                messagebox.showerror("Fehler", f"Konnte {file_name} nicht umbenennen: {e}")
                break

        messagebox.showinfo("Fertig", "Dateien wurden erfolgreich umbenannt.")
        self.preview_renaming()


if __name__ == "__main__":
    root = Tk()
    app = FileRenamerGUI(root)
    root.mainloop()  