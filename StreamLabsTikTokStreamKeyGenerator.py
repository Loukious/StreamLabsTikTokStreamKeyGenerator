import json
import multiprocessing
import threading
import tkinter as tk
from tkinter import messagebox
import webbrowser
from Stream import Stream
from TokenRetriever import TokenRetriever
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def load_config():
    """Load entry values from a JSON file."""
    try:
        with open("config.json", "r+") as file:
            data = json.load(file)
            
        token_entry.delete(0, tk.END)
        token_entry.insert(0, data.get("token", ""))

        stream_title_entry.config(state=tk.NORMAL)
        stream_title_entry.delete(0, tk.END)
        stream_title_entry.insert(0, data.get("title", ""))
        stream_title_entry.config(state=tk.DISABLED)


        game_category_entry.config(state=tk.NORMAL)
        game_category_entry.delete(0, tk.END)
        game_category_entry.insert(0, data.get("game", ""))
        game_category_entry.config(state=tk.DISABLED)
        
        audience_type_checkbox.config(state=tk.NORMAL)
        audience_type_var.set(data.get("audience_type", "0"))
        audience_type_checkbox.config(state=tk.DISABLED)

        if token_entry.get():
            global stream
            stream = Stream(token_entry.get())
            go_live_button.config(state=tk.NORMAL)
            stream_title_entry.config(state=tk.NORMAL)
            game_category_entry.config(state=tk.NORMAL)
            audience_type_checkbox.config(state=tk.NORMAL)
            load_account_info()

        if stream:
            fetch_game_mask_id(data.get("game", ""))

    except:
        print("Error loading config file. Ignore this if it's the first time running the program or you never saved your config before.")


def load_account_info():
    if stream:
        info = stream.getInfo()
        if "user" in info and "username" in info["user"]:
            tiktok_username_entry.config(state=tk.NORMAL)
            tiktok_username_entry.delete(0, tk.END)
            tiktok_username_entry.insert(0, info["user"]["username"])
            tiktok_username_entry.config(state=tk.DISABLED)
        else:
            tiktok_username_entry.config(state=tk.NORMAL)
            tiktok_username_entry.delete(0, tk.END)
            tiktok_username_entry.insert(0, "Unknown")
            tiktok_username_entry.config(state=tk.DISABLED)
        if "application_status" in info and "status" in info["application_status"]:
            streamlabs_app_status_entry.config(state=tk.NORMAL)
            streamlabs_app_status_entry.delete(0, tk.END)
            streamlabs_app_status_entry.insert(0, info["application_status"]["status"])
            streamlabs_app_status_entry.config(state=tk.DISABLED)
        else:
            streamlabs_app_status_entry.config(state=tk.NORMAL)
            streamlabs_app_status_entry.delete(0, tk.END)
            streamlabs_app_status_entry.insert(0, "Unknown")
            streamlabs_app_status_entry.config(state=tk.DISABLED)
        if "can_be_live" in info:
            can_go_live_entry.config(state=tk.NORMAL)
            can_go_live_entry.delete(0, tk.END)
            can_go_live_entry.insert(0, str(info["can_be_live"]))
            can_go_live_entry.config(state=tk.DISABLED)
        else:
            can_go_live_entry.config(state=tk.NORMAL)
            can_go_live_entry.delete(0, tk.END)
            can_go_live_entry.insert(0, "Unknown")
            can_go_live_entry.config(state=tk.DISABLED)


def fetch_game_mask_id(game_name):
    categories = stream.search(game_name)
    for category in categories:
        if category['full_name'] == game_name:
            game_category_entry.game_mask_id = category['game_mask_id']
            return category['game_mask_id']
    return ""

def save_config():
    """Save entry values to a JSON file."""
    data = {
        "title": stream_title_entry.get(),
        "game": game_category_entry.get(),
        "audience_type": audience_type_var.get(),
        "token": token_entry.get()
    }
    with open("config.json", "w") as file:
        json.dump(data, file)

def load_token():
    import os
    import re
    import glob
    import platform

    # Determine the correct path based on the operating system
    if platform.system() == 'Windows':
        path_pattern = os.path.expandvars(r'%appdata%\slobs-client\Local Storage\leveldb\*.log')
    elif platform.system() == 'Darwin':  # macOS
        path_pattern = os.path.expanduser('~/Library/Application Support/slobs-client/Local Storage/leveldb/*.log')
    else:
        return None

    # Get all files matching the pattern
    files = glob.glob(path_pattern)
    
    # Sort files by date modified, newest first
    files.sort(key=os.path.getmtime, reverse=True)
    
    # Define the regex pattern to search for the apiToken
    token_pattern = re.compile(r'"apiToken":"([a-f0-9]+)"', re.IGNORECASE)
    
    # Loop through files and search for the token pattern
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = token_pattern.findall(content)
                if matches:
                    # Get the last occurrence of the token
                    token = matches[-1]
                    return token
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file {file}: {e}")
    
    messagebox.showinfo("API Token", "No API Token found locally. A webpage will now open to allow you to login into your TikTok account.")
    return None

def fetch_online_token():
    retriever = TokenRetriever()
    token = retriever.retrieve_token()
    if token:
        token_entry.delete(0, tk.END)
        token_entry.insert(0, token)
        token_entry.config(show='*')
        global stream
        stream = Stream(token)
        stream_title_entry.config(state=tk.NORMAL)
        game_category_entry.config(state=tk.NORMAL)
        go_live_button.config(state=tk.NORMAL)
        audience_type_checkbox.config(state=tk.NORMAL)
        fetch_game_mask_id(game_category_entry.get())
        load_account_info()
    else:
        messagebox.showerror("Error", "Failed to obtain token online.")

def populate_token():
    global stream
    token = load_token()
    if not token:
        fetch_online_token()  # If no local token, try fetching online
    else:
        token_entry.delete(0, tk.END)
        token_entry.insert(0, token)
        token_entry.config(show='*')
        stream = Stream(token)
        load_account_info()
        stream_title_entry.config(state=tk.NORMAL)
        game_category_entry.config(state=tk.NORMAL)
        go_live_button.config(state=tk.NORMAL)
        # Fetch game_mask_id after token is loaded
        fetch_game_mask_id(game_category_entry.get())

def toggle_token_visibility():
    if token_entry.cget('show') == '':
        token_entry.config(show='*')
        toggle_button.config(text='Show Token')
    else:
        token_entry.config(show='')
        toggle_button.config(text='Hide Token')

def on_token_entry_change(*args):
    if token_entry.get():  # Check if the token_entry has any text
        go_live_button.config(state=tk.NORMAL)  # Enable the Go Live button
    else:
        go_live_button.config(state=tk.DISABLED)  # Disable the Go Live button if empty

def go_live():
    game_mask_id = getattr(game_category_entry, 'game_mask_id', "")

    stream_url, stream_key = stream.start(stream_title_entry.get(), game_mask_id, audience_type_var.get())

    if stream_url or stream_key:
        stream_url_entry.config(state=tk.NORMAL)
        stream_key_entry.config(state=tk.NORMAL)

        stream_url_entry.delete(0, tk.END)
        stream_url_entry.insert(0, stream_url)

        stream_key_entry.delete(0, tk.END)
        stream_key_entry.insert(0, stream_key)

        stream_url_entry.config(state='readonly')
        stream_key_entry.config(state='readonly')
        
        end_live_button.config(state=tk.NORMAL)
        messagebox.showinfo("Go Live", "Stream started successfully!")
    else:
        messagebox.showerror("Go Live", "Error starting stream.")


def end_live():
    end_live_button.config(state=tk.DISABLED)
    stream_url_entry.config(state=tk.NORMAL)
    stream_key_entry.config(state=tk.NORMAL)

    stream_url_entry.delete(0, tk.END)
    stream_url_entry.insert(0, "")

    stream_key_entry.delete(0, tk.END)
    stream_key_entry.insert(0, "")

    stream_url_entry.config(state='readonly')
    stream_key_entry.config(state='readonly')
    if stream:
        success = stream.end()
        if success:
            messagebox.showinfo("End Live", "Stream ended successfully!")
        else:
            messagebox.showerror("End Live", "Error ending stream.")
    else:
        messagebox.showerror("End Live", "No active stream found.")

def copy_to_clipboard(entry):
    root.clipboard_clear()
    root.clipboard_append(entry.get())
    messagebox.showinfo("Copy", "Copied to clipboard!")

def show_help():
    help_window = tk.Toplevel(root)
    help_window.title("Help")
    
    help_message = """\
    1. First you have to apply and get access to LIVE on Streamlabs using the link on the bottom
    2. Install Streamlabs and log into your TikTok account
    3. Use this app to get Streamlabs token
    4. Go live!
    """

    help_label = tk.Label(help_window, text=help_message, justify='left', padx=10, pady=10)
    help_label.pack()

    help_link = tk.Label(help_window, text="Click here to apply for LIVE access on Streamlabs", fg="blue", cursor="hand2")
    help_link.pack()
    help_link.bind("<Button-1>", lambda e: webbrowser.open("https://tiktok.com/falcon/live_g/live_access_pc_apply/result/index.html?id=GL6399433079641606942&lang=en-US"))

def on_keyrelease(event):
    value = event.widget.get()
    if value == '':
        listbox.pack_forget()
    else:
        threading.Thread(target=search_and_update_listbox, args=(value,)).start()

def search_and_update_listbox(value):
    categories = stream.search(value)
    listbox.delete(0, tk.END)
    for category in categories:
        listbox.insert(tk.END, category['full_name'])
    if categories:
        listbox.pack(fill='x', pady=(0, 10))
    else:
        listbox.pack_forget()

def on_select(event):
    widget = event.widget
    selection = widget.curselection()
    if selection:
        index = selection[0]
        data = widget.get(index)
        game_category_entry.delete(0, tk.END)
        game_category_entry.insert(0, data)
        game_category_entry.game_mask_id = fetch_game_mask_id(data)
        listbox.pack_forget()

def on_motion(event):
    widget = event.widget
    widget.focus_set()
    widget.selection_clear(0, tk.END)
    index = widget.nearest(event.y)
    widget.selection_set(index)
    widget.activate(index)

# Create the main window
root = tk.Tk()
root.title("StreamLabs TikTok Stream Key Generator")

# Create a LabelFrame for token loading
token_frame = tk.LabelFrame(root, text="Token Loader", padx=10, pady=10)
token_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

# Create the "Load token" button
load_button = tk.Button(token_frame, text="Load token", command=populate_token)
load_button.pack(pady=5)

# Create a text entry to display the token, initially hidden
token_var = tk.StringVar()
token_entry = tk.Entry(token_frame, width=50, textvariable=token_var, show='*', justify='center')
token_entry.pack(pady=5)

# Bind the StringVar to the on_token_entry_change function
token_var.trace_add("write", on_token_entry_change)

# Create a button to toggle token visibility
toggle_button = tk.Button(token_frame, text="Show Token", command=toggle_token_visibility)
toggle_button.pack(pady=5)

# Tiktok Username
tiktok_username_label = tk.Label(token_frame, text="TikTok Username:")
tiktok_username_label.pack(pady=5)

tiktok_username_var = tk.StringVar()
tiktok_username_entry = tk.Entry(token_frame, textvariable=tiktok_username_var, width=50, state=tk.DISABLED)
tiktok_username_entry.pack(pady=5)

# StreamLabs application status
streamlabs_app_status_label = tk.Label(token_frame, text="StreamLabs Application Status:")
streamlabs_app_status_label.pack(pady=5)

streamlabs_app_status_var = tk.StringVar()
streamlabs_app_status_entry = tk.Entry(token_frame, textvariable=streamlabs_app_status_var, width=50, state=tk.DISABLED)
streamlabs_app_status_entry.pack(pady=5)

# Can go live?
can_go_live_label = tk.Label(token_frame, text="Can Go Live:")
can_go_live_label.pack(pady=5)

can_go_live_var = tk.StringVar()
can_go_live_entry = tk.Entry(token_frame, textvariable=can_go_live_var, width=50, state=tk.DISABLED)
can_go_live_entry.pack(pady=5)

# Create a LabelFrame for stream details
stream_frame = tk.LabelFrame(root, text="Stream Details", padx=10, pady=10)
stream_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

# Create a label for stream title
stream_title_label = tk.Label(stream_frame, text="Stream Title:")
stream_title_label.pack(pady=5)

# Create a text entry for stream title
stream_title_entry = tk.Entry(stream_frame, width=50, state=tk.DISABLED)
stream_title_entry.pack(pady=5)

# Create a label for game category
game_category_label = tk.Label(stream_frame, text="Game:")
game_category_label.pack(pady=5)

# Create a text entry for game category
game_category_entry = tk.Entry(stream_frame, width=50, state=tk.DISABLED)
game_category_entry.pack(pady=5)

# Bind the key release event for auto-complete
game_category_entry.bind('<KeyRelease>', on_keyrelease)

# Create a listbox for suggestions
listbox = tk.Listbox(stream_frame)
listbox.pack_forget()
listbox.bind("<<ListboxSelect>>", on_select)
listbox.bind("<Motion>", on_motion)

# Create a StringVar to hold the value for audience type
audience_type_var = tk.StringVar(value='0')  # Default to '0' (everyone)

# Create a checkbox for mature content
audience_type_checkbox = tk.Checkbutton(
    stream_frame,
    text="Enable mature content",
    variable=audience_type_var,
    onvalue='1',  # Set to '1' when checked
    offvalue='0',  # Set to '0' when unchecked
    state=tk.DISABLED
)
audience_type_checkbox.pack(pady=5)

# Create a LabelFrame for stream control buttons and info
control_frame = tk.LabelFrame(root, text="Stream Control", padx=10, pady=10)
control_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky='nsew')

# Create "Go Live" and "End Live" buttons
go_live_button = tk.Button(control_frame, text="Go Live", command=go_live, state=tk.DISABLED)
go_live_button.pack(pady=5)

end_live_button = tk.Button(control_frame, text="End Live", command=end_live, state=tk.DISABLED)
end_live_button.pack(pady=5)

# Create read-only text entries for stream URL and stream key with copy buttons
stream_url_label = tk.Label(control_frame, text="Stream URL:")
stream_url_label.pack(pady=5)

stream_url_entry = tk.Entry(control_frame, width=50, state='readonly')
stream_url_entry.pack(pady=5)

copy_url_button = tk.Button(control_frame, text="Copy URL", command=lambda: copy_to_clipboard(stream_url_entry))
copy_url_button.pack(pady=5)

stream_key_label = tk.Label(control_frame, text="Stream Key:")
stream_key_label.pack(pady=5)

stream_key_entry = tk.Entry(control_frame, width=50, state='readonly')
stream_key_entry.pack(pady=5)

copy_key_button = tk.Button(control_frame, text="Copy Key", command=lambda: copy_to_clipboard(stream_key_entry))
copy_key_button.pack(pady=5)

save_config_button = tk.Button(root, text="Save Config", command=save_config)
save_config_button.grid(row=2, column=0, padx=10, pady=10, columnspan=2, sticky='ew')

# Create a "Help" button
help_button = tk.Button(root, text="Help", command=show_help)
help_button.grid(row=3, column=0, padx=10, pady=10, columnspan=2, sticky='ew')

open_live_monitor_button = tk.Button(root, text="Open Live Monitor", command=lambda: webbrowser.open("https://livecenter.tiktok.com/live_monitor?lang=en-US"))
open_live_monitor_button.grid(row=4, column=0, padx=10, pady=10, columnspan=2, sticky='ew')

# Configure the grid weights for proper resizing behavior
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)

# Start the Tkinter event loop
if __name__ == "__main__":
    multiprocessing.freeze_support()
    stream = None
    load_config()
    root.mainloop()
