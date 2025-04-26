import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import datetime
import random
import os

# Global variables
running = False
send_rate = 1  # Messages per second
messages_sent = 0  # Counter
save_directory = None  # Folder to save sent messages
hl7_files = []  # List of HL7 file paths
stop_after_messages = None  # Number of messages to stop after
stop_after_seconds = None  # Seconds to stop after
start_time = None

# Official NHS Test Patients
nhs_test_patients = [
    {
        "patient_id": "9876543210",
        "last_name": "TEST",
        "first_name": "PATIENT",
        "dob": "19700101",
        "gender": "M",
        "address": "1 Test Street^^Testville^London^SE1 2AB",
        "phone": "02079460000"
    },
    {
        "patient_id": "1234567890",
        "last_name": "TEST",
        "first_name": "JOHN",
        "dob": "19850523",
        "gender": "M",
        "address": "2 Example Road^^Sampleton^Manchester^M1 1AA",
        "phone": "01611234567"
    },
    {
        "patient_id": "1029384756",
        "last_name": "TEST",
        "first_name": "EMILY",
        "dob": "19921212",
        "gender": "F",
        "address": "3 Demo Lane^^Mockbury^Bristol^BS1 5AH",
        "phone": "01179234567"
    }
]

# Generate HL7 Message
def generate_hl7(msh_text, pid_text, pv1_text):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    message = msh_text.replace("{TIMESTAMP}", timestamp) + "\n" + pid_text + "\n" + pv1_text
    return message

# Sending messages loop
def send_messages():
    global running, messages_sent, start_time

    if not hl7_files:
        # Manual message from screen
        msh = msh_entry.get("1.0", tk.END).strip()
        pid = pid_entry.get("1.0", tk.END).strip()
        pv1 = pv1_entry.get("1.0", tk.END).strip()

    start_time = time.time()

    while running:
        if hl7_files:
            filepath = random.choice(hl7_files)
            try:
                with open(filepath, "r") as f:
                    message = f.read()
            except Exception as e:
                log_message(f"Error reading {filepath}: {str(e)}")
                continue
        else:
            message = generate_hl7(msh, pid, pv1)

        log_message(message)
        messages_sent += 1
        update_counter()

        if save_directory:
            save_message_to_folder(message)

        # Check stop conditions
        if stop_after_messages and messages_sent >= stop_after_messages:
            stop_sending()
            break

        if stop_after_seconds and (time.time() - start_time) >= stop_after_seconds:
            stop_sending()
            break

        time.sleep(1 / send_rate)

# Start sending
def start_sending():
    global running, messages_sent
    messages_sent = 0
    running = True
    thread = threading.Thread(target=send_messages)
    thread.start()

# Stop sending
def stop_sending():
    global running
    running = False

# Update send rate
def update_rate(val):
    global send_rate
    send_rate = float(val)
    rate_value_label.config(text=f"{send_rate:.1f} msg/sec")

# Update counter display
def update_counter():
    counter_label.config(text=f"Messages Sent: {messages_sent}")

# Reset counter
def reset_counter():
    global messages_sent
    messages_sent = 0
    update_counter()

# Log message to the GUI
def log_message(message):
    log_text.config(state="normal")
    log_text.insert(tk.END, f"\nSENT:\n{message}\n{'-'*60}\n")
    log_text.see(tk.END)
    log_text.config(state="disabled")

# Upload one or more HL7 files
def upload_hl7_files():
    global hl7_files
    files = filedialog.askopenfilenames(filetypes=[("HL7 files", "*.hl7"), ("Text files", "*.txt"), ("All files", "*.*")])
    hl7_files = list(files)
    if hl7_files:
        messagebox.showinfo("Loaded", f"{len(hl7_files)} HL7 file(s) loaded for batch sending.")

# Insert NHS Test Patient
def insert_test_patient():
    patient = random.choice(nhs_test_patients)
    pid_entry.delete("1.0", tk.END)
    pid_entry.insert(tk.END, f"PID|||{patient['patient_id']}||{patient['last_name']}^{patient['first_name']}||{patient['dob']}|{patient['gender']}|||{patient['address']}||{patient['phone']}")

# Save current message to a file manually
def save_current_message():
    message = generate_hl7(msh_entry.get("1.0", tk.END).strip(),
                           pid_entry.get("1.0", tk.END).strip(),
                           pv1_entry.get("1.0", tk.END).strip())

    filepath = filedialog.asksaveasfilename(defaultextension=".hl7", filetypes=[("HL7 files", "*.hl7"), ("All files", "*.*")])
    if filepath:
        try:
            with open(filepath, "w") as f:
                f.write(message)
            messagebox.showinfo("Success", "Message saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

# Choose folder to auto-save sent messages
def choose_save_directory():
    global save_directory
    save_directory = filedialog.askdirectory()
    if save_directory:
        messagebox.showinfo("Save Directory Set", f"Messages will be saved to:\n{save_directory}")

# Save individual message to folder automatically
def save_message_to_folder(message):
    filename = f"hl7_message_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}.hl7"
    filepath = os.path.join(save_directory, filename)
    try:
        with open(filepath, "w") as f:
            f.write(message)
    except Exception as e:
        print(f"Error saving message to folder: {str(e)}")

# Set how many messages to stop after
def set_stop_after_messages():
    global stop_after_messages
    try:
        stop_after_messages = int(stop_messages_entry.get())
        messagebox.showinfo("Set", f"Will stop after {stop_after_messages} messages.")
    except:
        messagebox.showerror("Error", "Please enter a valid number.")

# Set how many seconds to stop after
def set_stop_after_seconds():
    global stop_after_seconds
    try:
        stop_after_seconds = int(stop_seconds_entry.get())
        messagebox.showinfo("Set", f"Will stop after {stop_after_seconds} seconds.")
    except:
        messagebox.showerror("Error", "Please enter a valid number.")

# Create GUI
root = tk.Tk()
root.title("HL7 NHS Test Patient Sender")

# Frame for HL7 sections
section_frame = ttk.LabelFrame(root, text="HL7 Sections", padding=10)
section_frame.grid(row=0, column=0, padx=10, pady=10)

ttk.Label(section_frame, text="MSH Segment:").grid(row=0, column=0, sticky="w")
msh_entry = tk.Text(section_frame, height=3, width=80)
msh_entry.grid(row=1, column=0)

ttk.Label(section_frame, text="PID Segment:").grid(row=2, column=0, sticky="w")
pid_entry = tk.Text(section_frame, height=3, width=80)
pid_entry.grid(row=3, column=0)

ttk.Label(section_frame, text="PV1 Segment:").grid(row=4, column=0, sticky="w")
pv1_entry = tk.Text(section_frame, height=3, width=80)
pv1_entry.grid(row=5, column=0)

upload_button = ttk.Button(section_frame, text="Upload HL7 File(s)", command=upload_hl7_files)
upload_button.grid(row=6, column=0, pady=5)

test_patient_button = ttk.Button(section_frame, text="Insert NHS Test Patient", command=insert_test_patient)
test_patient_button.grid(row=7, column=0, pady=5)

save_current_button = ttk.Button(section_frame, text="Save Current Message", command=save_current_message)
save_current_button.grid(row=8, column=0, pady=5)

choose_dir_button = ttk.Button(section_frame, text="Set Folder for Auto-Save", command=choose_save_directory)
choose_dir_button.grid(row=9, column=0, pady=5)

# Frame for controls
control_frame = ttk.LabelFrame(root, text="Controls", padding=10)
control_frame.grid(row=1, column=0, padx=10, pady=10)

start_button = ttk.Button(control_frame, text="Start Sending", command=start_sending)
start_button.grid(row=0, column=0, padx=5, pady=5)

stop_button = ttk.Button(control_frame, text="Stop Sending", command=stop_sending)
stop_button.grid(row=0, column=1, padx=5, pady=5)

rate_label = ttk.Label(control_frame, text="Messages per Second:")
rate_label.grid(row=1, column=0, sticky="w", pady=(10,0))

rate_value_label = ttk.Label(control_frame, text="1.0 msg/sec")
rate_value_label.grid(row=1, column=1, sticky="e", pady=(10,0))

rate_slider = ttk.Scale(control_frame, from_=0.1, to=10, value=1, orient="horizontal", command=update_rate)
rate_slider.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)

counter_label = ttk.Label(control_frame, text="Messages Sent: 0")
counter_label.grid(row=3, column=0, columnspan=2, pady=(10,0))

reset_button = ttk.Button(control_frame, text="Reset Counter", command=reset_counter)
reset_button.grid(row=4, column=0, columnspan=2, pady=5)

# Stop after messages
stop_messages_entry = ttk.Entry(control_frame)
stop_messages_entry.grid(row=5, column=0)
ttk.Button(control_frame, text="Set Stop After Messages", command=set_stop_after_messages).grid(row=5, column=1)

# Stop after seconds
stop_seconds_entry = ttk.Entry(control_frame)
stop_seconds_entry.grid(row=6, column=0)
ttk.Button(control_frame, text="Set Stop After Seconds", command=set_stop_after_seconds).grid(row=6, column=1)

# Frame for log
log_frame = ttk.LabelFrame(root, text="Sent Message Log", padding=10)
log_frame.grid(row=2, column=0, padx=10, pady=10)

log_text = tk.Text(log_frame, height=15, width=90, state="disabled", wrap="word")
log_text.pack()

# Default templates
msh_entry.insert(tk.END, "MSH|^~\\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|{TIMESTAMP}||ADT^A01|MSGID|P|2.3")
pid_entry.insert(tk.END, "PID|||9876543210||TEST^PATIENT||19700101|M|||1 Test Street^^Testville^London^SE1 2AB||02079460000")
pv1_entry.insert(tk.END, "PV1||I|W^389^1^A^^^||||1234^PrimaryDoctor^Joe||||||||||5678")

root.mainloop()
