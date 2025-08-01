import pandas as pd
from yt_dlp import YoutubeDL

def get_playlists(channel_url):
    # اگر آدرس کانال داده شده، به صفحه پلی‌لیست‌ها هدایت شود
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
                # فقط پلی‌لیست‌هایی که id دارند
                pl_id = entry.get('id') or entry.get('url')
                if pl_id and entry.get('title'):
                    playlists.append({
                        'name': entry.get('title', ''),
                        'url': f'https://www.youtube.com/playlist?list={pl_id}'
                    })
    return playlists

def main():
    channel_url = input("آدرس کانال یوتیوب را وارد کنید: ").strip()
    playlists = get_playlists(channel_url)
    if not playlists:
        print("هیچ پلی‌لیستی پیدا نشد.")
        return
    # تبدیل به DataFrame و ذخیره در اکسل
    df = pd.DataFrame(playlists)
    df['url'] = df['url'].apply(lambda u: f'https://www.youtube.com/playlist?list={u}' if not u.startswith('http') else u)
    df.to_excel('playlists.xlsx', index=False)
    print("فایل playlists.xlsx با موفقیت ذخیره شد.")

if __name__ == "__main__":
    main()
