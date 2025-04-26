import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import datetime
import random
import os

# --- Global Variables ---
running = False
send_rate = 1
messages_sent = 0
send_folder = None
hl7_files = []
stop_after_messages = None
stop_after_seconds = None
start_time = None
saved_msh_templates = {}
saved_pid_templates = {}
saved_pv1_templates = {}
selected_patient = None

# --- NHS Test Patients ---
nhs_test_patients = [
    {"name": "TEST^PATIENT", "patient_id": "9876543210", "dob": "19700101", "gender": "M", "address": "1 Test Street^^Testville^London^SE1 2AB", "phone": "02079460000"},
    {"name": "TEST^JOHN", "patient_id": "1234567890", "dob": "19850523", "gender": "M", "address": "2 Example Road^^Sampleton^Manchester^M1 1AA", "phone": "01611234567"},
    {"name": "TEST^EMILY", "patient_id": "1029384756", "dob": "19921212", "gender": "F", "address": "3 Demo Lane^^Mockbury^Bristol^BS1 5AH", "phone": "01179234567"}
]

# --- HL7 Message Generation ---
def generate_hl7(msh_text, pid_text, pv1_text):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return msh_text.replace("{TIMESTAMP}", timestamp) + "\n" + pid_text + "\n" + pv1_text

# --- Send Messages Loop ---
def send_messages():
    global running, messages_sent, start_time
    msh = msh_entry.get("1.0", tk.END).strip()
    pid = pid_entry.get("1.0", tk.END).strip()
    pv1 = pv1_entry.get("1.0", tk.END).strip()

    start_time = time.time()

    while running:
        message = generate_hl7(msh, pid, pv1)
        log_message(message)
        messages_sent += 1
        update_counter()

        if send_folder:
            save_message_to_send_folder(message)

        if stop_after_messages and messages_sent >= stop_after_messages:
            stop_sending()
            break
        if stop_after_seconds and (time.time() - start_time) >= stop_after_seconds:
            stop_sending()
            break

        time.sleep(1 / send_rate)

# --- Save message to send folder ---
def save_message_to_send_folder(message):
    filename = f"hl7_message_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}.hl7"
    filepath = os.path.join(send_folder, filename)
    with open(filepath, "w") as f:
        f.write(message)

# --- Start Sending ---
def start_sending():
    global running, messages_sent
    if not send_folder:
        messagebox.showerror("Error", "Please choose a folder to save generated messages!")
        return
    messages_sent = 0
    running = True
    threading.Thread(target=send_messages).start()

# --- Stop Sending ---
def stop_sending():
    global running
    running = False

# --- Update Sent Counter ---
def update_counter():
    counter_label.config(text=f"Messages Sent: {messages_sent}")

# --- Choose Save Folder ---
def choose_send_folder():
    global send_folder
    send_folder = filedialog.askdirectory()
    if send_folder:
        messagebox.showinfo("Folder Selected", f"Messages will be saved to:\n{send_folder}")

# --- Save Segment Functions ---
def save_current_msh():
    name = simple_prompt("Enter name for MSH Template:")
    if name:
        saved_msh_templates[name] = msh_entry.get("1.0", tk.END).strip()
        msh_var.set(name)
        msh_dropdown['menu'].add_command(label=name, command=tk._setit(msh_var, name))

def save_current_pid():
    name = simple_prompt("Enter name for PID Template:")
    if name:
        saved_pid_templates[name] = pid_entry.get("1.0", tk.END).strip()
        pid_var.set(name)
        pid_dropdown['menu'].add_command(label=name, command=tk._setit(pid_var, name))

def save_current_pv1():
    name = simple_prompt("Enter name for PV1 Template:")
    if name:
        saved_pv1_templates[name] = pv1_entry.get("1.0", tk.END).strip()
        pv1_var.set(name)
        pv1_dropdown['menu'].add_command(label=name, command=tk._setit(pv1_var, name))

# --- Load Segment Functions ---
def load_selected_msh(event=None):
    name = msh_var.get()
    if name in saved_msh_templates:
        msh_entry.delete("1.0", tk.END)
        msh_entry.insert(tk.END, saved_msh_templates[name])

def load_selected_pid(event=None):
    name = pid_var.get()
    if name in saved_pid_templates:
        pid_entry.delete("1.0", tk.END)
        pid_entry.insert(tk.END, saved_pid_templates[name])

def load_selected_pv1(event=None):
    name = pv1_var.get()
    if name in saved_pv1_templates:
        pv1_entry.delete("1.0", tk.END)
        pv1_entry.insert(tk.END, saved_pv1_templates[name])

# --- Apply Stop After Options ---
def apply_stop_setting():
    global stop_after_seconds
    choice = stop_var.get()
    if choice == "Off":
        stop_after_seconds = None
    elif choice == "10 seconds":
        stop_after_seconds = 10
    elif choice == "30 seconds":
        stop_after_seconds = 30
    elif choice == "1 minute":
        stop_after_seconds = 60
    elif choice == "5 minutes":
        stop_after_seconds = 300
    elif choice == "Custom":
        user_value = simple_prompt("Enter custom stop time (seconds):")
        try:
            stop_after_seconds = int(user_value)
        except:
            stop_after_seconds = None

# --- Simple Prompt for Text Entry ---
def simple_prompt(title):
    prompt = tk.Toplevel(root)
    prompt.title(title)
    tk.Label(prompt, text=title).pack()
    entry = tk.Entry(prompt)
    entry.pack()
    result = []

    def on_ok():
        result.append(entry.get())
        prompt.destroy()

    tk.Button(prompt, text="OK", command=on_ok).pack()
    prompt.grab_set()
    prompt.wait_window()
    return result[0] if result else None

# --- Log Message to Console ---
def log_message(message):
    log_text.config(state="normal")
    log_text.insert(tk.END, f"\nSENT:\n{message}\n{'-'*60}\n")
    log_text.see(tk.END)
    log_text.config(state="disabled")

# --- Main GUI Layout ---
root = tk.Tk()
root.title("NERV HL7 Transmission Terminal")
root.configure(bg="#111111")

# Styling
style = ttk.Style()
style.theme_use('clam')
style.configure("TLabelframe", background="#111111", foreground="#FF3333", font=("Arial Black", 12, "bold"))
style.configure("TLabelframe.Label", background="#111111", foreground="#FF3333", font=("Arial Black", 12, "bold"))
style.configure("TLabel", background="#111111", foreground="#FF3333", font=("Arial Black", 10, "bold"))
style.configure("TButton", background="#5D3FD3", foreground="white", font=("Arial Black", 10), padding=5)

# --- Message Setup Frame ---
message_frame = ttk.LabelFrame(root, text="HL7 Message Setup", padding=10)
message_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

msh_var = tk.StringVar()
msh_dropdown = ttk.OptionMenu(message_frame, msh_var, "Select MSH", command=load_selected_msh)
msh_dropdown.grid(row=0, column=0, pady=5, sticky="ew")
ttk.Button(message_frame, text="Save MSH", command=save_current_msh).grid(row=0, column=1, padx=5)

ttk.Label(message_frame, text="MSH Segment:").grid(row=1, column=0, sticky="w")
msh_entry = tk.Text(message_frame, height=3, width=80, bg="#222222", fg="white", insertbackground="white")
msh_entry.grid(row=2, column=0, columnspan=2)

pid_var = tk.StringVar()
pid_dropdown = ttk.OptionMenu(message_frame, pid_var, "Select PID", command=load_selected_pid)
pid_dropdown.grid(row=3, column=0, pady=5, sticky="ew")
ttk.Button(message_frame, text="Save PID", command=save_current_pid).grid(row=3, column=1, padx=5)

ttk.Label(message_frame, text="PID Segment:").grid(row=4, column=0, sticky="w")
pid_entry = tk.Text(message_frame, height=3, width=80, bg="#222222", fg="white", insertbackground="white")
pid_entry.grid(row=5, column=0, columnspan=2)

pv1_var = tk.StringVar()
pv1_dropdown = ttk.OptionMenu(message_frame, pv1_var, "Select PV1", command=load_selected_pv1)
pv1_dropdown.grid(row=6, column=0, pady=5, sticky="ew")
ttk.Button(message_frame, text="Save PV1", command=save_current_pv1).grid(row=6, column=1, padx=5)

ttk.Label(message_frame, text="PV1 Segment:").grid(row=7, column=0, sticky="w")
pv1_entry = tk.Text(message_frame, height=3, width=80, bg="#222222", fg="white", insertbackground="white")
pv1_entry.grid(row=8, column=0, columnspan=2)

# --- Send Control Frame ---
control_frame = ttk.LabelFrame(root, text="Send Controls", padding=10)
control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

ttk.Button(control_frame, text="Start Sending", command=start_sending).grid(row=0, column=0, padx=5, pady=5)
ttk.Button(control_frame, text="Stop Sending", command=stop_sending).grid(row=0, column=1, padx=5, pady=5)
ttk.Button(control_frame, text="Choose Send Folder", command=choose_send_folder).grid(row=0, column=2, padx=5, pady=5)

ttk.Label(control_frame, text="Messages per Second:").grid(row=1, column=0, sticky="w")
rate_slider = ttk.Scale(control_frame, from_=0.1, to=10, value=1, orient="horizontal", command=lambda v: rate_value_label.config(text=f"{float(v):.1f} msg/sec"))
rate_slider.grid(row=2, column=0, columnspan=3, sticky="ew")
rate_value_label = ttk.Label(control_frame, text="1.0 msg/sec")
rate_value_label.grid(row=1, column=1, sticky="e")

stop_options = ["Off", "10 seconds", "30 seconds", "1 minute", "5 minutes", "Custom"]
stop_var = tk.StringVar()
stop_dropdown = ttk.OptionMenu(control_frame, stop_var, "Stop After", *stop_options)
stop_dropdown.grid(row=3, column=0, pady=5)

apply_button = ttk.Button(control_frame, text="Apply Stop Setting", command=apply_stop_setting)
apply_button.grid(row=3, column=1, padx=5)

counter_label = ttk.Label(control_frame, text="Messages Sent: 0")
counter_label.grid(row=4, column=0, columnspan=2, pady=5)

# --- Transmission Log Frame ---
log_frame = ttk.LabelFrame(root, text="Transmission Log", padding=10)
log_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

log_text = tk.Text(log_frame, height=15, width=90, bg="#111111", fg="white", insertbackground="white", wrap="word", state="disabled")
log_text.pack()

# --- Default Template Texts ---
msh_entry.insert(tk.END, "MSH|^~\\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|{TIMESTAMP}||ADT^A01|MSGID|P|2.3")
pid_entry.insert(tk.END, "PID|||9876543210||TEST^PATIENT||19700101|M|||1 Test Street^^Testville^London^SE1 2AB||02079460000")
pv1_entry.insert(tk.END, "PV1||I|W^389^1^A^^^||||1234^PrimaryDoctor^Joe||||||||||5678")

# --- Start Main Loop ---
root.mainloop()
