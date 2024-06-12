import platform
import locale
import subprocess
import pycountry
import os
import json
import re
import sqlite3
import shutil
import re

from country_tlds import country_language_tlds


def run_command(command):
    """
    Runs a shell command and returns the output.
    """
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL).decode().strip()
        return result if result else None
    except subprocess.CalledProcessError:
        return None

def get_windows_language():
    """
    Retrieve the default UI language for Windows.

    Returns:
        str: The language code.
    """
    import ctypes
    windll = ctypes.windll.kernel32
    lang_id = windll.GetUserDefaultUILanguage()
    lang_code = locale.windows_locale[lang_id]
    return lang_code

def get_windows_keyboard_layouts():
    """
    Retrieve the installed keyboard layouts for Windows.

    Returns:
        list: A list of installed keyboard layouts.
    """
    from winreg import OpenKey, EnumKey, QueryValueEx, HKEY_LOCAL_MACHINE

    layouts = []
    key = OpenKey(HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Keyboard Layouts')
    for i in range(0, 256):
        try:
            layout_key = EnumKey(key, i)
            with OpenKey(key, layout_key) as subkey:
                layout_text, _ = QueryValueEx(subkey, 'Layout Text')
                layouts.append(layout_text)
        except OSError:
            break

    return layouts

def get_linux_locale():
    """
    Retrieve the default locale for Linux.

    Returns:
        str: The language code.
    """
    return locale.getdefaultlocale()[0]

def get_linux_keyboard_layout():
    """
    Retrieve the current keyboard layout for Linux.

    Returns:
        str: The keyboard layout.
    """
    keyboard_layout = run_command("setxkbmap -query | grep layout")
    if keyboard_layout:
        return keyboard_layout.split(':')[1].strip()
    return "Unknown"

def get_linux_installed_languages():
    """
    Retrieve the installed languages for Linux.

    Returns:
        list: A list of installed languages.
    """
    installed_languages = run_command("locale -a")
    if installed_languages:
        return installed_languages.split('\n')
    return []

def get_human_readable_languages(language_codes):
    """
    Convert locale language codes to human-readable language names.

    Args:
        language_codes (list): List of locale language codes.

    Returns:
        list: List of human-readable language names.
    """
    human_readable_languages = set()
    for code in language_codes:
        lang = code.split('_')[0]  # Extract the language part
        try:
            language = pycountry.languages.get(alpha_2=lang)
            if language:
                human_readable_languages.add(language.name)
        except KeyError:
            continue
    return list(human_readable_languages)

def get_firefox_languages():
    """
    Retrieve the installed languages for Firefox.

    Returns:
        list: A list of installed languages.
    """
    firefox_profiles_path = os.path.expanduser("~/.mozilla/firefox")
    languages = set()
    
    if not os.path.exists(firefox_profiles_path):
        return []

    for profile in os.listdir(firefox_profiles_path):
        prefs_js_path = os.path.join(firefox_profiles_path, profile, "prefs.js")
        if os.path.isfile(prefs_js_path):
            with open(prefs_js_path, 'r') as prefs_js_file:
                for line in prefs_js_file:
                    if 'intl.accept_languages' in line:
                        lang_code = line.split('"')[1]
                        languages.update(lang_code.split(','))
    return list(languages)

def get_chrome_languages():
    """
    Retrieve the installed languages for Chrome.

    Returns:
        list: A list of installed languages.
    """
    chrome_profile_path = os.path.expanduser("~/.config/google-chrome")
    languages = set()

    if not os.path.exists(chrome_profile_path):
        return []

    for profile in os.listdir(chrome_profile_path):
        preferences_path = os.path.join(chrome_profile_path, profile, "Preferences")
        if os.path.isfile(preferences_path):
            with open(preferences_path, 'r') as preferences_file:
                try:
                    preferences = json.load(preferences_file)
                    language = preferences.get('intl', {}).get('accept_languages', '')
                    if language:
                        languages.update(language.split(','))
                except json.JSONDecodeError:
                    continue
    return list(languages)

def get_ie_languages():
    """
    Retrieve the installed languages for Internet Explorer.

    Returns:
        list: A list of installed languages.
    """
    from winreg import OpenKey, EnumValue, HKEY_CURRENT_USER
    languages = []
    try:
        with OpenKey(HKEY_CURRENT_USER, r'Software\Microsoft\Internet Explorer\International\AcceptLanguage') as key:
            i = 0
            while True:
                try:
                    languages.append(EnumValue(key, i)[1])
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        pass
    return languages

def get_steam_language(os_name):
    """
    Retrieve the Steam language setting from the configuration file.

    Args:
        os_name (str): The operating system name.

    Returns:
        str: The Steam language code.
    """
    steam_config_path = ""

    if os_name == "Windows":
        steam_config_path = os.path.expandvars(r'%ProgramFiles(x86)%\Steam\config\config.vdf')
    elif os_name == "Linux":
        steam_config_path = os.path.expanduser('~/.steam/steam/config/config.vdf')
        if not os.path.exists(steam_config_path):
            steam_config_path = os.path.expanduser('~/.local/share/Steam/config/config.vdf')
    else:
        return None

    if not os.path.exists(steam_config_path):
        return None

    with open(steam_config_path, 'r', encoding='utf-8') as file:
        config_content = file.read()

    language_match = re.search(r'"Language"\s+"(\w+)"', config_content)
    if language_match:
        return language_match.group(1)
    else:
        return None

from collections import defaultdict, Counter

from collections import defaultdict, Counter
from urllib.parse import urlparse

def get_base_domain(url):
    """
    Extract the base domain from a full URL.
    
    Args:
        url (str): The full URL.
        
    Returns:
        str: The base domain.
    """
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split('.')
    if len(domain_parts) > 2:
        base_domain = '.'.join(domain_parts[-2:])
    else:
        base_domain = parsed_url.netloc
    return base_domain

def get_tld_from_domain(domain):
    """
    Extract the TLD from a base domain.
    
    Args:
        domain (str): The base domain.
        
    Returns:
        str: The TLD.
    """
    return domain.split('.')[-1]

def filter_non_com_urls(history_entries):
    """
    Filters history entries to only include non-.com country and language-related URLs,
    counts the occurrences of each TLD, and records the most common base URLs.

    Args:
        history_entries (list): List of dictionaries with history entries.

    Returns:
        dict: Dictionary with TLDs as keys and another dictionary as values, 
              containing the count and most common base URLs.
    """
    tld_data = defaultdict(lambda: {"count": 0, "urls": []})

    for entry in history_entries:
        base_domain = get_base_domain(entry['url'])
        tld = get_tld_from_domain(base_domain)
        if tld in country_language_tlds:
            tld_data[tld]["count"] += 1
            tld_data[tld]["urls"].append(base_domain)

    # Keep only the 3 most common base URLs for each TLD
    for tld, data in tld_data.items():
        url_counts = Counter(data["urls"])
        most_common_urls = [url for url, _ in url_counts.most_common(3)]
        tld_data[tld]["urls"] = most_common_urls

    return tld_data



def get_ie_history():
    """
    Retrieve search history from Internet Explorer.

    Returns:
        list: A list of search history entries.
    """
    from winreg import OpenKey, EnumValue, HKEY_CURRENT_USER
    history_entries = []

    def read_ie_history(key):
        try:
            with OpenKey(HKEY_CURRENT_USER, key) as regkey:
                i = 0
                while True:
                    try:
                        name, value, _ = EnumValue(regkey, i)
                        if name.startswith("url"):
                            history_entries.append({
                                "url": value,
                                "title": "",
                                "visit_date": ""
                            })
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            pass

    ie_history_keys = [
        r"Software\Microsoft\Internet Explorer\TypedURLs",
        r"Software\Microsoft\Internet Explorer\TypedURLsTime"
    ]

    for key in ie_history_keys:
        read_ie_history(key)

    return filter_non_com_urls(history_entries)

def print_windows_settings():
    """
    Print language and keyboard settings for Windows.
    """
    lang_code = get_windows_language()
    keyboard_layouts = get_windows_keyboard_layouts()
    installed_languages = [lang_code]
    ie_languages = get_ie_languages()
    steam_language = get_steam_language("Windows")

    print(f"Operating System: Windows")
    print(f"Language Code: {lang_code}")
    print("Installed Keyboard Layouts:")
    for layout in keyboard_layouts:
        print(f"  - {layout}")
    print("Internet Explorer Languages:")
    for lang in ie_languages:
        print(f"  - {lang}")
    if steam_language:
        print(f"Steam Language: {steam_language}")

    # check music
    print_music_folder_analysis("Linux")   

    human_readable_languages = get_human_readable_languages(installed_languages + ie_languages + ([steam_language] if steam_language else []))
    print("Installed Languages (Human-readable):")
    for language in human_readable_languages:
        print(f"  - {language}")

    print("Internet Explorer History (Non-.com URLs):")
    ie_history = get_ie_history()
    for entry in ie_history:
        print(f"  - {entry['url']}")

def print_linux_settings():
    """
    Print language and keyboard settings for Linux.
    """
    lang_code = get_linux_locale()
    keyboard_layout = get_linux_keyboard_layout()
    installed_languages = get_linux_installed_languages()
    firefox_languages = get_firefox_languages()
    chrome_languages = get_chrome_languages()
    steam_language = get_steam_language("Linux")

    # print the languages installed in chrome and firefox
    print("Firefox Languages:")
    for lang in firefox_languages:
        print(f"  - {lang}")
    print("Chrome Languages:")
    for lang in chrome_languages:
        print(f"  - {lang}")

    # print the language found in steam, this one requeres more testing.
    if steam_language:
        print(f"Steam Language: {steam_language}")


     # check music
    print_music_folder_analysis("Linux")   

    # retrieve the language codes and make them human readable
    human_readable_languages = get_human_readable_languages(installed_languages + firefox_languages + chrome_languages + ([steam_language] if steam_language else []))
    print("Installed Languages (Human-readable):")
    for language in human_readable_languages:
        print(f"  - {language}")

    # print the non .com urls with 3 examples from search history
    print("Firefox History (Non-.com URLs):")
    firefox_history_data = get_firefox_history()
    for tld, data in firefox_history_data.items():
        print(f"  - {tld} x {data['count']}: {', '.join(data['urls'])}")

    # print the non .com urls with 3 examples from search history
    print("Chrome History (Non-.com URLs):")
    chrome_history_data = get_chrome_history()
    for tld, data in chrome_history_data.items():
        print(f"  - {tld} x {data['count']}: {', '.join(data['urls'])}")

    # print general infromation, such as the main installed language and keyboard languages installed
    print(f"Operating System: Linux")
    print(f"Language Code: {lang_code}")
    print(f"Current Keyboard Layout: {keyboard_layout}") 
 


def get_firefox_history():
    """
    Retrieve search history from Firefox and count TLD occurrences.

    Returns:
        dict: Dictionary with TLDs as keys and another dictionary as values, 
              containing the count and most common base URLs.
    """
    firefox_profiles_path = os.path.expanduser("~/.mozilla/firefox")
    history_entries = []

    if not os.path.exists(firefox_profiles_path):
        return {}

    for profile in os.listdir(firefox_profiles_path):
        places_db_path = os.path.join(firefox_profiles_path, profile, "places.sqlite")
        if os.path.isfile(places_db_path):
            conn = sqlite3.connect(places_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, visit_date FROM moz_places, moz_historyvisits WHERE moz_places.id = moz_historyvisits.place_id")
            for row in cursor.fetchall():
                history_entries.append({
                    "url": row[0],
                    "title": row[1],
                    "visit_date": row[2]
                })
            conn.close()
    return filter_non_com_urls(history_entries)

def get_chrome_history():
    """
    Retrieve search history from Chrome and count TLD occurrences.

    Returns:
        dict: Dictionary with TLDs as keys and another dictionary as values, 
              containing the count and most common base URLs.
    """
    chrome_profile_path = os.path.expanduser("~/.config/google-chrome/Default")
    history_db_path = os.path.join(chrome_profile_path, "History")
    history_entries = []

    if not os.path.isfile(history_db_path):
        return {}

    shutil.copy2(history_db_path, "/tmp/History")  # Chrome locks the file, so copy it
    conn = sqlite3.connect("/tmp/History")
    cursor = conn.cursor()
    cursor.execute("SELECT url, title, last_visit_time FROM urls")
    for row in cursor.fetchall():
        history_entries.append({
            "url": row[0],
            "title": row[1],
            "visit_date": row[2]
        })
    conn.close()
    os.remove("/tmp/History")
    return filter_non_com_urls(history_entries)



def detect_language_in_text(text):
    """
    Detects the presence of specific language scripts in a given text.

    Args:
        text (str): The text to analyze.

    Returns:
        list: A list of detected languages based on scripts.
    """
    scripts = {
        'Cyrillic': re.compile(r'[\u0400-\u04FF]'),
        'Arabic': re.compile(r'[\u0600-\u06FF]'),
        'Chinese': re.compile(r'[\u4E00-\u9FFF]'),
        'Greek': re.compile(r'[\u0370-\u03FF]'),
        'Hebrew': re.compile(r'[\u0590-\u05FF]'),
        'Devanagari': re.compile(r'[\u0900-\u097F]'),
        'Thai': re.compile(r'[\u0E00-\u0E7F]'),
        'Hangul': re.compile(r'[\uAC00-\uD7AF]')
    }
    
    detected_languages = []
    
    for language, pattern in scripts.items():
        if pattern.search(text):
            detected_languages.append(language)
    
    return detected_languages


def print_music_folder_analysis(os_name):
    """
    Print analysis of the Music folder for potential language usage.
    """
    if os_name == "Windows":
        music_folder = os.path.expandvars(r'%USERPROFILE%\Music')
    else:  # Assuming Linux
        music_folder = os.path.expanduser("~/Music")

    music_languages = scan_music_folder(music_folder)
    print("Detected Languages in Music Folder:")
    for language, data in music_languages.items():
        examples = ', '.join(data["examples"])
        print(f"  - {language} x {data['count']}: {examples}")


def scan_music_folder(folder_path):
    """
    Scans the Music folder for file and folder names to gather clues about the user's language.

    Args:
        folder_path (str): The path to the Music folder.

    Returns:
        dict: A dictionary with detected languages, their counts, and example files.
    """
    detected_languages = defaultdict(lambda: {"count": 0, "examples": []})
    
    if not os.path.exists(folder_path):
        return detected_languages

    for root, dirs, files in os.walk(folder_path):
        for name in dirs + files:
            languages = detect_language_in_text(name)
            for language in languages:
                detected_languages[language]["count"] += 1
                if len(detected_languages[language]["examples"]) < 3:
                    detected_languages[language]["examples"].append(name)
    
    return detected_languages






def main():
    """
    Main function to determine the OS and retrieve language settings and keyboard layouts.
    """
    os_name = platform.system()
    if os_name == "Windows":
        print_windows_settings()
    elif os_name == "Linux":
        print_linux_settings()
    else:
        print(f"Unsupported Operating System: {os_name}")

if __name__ == "__main__":
    main()
