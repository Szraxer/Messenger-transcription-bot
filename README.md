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
1. **Clone this repository:**
   ```bash
   git clone https://github.com/Szraxer/Messenger-transcription-bot.git
   cd messenger-transcription-bot
   ```
2. **Install Python packages:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install FFmpeg (Crucial!):**
   If using Anaconda, run:
   ```bash
   conda install -c conda-forge ffmpeg
   ```
   Otherwise, download it from the official site and add it to your System PATH.

### Step 2: Environment Configuration
Create a `.env` file in the root directory and populate it with your keys (refer to `.env.example`):
```text
PAGE_ACCESS_TOKEN=your_facebook_page_access_token
WIT_ACCESS_TOKEN=your_wit_ai_server_token
VERIFY_TOKEN=your_custom_webhook_verify_password
```

### Step 3: Run the Bot
1. **Start Ngrok:** Open a terminal and run `ngrok http 5000`. Copy the generated `https` Forwarding URL.
2. **Setup Meta Webhook:** Go to your Meta App Dashboard -> Messenger -> API Setup. Paste your Ngrok URL followed by `/webhook` (e.g., `https://abc-123.ngrok-free.app/webhook`) and enter your Verify Token.
3. **Start Flask:** Open another terminal and run `python app.py`.

## 🎮 How to Use?
* **Text the Bot:** Send a standard text message to your Facebook Page. The bot will reply with instructions.
* **Send a Voice Note:** Record and send a voice message. The bot will acknowledge receipt, process the audio, and reply with the `📝 Transcription`.

## 🐛 Troubleshooting

* **Error: `[WinError 2] Nie można odnaleźć określonego pliku` (File not found)**
  * *Cause:* `pydub` cannot find FFmpeg on your system.
  * *Fix:* Ensure FFmpeg is installed and correctly added to your system's PATH variables, or install it via your package manager (`conda install -c conda-forge ffmpeg`).
* **Facebook Webhook Verification Fails / Red Cross in Meta Dashboard**
  * *Cause:* Mismatch in `VERIFY_TOKEN` or your Flask server is not running.
  * *Fix:* Double-check your `.env` file and ensure `app.py` is actively running on port `5000` before clicking "Verify and Save" on Facebook.
* **Bot stops responding after a PC restart**
  * *Cause:* Ngrok free tier changes the URL every time it launches.
  * *Fix:* You must update the Callback URL in the Meta Developer portal with your new Ngrok link.
