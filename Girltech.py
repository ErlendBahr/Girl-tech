import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import hashlib
import os
from PIL import Image, ImageTk

PIN_FILE = 'pin_hash.txt'
DEFAULT_PIN = '1234'

# --- Hjelpefunksjoner ---
def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def load_pin_hash():
    if not os.path.exists(PIN_FILE):
        save_pin_hash(DEFAULT_PIN)
    with open(PIN_FILE, 'r') as f:
        return f.read().strip()

def save_pin_hash(pin):
    with open(PIN_FILE, 'w') as f:
        f.write(hash_pin(pin))

# --- Adminvindu ---
class AdminVindu(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title('Administratorinnstillinger')
        self.geometry('320x140')  # Lite popup
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.attributes('-topmost', True)
        self.focus()
        self.label = tk.Label(self, text='Endre PIN-kode:', font=('TkDefaultFont', 14))
        self.label.pack(pady=(20, 5))
        self.pin_entry = tk.Entry(self, show='*', font=('TkDefaultFont', 14))
        self.pin_entry.pack(pady=(10, 20))
        self.pin_entry.focus_set()
        # Enter-knapp ramme for sentrering
        btn_frame = tk.Frame(self)
        btn_frame.pack()
        self.save_btn = ttk.Button(btn_frame, text='Enter', command=self.lagre_pin)
        self.save_btn.pack(ipadx=20, ipady=8)
        self.pin_entry.bind('<Return>', lambda event: self.lagre_pin())

    def lagre_pin(self):
        ny_pin = self.pin_entry.get()
        if not ny_pin.isdigit() or len(ny_pin) < 4:
            messagebox.showerror('Feil', 'PIN-koden må være minst 4 sifre.')
            return
        save_pin_hash(ny_pin)
        messagebox.showinfo('Lagret', 'PIN-koden er oppdatert!')
        self.destroy()

# --- Hovedvindu ---
class CoursurApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Coursur - Velkommen')
        try:
            self.attributes('-fullscreen', True)
        except Exception:
            self.geometry('900x600')
        self.resizable(False, False)
        self.pin_hash = load_pin_hash()
        self.lag_widgets()

    def lag_widgets(self):
        # Header removed as requested

        # Add image below header (Laerdal.png in current directory)
        import os
        image_path = 'Laerdal.png'
        if os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                image = image.resize((500, 267))
                self.photo = ImageTk.PhotoImage(image)
                self.image_label = tk.Label(self, image=self.photo)
                self.image_label.pack(pady=10)
            except Exception as e:
                print('Kunne ikke laste bilde:', e)
        else:
            print('Fant ikke bilde: Laerdal.png')
        # Tannhjul øverst til høyre
        self.gear_btn = tk.Button(self, text='⚙️', font=('TkDefaultFont', 16), command=self.aapne_admin, borderwidth=0)
        self.gear_btn.place(relx=0.97, rely=0.03, anchor='ne', width=30, height=30)
        # Midttekst
        self.mid_label = tk.Label(self, text='Tast inn PIN-kode', font=('TkDefaultFont', 32))
        self.mid_label.pack(pady=10)

        # Viser inntastet PIN
        self.pin_display = tk.Label(self, text='', font=('TkDefaultFont', 36, 'bold'))
        self.pin_display.pack(pady=10)

        # Fire bokser for PIN
        self.pin_vars = [tk.StringVar() for _ in range(4)]
        self.pin_entries = []
        entry_frame = tk.Frame(self)
        entry_frame.pack(pady=10)
        for i in range(4):
            entry = tk.Entry(entry_frame, textvariable=self.pin_vars[i], font=('TkDefaultFont', 36), width=2, justify='center', show='*')
            entry.grid(row=0, column=i, padx=10)
            entry.bind('<KeyRelease>', self._make_pin_entry_callback(i))
            self.pin_entries.append(entry)
        self.pin_entries[0].focus_set()

        # Enter- og Clear-knapper i felles ramme
        button_frame = tk.Frame(self)
        button_frame.pack(pady=30)
        self.enter_btn = ttk.Button(button_frame, text='Enter', command=self.sjekk_pin)
        self.enter_btn.grid(row=0, column=0, padx=20, ipadx=20, ipady=10)
        self.clear_btn = ttk.Button(button_frame, text='Clear', command=self.clear_pin)
        self.clear_btn.grid(row=0, column=1, padx=20, ipadx=20, ipady=10)

        # Feilmelding
        self.error_label = tk.Label(self, text='', fg='red', font=('TkDefaultFont', 20))
        self.error_label.pack()

    def _make_pin_entry_callback(self, idx):
        return lambda event: self.on_pin_entry(event, idx)

    def on_pin_entry(self, event, idx):
        # Tillat kun ett siffer per boks
        value = self.pin_vars[idx].get()
        if len(value) > 1:
            self.pin_vars[idx].set(value[-1])
        elif value and not value[-1].isdigit():
            self.pin_vars[idx].set('')
        # Flytt fokus til neste boks automatisk
        if self.pin_vars[idx].get() and idx < 3:
            self.pin_entries[idx+1].focus_set()
        # Oppdater visning
        self.update_pin_display()
        # Enter på siste boks
        if idx == 3 and event.keysym == 'Return':
            self.sjekk_pin()

    def update_pin_display(self):
        pin = ''.join(var.get() for var in self.pin_vars)
        self.pin_display.config(text=pin)

    def hent_pin(self):
        return ''.join(var.get() for var in self.pin_vars)

    def sjekk_pin(self):
        pin = self.hent_pin()
        if len(pin) < 4:
            self.error_label.config(text='Vennligst tast inn 4 sifre.')
            return
        if hash_pin(pin) == load_pin_hash():
            self.error_label.config(text='')
            self.withdraw()
            dash = DashboardVindu(self)
            dash.grab_set()
            for var in self.pin_vars:
                var.set('')
            self.update_pin_display()
            self.pin_entries[0].focus_set()
        else:
            self.error_label.config(text='Feil PIN-kode. Prøv igjen.')
            for var in self.pin_vars:
                var.set('')
            self.update_pin_display()
            self.pin_entries[0].focus_set()

    def clear_pin(self):
        for var in self.pin_vars:
            var.set('')
        self.update_pin_display()
        self.pin_entries[0].focus_set()

    def aapne_admin(self):
        # Spør etter adminpassord først
        passord = simpledialog.askstring('Administrator', 'Skriv inn administratorpassord:', show='*', parent=self)
        if passord is None:
            return  # Avbrutt
        if passord == 'Laerdal':
            AdminVindu(self)
        else:
            messagebox.showerror('Feil', 'Feil administratorpassord.')

class DashboardVindu(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title('Coursur - Dashboard')
        self.geometry('600x400')
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.lukk_dashboard)
        self.master = master
        self.lag_widgets()

    def lag_widgets(self):
        header = tk.Label(self, text='Dashboard', font=('TkDefaultFont', 32, 'bold'))
        header.pack(pady=30)
        # Large, cartoony buttons
        btn1 = tk.Button(self, text='❤️  Puls', command=self.vis_info,
                        font=('TkDefaultFont', 32, 'bold'), bg='#FFB300', fg='#000',
                        activebackground='#FFA000', activeforeground='#000',
                        relief='raised', bd=6, height=2, width=18, cursor='hand2')
        btn1.pack(pady=15)
        btn2 = tk.Button(self, text='🎨  Farge', command=self.vis_advarsel,
                        font=('TkDefaultFont', 32, 'bold'), bg='#FF1744', fg='#000',
                        activebackground='#D50000', activeforeground='#000',
                        relief='raised', bd=6, height=2, width=18, cursor='hand2')
        btn2.pack(pady=15)
        btn3 = tk.Button(self, text='💨  Pust', command=self.vis_om,
                        font=('TkDefaultFont', 32, 'bold'), bg='#00BFAE', fg='#000',
                        activebackground='#00897B', activeforeground='#000',
                        relief='raised', bd=6, height=2, width=18, cursor='hand2')
        btn3.pack(pady=15)
        # Logg ut-knapp
        logout_btn = ttk.Button(self, text='Logg ut', command=self.lukk_dashboard)
        logout_btn.pack(pady=30, ipadx=30, ipady=10)

    def vis_info(self):
        messagebox.showinfo('Informasjon', 'Dette er en informasjonsdialog fra dashbordet.')

    def vis_advarsel(self):
        messagebox.showwarning('Advarsel', 'Dette er en advarsel!')

    def vis_om(self):
        messagebox.showinfo('Om', 'Coursur v1.0\nLaget med tkinter.')

    def lukk_dashboard(self):
        self.master.deiconify()
        self.destroy()

if __name__ == '__main__':
    print('Script started')
    app = CoursurApp()
    app.mainloop()
