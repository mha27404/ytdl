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
        self.geometry("600x550")
        self.resizable(False, False)

        # متغیرها
        self.mode = ctk.StringVar(value="ویدیو تک")
        self.quality = ctk.StringVar(value="720p")
        self.url = None
        self.download_path = os.path.expanduser("~") + "/Downloads"
        self.use_cookies = False
        self.browser = "chrome"
        self.scheduled_time = None
        self._remaining_seconds = 0
        self._timer_thread = None
        self._stop_timer = threading.Event()

        # رابط گرافیکی
        self.create_widgets()  # Call to create widgets

    def create_widgets(self):
        # عنوان
        label = ctk.CTkLabel(self, text="دانلودر یوتیوب", font=("Arial", 24))
        label.pack(pady=20)

        # زمانبندی دانلود (شروع و پایان)
        schedule_frame = ctk.CTkFrame(self)
        schedule_frame.pack(pady=10)
        ctk.CTkLabel(schedule_frame, text="زمان شروع:").pack(side="left", padx=5)
        self.schedule_start_entry = ctk.CTkEntry(schedule_frame, width=70, placeholder_text="hh:mm")
        self.schedule_start_entry.pack(side="left")
        ctk.CTkLabel(schedule_frame, text="زمان پایان:").pack(side="left", padx=5)
        self.schedule_end_entry = ctk.CTkEntry(schedule_frame, width=70, placeholder_text="hh:mm")
        self.schedule_end_entry.pack(side="left")
        ctk.CTkLabel(schedule_frame, text="(مثال: 23:30)").pack(side="left", padx=5)

        # دکمه دانلود
        download_btn = ctk.CTkButton(self, text="دانلود", command=self.handle_download_button, fg_color="green", hover_color="dark green")
        download_btn.pack(pady=20)

        # پیشرفت
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.pack(pady=10)
        self.progress.set(0)
        self.status_label = ctk.CTkLabel(self, text="وضعیت: آماده")
        self.status_label.pack(pady=10)

        # نمایش زمان باقی‌مانده تا شروع دانلود
        self.timer_label = ctk.CTkLabel(self, text="")
        self.timer_label.pack(pady=5)

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


    def handle_download_button(self):
        # بررسی زمانبندی شروع و پایان
        start_str = self.schedule_start_entry.get().strip()
        end_str = self.schedule_end_entry.get().strip()
        import datetime
        if start_str:
            try:
                now = datetime.datetime.now()
                hour, minute = map(int, start_str.split(":"))
                scheduled_start = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if scheduled_start < now:
                    scheduled_start = scheduled_start + datetime.timedelta(days=1)
                self.scheduled_time = scheduled_start
                self._remaining_seconds = int((scheduled_start - now).total_seconds())
                # زمان پایان
                if end_str:
                    end_hour, end_minute = map(int, end_str.split(":"))
                    scheduled_end = scheduled_start.replace(hour=end_hour, minute=end_minute)
                    if scheduled_end <= scheduled_start:
                        scheduled_end += datetime.timedelta(days=1)
                    self.scheduled_end_time = scheduled_end
                else:
                    self.scheduled_end_time = None
                self.status_label.configure(text=f"دانلود زمانبندی شد برای {scheduled_start.strftime('%H:%M')}{' تا ' + self.scheduled_end_time.strftime('%H:%M') if self.scheduled_end_time else ''}")
                self._stop_timer.clear()
                self._timer_thread = threading.Thread(target=self._countdown_and_start_download)
                self._timer_thread.start()
            except Exception:
                messagebox.showerror("خطا", "فرمت زمان اشتباه است. مثال: 23:30")
        else:
            self.start_download()

    def _countdown_and_start_download(self):
        import time
        # شمارش معکوس تا شروع
        while self._remaining_seconds > 0 and not self._stop_timer.is_set():
            mins, secs = divmod(self._remaining_seconds, 60)
            hours, mins = divmod(mins, 60)
            time_str = f"زمان باقی‌مانده تا شروع دانلود: {hours:02d}:{mins:02d}:{secs:02d}"
            self.timer_label.after(0, lambda t=time_str: self.timer_label.configure(text=t))
            time.sleep(1)
            self._remaining_seconds -= 1
        if not self._stop_timer.is_set():
            self.timer_label.after(0, lambda: self.timer_label.configure(text=""))
            # اگر زمان پایان تعریف شده بود، دانلود را شروع و در زمان پایان متوقف کن
            if hasattr(self, 'scheduled_end_time') and self.scheduled_end_time:
                self._download_thread = threading.Thread(target=self._download_with_end_time)
                self._download_thread.start()
            else:
                self.start_download()

    def _download_with_end_time(self):
        import datetime, time
        self._download_active = True
        download_thread = threading.Thread(target=self.start_download)
        download_thread.start()
        while self._download_active:
            now = datetime.datetime.now()
            if now >= self.scheduled_end_time:
                self._stop_timer.set()
                self.status_label.after(0, lambda: self.status_label.configure(text="دانلود به پایان زمانبندی رسید!"))
                # اگر دانلود هنوز ادامه دارد، thread را متوقف کن (در صورت امکان)
                # در اینجا فقط پیام می‌دهیم و کاربر باید دانلود را متوقف کند یا برنامه را ببندد
                break
            time.sleep(1)

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

        # اگر تایمر فعال بود، متوقف کن
        self._stop_timer.set()
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
    # پایان برنامه 