# Language Detection Script

## Overview

This script is designed to help you determine what languages are being used on a computer. It analyzes various sources such as system settings, browser histories, and even gaming platforms like Steam to identify languages that might be in use, including those that are less obvious or "hidden".

## Features

- **Locale Detection**: Checks the system's locale settings to determine the primary language.
- **Keyboard Layouts**: Identifies all installed keyboard layouts on the system.
- **Browser Languages**: Extracts language settings from popular browsers like Firefox, Chrome, and Internet Explorer.
- **Browser History Analysis**: Analyzes browser history to identify languages based on visited non-.com domains.
- **Steam Language**: Detects the language settings in the Steam gaming platform.
- **Music Folder Analysis**: Scans the names of files and folders in the Music directory for clues about the user's language.

## Supported Platforms

- **Linux**: Fully tested and operational.
- **Windows**: Functionality implemented but requires additional testing.

## Usage

### Prerequisites

- Python 3.x
- Required Python libraries: `pycountry`

Install the necessary libraries using pip:

```bash
pip install pycountry
```

Run the script
```bash
python pimtel.py
```

Example output:

```bash
Firefox Languages:
Chrome Languages:
  - ru-RU
  - nl-NL
  - en
  - de
  - en-US
  - de-DE
  - es
  - nl
  - ru
  - es-US
Detected Languages in Music Folder:
  - Cyrillic x 1: Премьера.pm3
Installed Languages (Human-readable):
  - Dutch
  - Russian
  - German
  - English
  - Spanish
Firefox History (Non-.com URLs):
Chrome History (Non-.com URLs):
  - nl x 3905: educus.nl, nu.nl, google.nl
  - de x 51: immobilienscout24.de, immowelt.de, goethe.de
  - ru x 2: vk.ru, yandex.ru
  - be x 7: hln.be, standaard.be, youtu.be
  - etc.. etc.. etc..  
Operating System: Linux
Language Code: en_US
Current Keyboard Layout: us,us
```
## Interpertation of the results:

This person has multiple languages installed on their Chrome browser: Russian, English, German, Spanish, and Dutch. They do not seem to be using Firefox.

Their search history shows Dutch, German, Russian, and Belgian sites. You can alos see one song using Cyrillic ( The letters sometimes used in Belarusian, Bulgarian, Kazakh, Kyrgyz, Macedonian, Montenegrin, Russian, Serbian, Tajik, Turkmen, Ukrainian or Uzbek)

Note that in this example, the browser history has been significantly reduced. If someone has not cleared their history, the list can become very long. Some sites use a language domain for aesthetic reasons, which might catch you off guard. For example, YouTube uses youtu.be, even though this is not a Belgian site.


