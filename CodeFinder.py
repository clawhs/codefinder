import tkinter as tk
from tkinter import filedialog, messagebox
import csv

list1 = list2 = filtered_list = None

def center_window(window, width, height):
    position_top = int(window.winfo_screenheight() / 2 - height / 2)
    position_left = int(window.winfo_screenwidth() / 2 - width / 2)
    window.geometry(f"{width}x{height}+{position_left}+{position_top}")

def filter_codes(list1, list2, exact_match, avoid_data):
    avoid_list = [data.strip() for data in avoid_data.split(',')] if avoid_data else []
    result = []
    
    for code in list1:
        code_to_search = code.strip()
        for avoid in avoid_list:
            code_to_search = code_to_search.replace(avoid, "")
        
        matched_row = next((row for row in list2 if row and row[0] and 
                            ((exact_match and row[0].strip() == code_to_search) or 
                             (not exact_match and code_to_search.lower() in row[0].strip().lower()))), None)
        
        result.append([code] + matched_row[1:] if matched_row else [code] + ["MISSING"] * (len(list2[0]) - 1))
    
    return result

def load_list(is_first):
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path: return
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            if is_first:
                global list1
                list1 = [row[0].strip() for row in reader if row]
                label_first_list.config(text=f"First list loaded with {len(list1)} codes.")
                load_first_button.config(state="disabled")
                load_second_button.config(state="normal")
            else:
                global list2
                list2 = [row for row in reader if row]
                label_second_list.config(text=f"Second list loaded with {len(list2)} rows.")
            update_checkboxes_state()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load CSV file: {str(e)}")

def update_checkboxes_state():
    state = "normal" if list1 and list2 else "disabled"
    exact_match_check.config(state=state)
    partial_match_check.config(state=state)

def toggle_match_mode(mode):
    exact_match_var.set(mode == "exact")
    partial_match_var.set(mode == "partial")
    update_process_button_state()

def update_process_button_state():
    process_button.config(state="normal" if (exact_match_var.get() or partial_match_var.get()) and list1 and list2 else "disabled")

def process_lists():
    global filtered_list
    avoid_data = avoid_data_entry.get()
    filtered_list = filter_codes(list1, list2, exact_match_var.get(), avoid_data)
    save_button.config(state="normal")
    text_box.delete(1.0, tk.END)
    if filtered_list:
        text_box.insert(tk.END, ", ".join(filtered_list[0]))

def save_filtered_list():
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not save_path: return

    try:
        with open(save_path, mode='w', newline='', encoding='utf-8') as csvfile:
            csv.writer(csvfile).writerows(filtered_list)
        messagebox.showinfo("Success", f"Filtered list saved successfully to {save_path}")
    except PermissionError:
        error_window = tk.Toplevel(tk_root)
        error_window.title("File Open Error")
        error_window.geometry("400x150")
        center_window(error_window, 400, 150)
        tk.Label(error_window, text="You currently have this file open. Please close it and retry.").pack(pady=20)
        tk.Button(error_window, text="I have closed it, Retry.", command=lambda: save_filtered_list_retry(save_path, error_window)).pack(side="left", padx=20)
        tk.Button(error_window, text="Close", command=error_window.destroy).pack(side="right", padx=20)
        error_window.transient(tk_root)
        error_window.grab_set()

def save_filtered_list_retry(save_path, error_window):
    try:
        with open(save_path, mode='w', newline='', encoding='utf-8') as csvfile:
            csv.writer(csvfile).writerows(filtered_list)
        messagebox.showinfo("Success", f"Filtered list saved successfully to {save_path}")
        error_window.destroy()
    except PermissionError:
        messagebox.showwarning("Error", "Still unable to save. Please manually close the file and retry.")

def reset_gui():
    global list1, list2, filtered_list
    list1 = list2 = filtered_list = None
    label_first_list.config(text="No first list loaded yet.")
    label_second_list.config(text="No second list loaded yet.")
    load_first_button.config(state="normal")
    load_second_button.config(state="disabled")
    process_button.config(state="disabled")
    save_button.config(state="disabled")
    exact_match_var.set(False)
    partial_match_var.set(False)
    text_box.delete(1.0, tk.END)
    avoid_data_entry.delete(0, tk.END)
    update_checkboxes_state()

tk_root = tk.Tk()
tk_root.title("Code Filter from CSV")
center_window(tk_root, 550, 550)

exact_match_var = tk.BooleanVar()
partial_match_var = tk.BooleanVar()

tk.Label(tk_root, text="1. Input Codes From Our Website, ").pack(pady=5, fill='x')
load_first_button = tk.Button(tk_root, text="Load First List from CSV", command=lambda: load_list(True))
load_first_button.pack(pady=10)
label_first_list = tk.Label(tk_root, text="No first list loaded yet.")
label_first_list.pack(pady=5)

tk.Label(tk_root, text="2. Input The Whole Manufacturers Price List (Ensure Codes are in first column)").pack(pady=5)
load_second_button = tk.Button(tk_root, text="Load Second List from CSV", command=lambda: load_list(False), state="disabled")
load_second_button.pack(pady=10)
label_second_list = tk.Label(tk_root, text="No second list loaded yet.")
label_second_list.pack(pady=5)

frame_checkboxes = tk.Frame(tk_root)
frame_checkboxes.pack(pady=5)
tk.Label(tk_root, text="3. Choose Whether You Want Exact Or Partial Matches").pack(pady=5)
exact_match_check = tk.Checkbutton(frame_checkboxes, text="Exact Match", variable=exact_match_var, command=lambda: toggle_match_mode("exact"), state="disabled")
exact_match_check.pack(side="left", padx=5)
partial_match_check = tk.Checkbutton(frame_checkboxes, text="Partial Match", variable=partial_match_var, command=lambda: toggle_match_mode("partial"), state="disabled")
partial_match_check.pack(side="left", padx=5)

tk.Label(tk_root, text="Data To Avoid (Ex. -R, -G, -B, -inner) *Optional").pack(pady=5)
avoid_data_entry = tk.Entry(tk_root, width=40)
avoid_data_entry.pack(pady=5)

process_button = tk.Button(tk_root, text="Filter Codes", command=process_lists, state="disabled")
process_button.pack(pady=10)

text_box = tk.Text(tk_root, height=2, width=50, wrap=tk.WORD)
text_box.pack(pady=10)

frame_save_reset_buttons = tk.Frame(tk_root)
frame_save_reset_buttons.pack(pady=10)
save_button = tk.Button(frame_save_reset_buttons, text="Save Filtered List to CSV", command=save_filtered_list, state="disabled")
save_button.pack(side="left", padx=5)
reset_button = tk.Button(frame_save_reset_buttons, text="Reset", command=reset_gui)
reset_button.pack(side="right", padx=5)

tk_root.mainloop()
