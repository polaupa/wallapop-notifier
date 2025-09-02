# Wallapop Notifier Bot

A Telegram bot that monitors Wallapop searches and notifies you of interesting new items, using AI for product analysis and Google Sheets for search configuration.

---

## Features

- **Wallapop Scraper:** Finds new items matching your criteria.
- **AI Analysis:** Uses LLMs to analyze and score products.
- **Google Sheets Integration:** Configure your searches in a spreadsheet.
- **Telegram Notifications:** Sends you alerts for interesting items.
- **Database Storage:** Keeps track of notified items to avoid duplicates.
- **Docker Support:** Easy deployment with Docker.

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/polaupa/wallapop-notifier.git
cd wallapop-notifier
```

### 2. Set Up Environment Variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` and set:

- `TELEGRAM_TOKEN` — Your Telegram bot token ([how to get one](https://core.telegram.org/bots/tutorial))
- `SPREADSHEET_ID` (Check Step 3)
- `SPREADSHEET_PUBLIC_URL_CSV` (Check Step 3)
- `DEEPSEEK_API_KEY` (Optional): https://platform.deepseek.com/api_keys
- `MISTRAL_API_KEY` (Optional - Free): https://console.mistral.ai/api-keys
- `GEMINI_API_KEY` (Optional - Free): https://aistudio.google.com/apikey
- `PERPLEXITY_API_KEY` (Optional): https://www.perplexity.ai/account/api/keys


\* Note that if you don't set AI, you won't have access to AI features, and you will only retrieve the Wallapop data - which works fine. 

### 3. Set Up Google Sheets

Create a Google Sheet following [this template](docs.google.com/spreadsheets/d/1vm6eRdxIq2JPVT1KsuNuspUZM1Ey6C78hI5mABtE-9s) (import it to your Google Drive).

You only have to do one of the following two options:

Option 1: Use Public URL (simpler, less secure)
- Make your Google Sheet public ([Google Instructions](https://support.google.com/docs/answer/183965?hl=en&co=GENIE.Platform%3DDesktop))
- Set the `SPREADSHEET_PUBLIC_URL_CSV` with the PUBLIC URL in `.env`

Option 2: Use Google API (more secure, more complex)
- Share your spreadsheet with your Google API service account ([Google Instructions](https://developers.google.com/workspace/guides/create-credentials?hl=es-419))
- Set the `credentials.json` in `google_utils/credentials.json` 
- Set the `SPREADSHEET_ID` in `.env` with your Google Sheets spreadsheet ID (it is the ID in the link of the docs.google.com/spreadsheets/d/**SPREADSHEET_ID**/edit?gid=0#gid=0)

### 4. Run the bot

#### Locally

```bash
pip install -r requirements.txt
python main.py
```

#### With Docker:

```bash
docker compose up --build -d
```

To get Telegram notifications, make sure your bot is running and you have sent the `/start` command to it.

---

## Usage

- Start your Telegram bot and send `/start` to it.
- The bot will prompt you for your chat ID and save it in `.env`.
- The bot will check your Google Sheet for searches and notify you of new interesting items.

---

## Stopping the Bot

If running with Docker. In the folder where `docker-compose.yaml` is located, run:

```bash
docker compose down
```

---

## Project Structure

```
.
├── wallapop/           # Main app logic (scraper, AI, etc)
├── google_utils/       # Google Sheets integration
├── telegram_utils/     # Telegram bot utilities
├── main.py             # Entry point
├── requirements.txt
├── docker-compose.yaml
├── Dockerfile
└── .env
```

---

## License

MIT

---

## Credits

Created by [polaupa](https://github.com/polaupa)
