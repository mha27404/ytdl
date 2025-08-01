
import pandas as pd
from yt_dlp import YoutubeDL
import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def get_playlists(channel_url):
    if '/playlists' not in channel_url:
        if channel_url.endswith('/'):
            channel_url += 'playlists'
        else:
            channel_url += '/playlists'
    ydl_opts = {
        'extract_flat': True,
        'skip_download': True,
        'quiet': True,
    }
    playlists = []
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        if 'entries' in info:
            for entry in info['entries']:
                pl_id = entry.get('id') or entry.get('url')
                if pl_id and entry.get('title'):
                    playlists.append({
                        'name': entry.get('title', ''),
                        'url': f'https://www.youtube.com/playlist?list={pl_id}'
                    })
    return playlists

class PlaylistExtractorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("استخراج پلی‌لیست‌های کانال یوتیوب")
        self.geometry("500x300")
        self.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        label = ctk.CTkLabel(self, text="آدرس کانال یوتیوب را وارد کنید:", font=("Arial", 16))
        label.pack(pady=20)

        self.url_entry = ctk.CTkEntry(self, width=400)
        self.url_entry.pack(pady=10)

        self.extract_btn = ctk.CTkButton(self, text="استخراج پلی‌لیست‌ها و ذخیره در اکسل", command=self.extract_playlists, fg_color="green", hover_color="dark green")
        self.extract_btn.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="وضعیت: آماده")
        self.status_label.pack(pady=10)

    def extract_playlists(self):
        channel_url = self.url_entry.get().strip()
        if not channel_url:
            messagebox.showerror("خطا", "لطفاً آدرس کانال را وارد کنید!")
            return
        self.status_label.configure(text="در حال استخراج...")
        self.update()
        try:
            playlists = get_playlists(channel_url)
            if not playlists:
                messagebox.showinfo("نتیجه", "هیچ پلی‌لیستی پیدا نشد.")
                self.status_label.configure(text="هیچ پلی‌لیستی پیدا نشد.")
                return
            df = pd.DataFrame(playlists)
            # استخراج نام کانال از آدرس
            import re
            match = re.search(r"(?:channel/|@)([\w\-\.]+)", channel_url)
            if match:
                channel_name = match.group(1)
            else:
                channel_name = "channel"
            excel_filename = f"{channel_name}_playlists.xlsx"
            df.to_excel(excel_filename, index=False)
            messagebox.showinfo("موفقیت", f"فایل {excel_filename} با موفقیت ذخیره شد.")
            self.status_label.configure(text="استخراج کامل شد!")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا: {str(e)}")
            self.status_label.configure(text="خطا رخ داد!")

if __name__ == "__main__":
    app = PlaylistExtractorApp()
    app.mainloop()
