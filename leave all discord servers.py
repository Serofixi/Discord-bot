import discord
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from PIL import ImageTk, Image
import io
import requests
import asyncio

client = discord.Client()

# Your user token here
TOKEN = ''

# Function to leave selected servers
async def leave_servers(selected_servers):
    for guild_id in selected_servers:
        guild = client.get_guild(int(guild_id))
        if guild:
            await guild.leave()
            print(f"Left guild: {guild.name}")

# Function to leave all servers
async def leave_all_servers():
    for guild in client.guilds:
        await guild.leave()
        print(f"Left guild: {guild.name}")

# Function to save server icon
def save_icon(guild):
    icon_url = guild.icon.url
    response = requests.get(icon_url)
    file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                             filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        messagebox.showinfo("Info", f"Saved icon for {guild.name}")

# Function to create the popup
def create_popup(guilds):
    root = tk.Tk()
    root.title("Leave Discord Servers")

    style = ttk.Style()
    style.configure("TFrame", background="#00274D")
    style.configure("TLabel", background="#00274D", foreground="white", font=("Helvetica", 12, "bold"))
    style.configure("TButton", background="white", foreground="black", font=("Helvetica", 12, "bold"))
    style.configure("TCheckbutton", background="#00274D", foreground="white", font=("Helvetica", 12, "bold"))
    style.configure("TCanvas", background="#00274D")
    style.configure("TScrollbar", background="#00274D")

    canvas = tk.Canvas(root, background="#00274D")
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview, style="TScrollbar")
    scroll_frame = ttk.Frame(canvas, style="TFrame")

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    guild_checkbuttons = []
    guild_vars = []

    def on_confirm():
        selected_guilds = [guild.id for var, guild in zip(guild_vars, guilds) if var.get() == 1]
        asyncio.run_coroutine_threadsafe(leave_servers(selected_guilds), client.loop)
        messagebox.showinfo("Info", "Left selected servers.")
        root.destroy()

    def on_leave_all():
        response = messagebox.askyesno("Confirm", "Are you sure you want to leave all servers?")
        if response:
            asyncio.run_coroutine_threadsafe(leave_all_servers(), client.loop)
            root.destroy()  # Close the main window after leaving all servers

    for guild in guilds:
        guild_var = tk.IntVar()
        guild_vars.append(guild_var)

        frame = ttk.Frame(scroll_frame, style="TFrame", relief="sunken", padding=5)
        frame.pack(fill=tk.X, padx=5, pady=5)

        if guild.icon:
            icon_url = guild.icon.url
            response = requests.get(icon_url)
            icon_data = io.BytesIO(response.content)
            icon_image = ImageTk.PhotoImage(Image.open(icon_data).resize((32, 32)))

            icon_label = ttk.Label(frame, image=icon_image, style="TLabel")
            icon_label.image = icon_image
            icon_label.pack(side=tk.LEFT, padx=5)

        name_checkbutton = ttk.Checkbutton(frame, text=guild.name, variable=guild_var, style="TCheckbutton")
        name_checkbutton.pack(side=tk.LEFT, padx=5)

        save_button = ttk.Button(frame, text="Save Icon", command=lambda g=guild: save_icon(g), style="TButton")
        save_button.pack(side=tk.LEFT, padx=5)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(-1 * (event.delta // 120), "units"))

    confirm_button = ttk.Button(root, text="Confirm", command=on_confirm, style="TButton")
    confirm_button.pack(pady=10)

    leave_all_button = tk.Button(root, text="Leave All Servers", command=on_leave_all,
                                 bg="red", fg="white", font=("Helvetica", 16, "bold"))
    leave_all_button.pack(pady=10)

    root.configure(background="#00274D")
    root.mainloop()

async def start_bot():
    print("Starting bot")
    await client.start(TOKEN)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    guilds = client.guilds
    print(f'Loaded {len(guilds)} guilds')
    create_popup(guilds)

def run_client():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

if __name__ == "__main__":
    run_client()
