import os
import subprocess
import sys
import yt_dlp
from colorama import init, Fore, Style
from tqdm import tqdm
import platform
import time

def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        print(f"{package} not found, installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    finally:
        globals()[package] = __import__(package)

packages = ["requests", "yt_dlp", "colorama", "tqdm", "time", "instaloader"]

for package in packages:
    install_and_import(package)

import instaloader

init(autoreset=True)

def create_download_path(base_path, platform):
    platform_path = os.path.join(base_path, platform.lower())
    os.makedirs(platform_path, exist_ok=True)
    return platform_path

def download_hook(d):
    if d['status'] == 'downloading':
        if not hasattr(download_hook, 'progress_bar'):
            download_hook.progress_bar = tqdm(
                total=d['total_bytes'],
                unit='B',
                unit_scale=True,
                desc='Downloading',
                bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.YELLOW, Fore.RESET),
                ncols=100
            )
        download_hook.progress_bar.update(d['downloaded_bytes'] - download_hook.progress_bar.n)
    elif d['status'] == 'finished':
        if hasattr(download_hook, 'progress_bar'):
            download_hook.progress_bar.close()
            delattr(download_hook, 'progress_bar')
        print(Fore.GREEN + f"\nDownload complete! Saved to: {d['filename']}" + Style.RESET_ALL)

def download_youtube(url, file_type, quality, download_path):
    ydl_opts = {
        'format': 'bestaudio/best' if file_type == 'mp3' else f'bestvideo[ext=mp4][height<={quality}]+bestaudio/best[ext=m4a]',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}] if file_type == 'mp3' else [],
        'progress_hooks': [download_hook]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_tiktok(url, download_path):
    ydl_opts = {
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'format': 'best',
        'progress_hooks': [download_hook]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_facebook(url, download_path):
    ydl_opts = {
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'format': 'best',
        'progress_hooks': [download_hook]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_instagram(url, download_path):
    loader = instaloader.Instaloader()

    if '/reel/' in url:
        try:
            reel_shortcode = url.split('/')[-2]
            reel = instaloader.Post.from_shortcode(loader.context, reel_shortcode)
            loader.download_post(reel, target=os.path.join(download_path, 'reels'))
        except Exception as e:
            print(Fore.RED + f"Error: {str(e)}" + Style.RESET_ALL)
    elif '/stories/' in url:
        try:
            user_id = url.split('/')[-1]
            profile = instaloader.Profile.from_username(loader.context, user_id)
            for story in loader.get_stories(user_ids=[profile.userid]):
                for item in story.get_items():
                    loader.download_storyitem(item, target=os.path.join(download_path, 'stories'))
        except Exception as e:
            print(Fore.RED + f"Error: {str(e)}" + Style.RESET_ALL)
    else:
        try:
            post_shortcode = url.split('/')[-2]
            post = instaloader.Post.from_shortcode(loader.context, post_shortcode)
            loader.download_post(post, target=os.path.join(download_path, 'posts'))
        except Exception as e:
            print(Fore.RED + f"Error: {str(e)}" + Style.RESET_ALL)

def detect_platform(url):
    if 'youtube.com' in url or 'youtu.be' in url:
        return "YouTube"
    elif 'tiktok.com' in url:
        return "TikTok"
    elif 'facebook.com' in url:
        return "Facebook"
    elif 'instagram.com' in url:
        return "Instagram"
    else:
        return None

def clear_console():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def main():
    clear_console()

    print(Fore.GREEN + "Welcome to the Social Media Downloader!\n")
    print(Fore.GREEN + "-------By 5komar-------\n")
    
    download_base_path = input(Fore.CYAN + "Enter the download path (or press Enter to use default 'downloads'): " + Style.RESET_ALL).strip()
    if not download_base_path:
        download_base_path = 'downloads'
    
    url = input(Fore.CYAN + "Enter the video URL: " + Style.RESET_ALL)
    platform = detect_platform(url)
    
    if not platform:
        print(Fore.RED + "Error: Unsupported URL. Please enter a URL from YouTube, TikTok, Facebook, or Instagram.")
        return
    
    print(Fore.YELLOW + f"\nDetected platform: {platform}\n")
    
    download_path = create_download_path(download_base_path, platform)

    file_type = input(Fore.CYAN + "Enter the file type (mp3/mp4): " + Style.RESET_ALL).lower()
    
    if platform == "YouTube" and file_type == "mp4":
        quality = input(Fore.CYAN + "Enter the quality (144p, 360p, 720p, 1080p): " + Style.RESET_ALL)
    else:
        quality = None

    print(Fore.MAGENTA + "\nStarting download...\n" + Style.RESET_ALL)

    try:
        if platform == "YouTube":
            download_youtube(url, file_type, quality, download_path)
        elif platform == "TikTok":
            download_tiktok(url, download_path)
        elif platform == "Facebook":
            download_facebook(url, download_path)
        elif platform == "Instagram":
            download_instagram(url, download_path)
    except Exception as e:
        print(Fore.RED + f"Error: {str(e)}" + Style.RESET_ALL)

if __name__ == "__main__":
    main()