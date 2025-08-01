import os
import threading
import customtkinter as ctk
from yt_dlp import YoutubeDL
from tkinter import filedialog, messagebox

# تنظیم تم مدرن
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# مسیر ثابت ffmpeg (می‌تونید اینجا تغییر بدید اگر لازم بود)
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"  # r برای جلوگیری از مشکلات بک‌اسلش

class YouTubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("دانلودر یوتیوب - مدرن")
        self.geometry("600x500")
        self.resizable(False, False)

        # متغیرها
        self.mode = ctk.StringVar(value="ویدیو تک")
        self.quality = ctk.StringVar(value="720p")
        self.url = None
        self.download_path = os.path.expanduser("~") + "/Downloads"
        self.use_cookies = False
        self.browser = "chrome"

        # رابط گرافیکی
        self.create_widgets()

    def create_widgets(self):
        # عنوان
        label = ctk.CTkLabel(self, text="دانلودر یوتیوب", font=("Arial", 24))
        label.pack(pady=20)

        # انتخاب حالت
        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(pady=10)
        ctk.CTkLabel(mode_frame, text="حالت دانلود:").pack(side="left", padx=10)
        modes = ["ویدیو تک", "پلی‌لیست", "کانال کامل"]
        mode_menu = ctk.CTkOptionMenu(mode_frame, values=modes, variable=self.mode)
        mode_menu.pack(side="left")

        # ورودی URL
        url_frame = ctk.CTkFrame(self)
        url_frame.pack(pady=10)
        ctk.CTkLabel(url_frame, text="URL:").pack(side="left", padx=10)
        self.url_entry = ctk.CTkEntry(url_frame, width=300)
        self.url_entry.pack(side="left")

        # انتخاب کیفیت
        quality_frame = ctk.CTkFrame(self)
        quality_frame.pack(pady=10)
        ctk.CTkLabel(quality_frame, text="کیفیت:").pack(side="left", padx=10)
        qualities = ["480p", "720p", "1080p", "فقط صدا"]
        quality_menu = ctk.CTkOptionMenu(quality_frame, values=qualities, variable=self.quality)
        quality_menu.pack(side="left")

        # فولدر دانلود
        path_frame = ctk.CTkFrame(self)
        path_frame.pack(pady=10)
        ctk.CTkLabel(path_frame, text="فولدر دانلود:").pack(side="left", padx=10)
        self.path_label = ctk.CTkLabel(path_frame, text=self.download_path)
        self.path_label.pack(side="left", padx=10)
        browse_btn = ctk.CTkButton(path_frame, text="انتخاب فولدر", command=self.browse_folder)
        browse_btn.pack(side="left")

        # گزینه کوکی
        cookie_frame = ctk.CTkFrame(self)
        cookie_frame.pack(pady=10)
        self.cookie_check = ctk.CTkCheckBox(cookie_frame, text="استفاده از کوکی مرورگر (برای محدودیت‌ها)", command=self.toggle_cookies)
        self.cookie_check.pack(side="left")
        browsers = ["chrome", "firefox", "edge"]
        self.browser_menu = ctk.CTkOptionMenu(cookie_frame, values=browsers, variable=ctk.StringVar(value="chrome"))
        self.browser_menu.pack(side="left", padx=10)
        self.browser_menu.configure(state="disabled")

        # دکمه دانلود
        download_btn = ctk.CTkButton(self, text="دانلود", command=self.start_download, fg_color="green", hover_color="dark green")
        download_btn.pack(pady=20)

        # پیشرفت
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.pack(pady=10)
        self.progress.set(0)
        self.status_label = ctk.CTkLabel(self, text="وضعیت: آماده")
        self.status_label.pack(pady=10)

    def toggle_cookies(self):
        self.use_cookies = self.cookie_check.get()
        self.browser_menu.configure(state="normal" if self.use_cookies else "disabled")
        self.browser = self.browser_menu.get()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path = folder
            self.path_label.configure(text=folder)

    def start_download(self):
        self.url = self.url_entry.get().strip()
        if not self.url:
            messagebox.showerror("خطا", "لطفاً URL وارد کنید!")
            return

        threading.Thread(target=self.download).start()

    def download(self):
        try:
            self.status_label.configure(text="در حال دانلود...")
            self.progress.set(0)

            # تنظیم کیفیت اصلی (با ادغام)
            quality_map = {
                "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
                "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
                "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                "فقط صدا": "bestaudio[ext=m4a]/best"
            }
            format = quality_map[self.quality.get()]

            # تنظیمات yt-dlp
            ydl_opts = {
                'format': format,
                'outtmpl': os.path.join(self.download_path, '%(playlist_index)s - %(title)s.%(ext)s') if self.mode.get() != "ویدیو تک" else os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'noplaylist': self.mode.get() == "ویدیو تک",
                'quiet': False,
                'progress_hooks': [self.progress_hook],
                'continuedl': True,
                'no_warnings': True,
                'ffmpeg_location': FFMPEG_PATH,  # مسیر ثابت ffmpeg
            }

            if self.mode.get() in ["پلی‌لیست", "کانال کامل"]:
                ydl_opts['playlistreverse'] = False
                ydl_opts['playliststart'] = 1

            if self.use_cookies:
                ydl_opts['cookiesfrombrowser'] = (self.browser,)

            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.url])
            except Exception as inner_e:
                if "ffmpeg" in str(inner_e).lower():
                    # اگر مشکل ffmpeg بود، به حالت بدون ادغام سوییچ کن
                    self.status_label.configure(text="مشکل ffmpeg - دانلود بدون ادغام...")
                    fallback_map = {
                        "480p": "best[height<=480]",
                        "720p": "best[height<=720]",
                        "1080p": "best[height<=1080]",
                        "فقط صدا": "bestaudio[ext=m4a]/best"
                    }
                    ydl_opts['format'] = fallback_map[self.quality.get()]
                    del ydl_opts['ffmpeg_location']  # حذف برای جلوگیری از ارور
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([self.url])
                else:
                    raise inner_e

            self.status_label.configure(text="دانلود کامل شد!")
            self.progress.set(1)
            messagebox.showinfo("موفقیت", "دانلود با موفقیت انجام شد!")

        except Exception as e:
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower():
                messagebox.showerror("خطا", f"مشکل با ffmpeg. مسیر رو چک کنید: {FFMPEG_PATH}. اگر درست نیست، کد رو ویرایش کنید.")
            elif "sign in" in error_msg.lower() or "login" in error_msg.lower():
                messagebox.showerror("خطا", "یوتیوب درخواست لاگین کرده. گزینه کوکی رو فعال کنید.")
            elif "network" in error_msg.lower():
                messagebox.showerror("خطا", "مشکل اینترنت.")
            elif "invalid url" in error_msg.lower():
                messagebox.showerror("خطا", "URL نامعتبر.")
            else:
                messagebox.showerror("خطا", f"خطای نامشخص: {error_msg}")
            self.status_label.configure(text="خطا رخ داد!")
            self.progress.set(0)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes')
            if total and downloaded:
                self.progress.set(downloaded / total)
        elif d['status'] == 'finished':
            self.progress.set(1)

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()