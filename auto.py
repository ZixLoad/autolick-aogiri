import random
import threading
import time
import win32api, win32con, win32gui
import signal
import sys
import tkinter as tk

# Variable pour indiquer si le programme doit continuer à tourner
running = True
auto_click_enabled = False  # Variable pour activer/désactiver l'autoclicker

# Capturer le signal d'interruption (CTRL + C)
def signal_handler(sig, frame):
    global running
    print("Arrêt du programme")
    running = False

signal.signal(signal.SIGINT, signal_handler)

# Effectue un clic à la position actuelle de la souris
def click_mouse(button="left", bblock=False):
    if bblock:
        if button == 'left':
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        else:
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
    else:
        msg_down = win32con.WM_LBUTTONDOWN if button == 'left' else win32con.WM_RBUTTONDOWN
        msg_up = win32con.WM_LBUTTONUP if button == 'left' else win32con.WM_RBUTTONUP
        x, y = win32api.GetCursorPos()
        hwnd = win32gui.WindowFromPoint((x, y))
        win32api.SendMessage(hwnd, msg_down, 0, win32api.MAKELONG(x, y))
        win32api.SendMessage(hwnd, msg_up, 0, win32api.MAKELONG(x, y))

# Ajoute un effet "shake" à la souris
def shake_effect(shake_intensity=5):
    if shake_intensity == 0:
        return
    x, y = win32api.GetCursorPos()
    x_shake = random.randint(-shake_intensity, shake_intensity)
    y_shake = random.randint(-shake_intensity, shake_intensity)
    win32api.SetCursorPos((x + x_shake, y + y_shake))

# Calcule l'intervalle entre les clics selon un CPS donné
def interval_calculator(cps, randomize_factor=0):
    if cps <= 0:
        return 0.1  # Intervalle par défaut si CPS est 0 ou invalide
    rand_cps = cps + random.randint(-randomize_factor, randomize_factor)
    return 1.0 / max(rand_cps, 1)

# Fonction pour surveiller l'état du clic et effectuer des clics automatiques
def auto_click_when_pressed(cps=10, randomize=2, shake=5, bblock=False):
    global running, auto_click_enabled
    while running:
        if auto_click_enabled:
            left_button_state = win32api.GetAsyncKeyState(0x01) & 0x8000
            if left_button_state:
                interval = interval_calculator(cps, randomize)
                click_mouse('left', bblock)
                shake_effect(shake)
                time.sleep(interval)
            else:
                time.sleep(0.1)
        else:
            time.sleep(0.1)

# Thread pour exécuter l'autoclic
def start_click_thread(cps=10, randomize=2, shake=5, bblock=False):
    thread = threading.Thread(target=auto_click_when_pressed, args=(cps, randomize, shake, bblock))
    thread.start()
    return thread

def toggle_auto_click():
    global auto_click_enabled
    auto_click_enabled = not auto_click_enabled
    toggle_button.config(text="Stop" if auto_click_enabled else "Start")
    print(f"Autoclicker {'activé' if auto_click_enabled else 'désactivé'}")

def apply_settings():
    cps = int(cps_entry.get())
    randomize = int(randomize_entry.get())
    shake = int(shake_entry.get())
    toggle_auto_click()  # Démarre ou arrête l'autoclick
    if auto_click_enabled:
        start_click_thread(cps=cps, randomize=randomize, shake=shake)

def monitor_keyboard():
    global running
    while running:
        if win32api.GetAsyncKeyState(ord('T')) & 0x8000:
            toggle_auto_click()
            while win32api.GetAsyncKeyState(ord('T')) & 0x8000:
                time.sleep(0.1)
        time.sleep(0.1)

# Interface graphique avec tkinter
root = tk.Tk()
root.title("Auto Clicker")

# Labels et champs pour CPS, Randomize et Shake
tk.Label(root, text="CPS:").grid(row=0, column=0, padx=10, pady=5)
cps_entry = tk.Entry(root)
cps_entry.grid(row=0, column=1, padx=10, pady=5)
cps_entry.insert(0, "10")

tk.Label(root, text="Randomize:").grid(row=1, column=0, padx=10, pady=5)
randomize_entry = tk.Entry(root)
randomize_entry.grid(row=1, column=1, padx=10, pady=5)
randomize_entry.insert(0, "2")

tk.Label(root, text="Shake:").grid(row=2, column=0, padx=10, pady=5)
shake_entry = tk.Entry(root)
shake_entry.grid(row=2, column=1, padx=10, pady=5)
shake_entry.insert(0, "5")

# Bouton pour appliquer les paramètres et démarrer/arrêter
toggle_button = tk.Button(root, text="Start", command=apply_settings)
toggle_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

def on_close():
    global running
    running = False
    root.quit()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)


keyboard_thread = threading.Thread(target=monitor_keyboard)
keyboard_thread.start()

# Lancer l'interface tkinter
root.mainloop()

running = False
keyboard_thread.join()  
