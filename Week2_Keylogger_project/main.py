import tkinter as tk
from tkinter import messagebox
from logger import KeyLogger

class KeyloggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger")
        self.root.geometry("400x350")
        self.root.resizable(False, False)

        # Colors
        self.bg_color = "#f0f4f8"
        self.accent_color = "#3b82f6"
        self.text_color = "#1e293b"
        self.success_color = "#10b981"
        self.stop_color = "#ef4444"
        self.white = "#ffffff"

        self.root.configure(bg=self.bg_color)

        self.logger = KeyLogger()
        self.is_logging = False

        self.setup_ui()

    def setup_ui(self):
        # Main Container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Header
        header_label = tk.Label(main_frame, text="Keylogger", font=("Segoe UI", 24, "bold"),
                                bg=self.bg_color, fg=self.accent_color)
        header_label.pack(pady=(0, 5))

        sub_header = tk.Label(main_frame, text="Secure Activity Monitor", font=("Segoe UI", 10),
                              bg=self.bg_color, fg="#64748b")
        sub_header.pack(pady=(0, 30))

        # Status Indicator
        self.status_frame = tk.Frame(main_frame, bg=self.white, padx=20, pady=15)
        self.status_frame.pack(fill="x", pady=(0, 20))

        self.status_dot = tk.Label(self.status_frame, text="●", font=("Segoe UI", 14), bg=self.white, fg=self.stop_color)
        self.status_dot.pack(side="left")

        self.status_text = tk.Label(self.status_frame, text="Not Recording", font=("Segoe UI", 11, "bold"),
                                    bg=self.white, fg=self.text_color)
        self.status_text.pack(side="left", padx=10)

        # Control Button
        self.action_button = tk.Button(main_frame, text="Start Recording", font=("Segoe UI", 11, "bold"),
                                       bg=self.accent_color, fg=self.white, activebackground="#2563eb", 
                                       activeforeground=self.white, relief="flat", cursor="hand2", 
                                       command=self.toggle_logging, height=2)
        self.action_button.pack(fill="x", pady=10)

        # Footer
        footer_label = tk.Label(main_frame, text="Logs saved locally", font=("Segoe UI", 8), bg=self.bg_color, fg="#94a3b8")
        footer_label.pack(side="bottom")

    def toggle_logging(self):
        if not self.is_logging:
            self.start_logging()
        else:
            self.stop_logging()

    def start_logging(self):
        self.is_logging = True
        self.logger.start()

        # Update UI
        self.status_dot.config(fg=self.success_color)
        self.status_text.config(text="Recording Active")
        self.action_button.config(text="Stop Recording", bg=self.stop_color, activebackground="#dc2626")

    def stop_logging(self):
        self.is_logging = False
        self.logger.stop()

        # Update UI
        self.status_dot.config(fg=self.stop_color)
        self.status_text.config(text="Not Recording")
        self.action_button.config(text="Start Recording", bg=self.accent_color, activebackground="#2563eb")

        messagebox.showinfo("Saved", "Log files have been updated.")

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyloggerApp(root)
    root.mainloop()