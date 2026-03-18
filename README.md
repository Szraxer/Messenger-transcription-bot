# 🎙️ Messenger Voice Transcription Bot

A seamless integration bridging Facebook Messenger and Meta's Wit.ai Speech-to-Text model. Built with Python (Flask) and deployed locally via Ngrok, this bot automatically intercepts voice messages, processes the audio on the fly, and returns highly accurate transcriptions directly to the user's chat.

## 🧠 Architecture and Design Patterns

To ensure high performance, security, and stability, the project implements several specific engineering solutions:

### 1. In-Memory Audio Processing (Zero Disk I/O)
* **Problem:** Downloading audio attachments from Facebook to the local hard drive creates I/O bottlenecks, slows down response times, and requires complex cleanup mechanisms to avoid cluttering the server.
* **Solution:** The bot utilizes Python's `io.BytesIO`.
* **Action:** The audio payload is downloaded directly into a RAM buffer. The `pydub` library (powered by FFmpeg) reads this byte stream, converts the compressed AAC/MP4 file into a lossless WAV format, and holds it in memory. This ensures blazing-fast processing without leaving temporary file "trash" on the disk.

### 2. Regex-Based Stream Parsing
* **Problem:** Wit.ai's `/speech` endpoint returns chunked, streamed JSON responses. Instead of one clean JSON object, it sends multiple partial transcripts as the AI "listens" (e.g., {"text": "Hello"}, {"text": "Hello how"}, {"text": "Hello how are you"}). Native JSON parsers often fail on this streamed format.
* **Solution:** A custom Regular Expression parser (`re.findall(r'"text":\s*"(.*?)"', ...)`).
* **Action:** The script scans the raw text payload to extract all values tied to the `"text"` key, dynamically selecting the final array element (`results[-1]`), which always contains the most complete and accurate transcription.

### 3. Event-Driven Webhook Lifecycle
* **Mechanism:** The Flask application cleanly separates the Verification Handshake (`GET`) required by Meta's security protocols from the continuous Message Processing (`POST`). 
* **User Experience:** Upon receiving an audio attachment, the bot immediately sends a "Processing... 🎧" text back to the user. This provides instant UX feedback while the heavier FFmpeg conversion and Wit.ai API calls happen in the background.

## 🚀 Features
* **Meta Graph API Integration:** Fully compatible with Facebook Pages and Messenger infrastructure.
* **Format Optimization:** Automatically converts audio to 16kHz, mono WAV files—the optimal format recommended by Wit.ai for maximum transcription accuracy.
* **Secure Environment:** Sensitive credentials (Page Tokens, Verification Tokens) are strictly isolated using `python-dotenv` and ignored via `.gitignore`.
* **Graceful Error Handling:** Try-Except blocks ensure the Flask server never crashes due to malformed audio files or API timeouts.

## 🛠️ Requirements
* **Python 3.8+** (Anaconda recommended for dependency management)
* **Ngrok** (For localhost tunneling)
* **FFmpeg** (Required system-level audio processing engine)
* **Meta Developer Account** (For the Messenger App)
* **Wit.ai Account** (For the NLP Server Token)

## ⚙️ Installation Instructions

### Step 1: Clone & Install Dependencies
1. Clone this repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/messenger-transcription-bot.git](https://github.com/YOUR_USERNAME/messenger-transcription-bot.git)
   cd messenger-transcription-bot
