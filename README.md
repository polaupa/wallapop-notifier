# Wallapop Notifier Bot

A Telegram bot that monitors Wallapop searches and notifies you of interesting new items, using AI for product analysis and Google Sheets for search configuration.

---

## Features

- **Wallapop Scraper:** Finds new items matching your criteria.
- **AI Analysis:** Uses LLMs to analyze and score products.
- **Google Sheets Integration:** Configure your searches in a spreadsheet.
- **Telegram Notifications:** Sends you alerts for interesting items.

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
- `SPREADSHEET_ID` — Your Google Sheets spreadsheet ID (It is the ID in the link of the docs.google.com/spreadsheets/d/**SPREADSHEET_ID**/edit?gid=0#gid=0)
- `SPREADSHEET_PUBLIC_URL_CSV` (You have to make your spreadsheet public or to set up Google Sheets - Step 3) - Your CSV public URL ([how to get one](https://support.google.com/docs/answer/183965?hl=en&co=GENIE.Platform%3DDesktop))
- `AI_MODEL_API_KEY` — (Optional) API key for your AI model
- `AI_MODEL` — (Optional) Model name. At this moment accepts:
    - `deepseek-chat`: https://platform.deepseek.com/api_keys
    - `sonar`, `r1-1776`: https://www.perplexity.ai/account/api/keys
    - `mistral-large-2411`, `mistral-large-latest`, `mistral-medium-2505`, `magistral-medium-2506`
    - `gemini-2.5-pro`: https://aistudio.google.com/apikey -> This is free!

- \* Note that if you don't set AI, you won't have access to AI features, and you will only retrieve the Wallapop data - which works fine. 

### 3. Set Up Google Sheets

- Share your spreadsheet with your Google API service account ([Google Instructions](https://developers.google.com/workspace/guides/create-credentials?hl=es-419))
- Set the `credentials.json` in `google_utils/credentials.json` 
- The spreadsheet should have this format:

| MIN_PRICE | MAX_PRICE | ITEM      | LONGITUDE | LATITUDE | DISTANCE | PROMPT |
|-----------|-----------|-----------|-----------|----------|----------|--------|
| -         | -         | item_name | -         | -        | -        | -      |
- The only mandatory item is `ITEM`.
- If you don't want to configure `MIN_PRICE`, `MAX_PRICE`, `LONGITUDE`, `LATITUDE`, `DISTANCE`, `PROMPT`: Just put a  `-`
LO
### 4. Run the bot

#### Locally

```bash
pip install -r requirements.txt
python main.py
```

#### With Docker:

```bash
docker-compose up --build -d
```

---

## Usage

- Start your Telegram bot and send `/start` to it.
- The bot will prompt you for your chat ID and save it in `.env`.
- The bot will check your Google Sheet for searches and notify you of new interesting items.

---

## Stopping the Bot

If running with Docker:

```bash
docker kill wallapop-wallapop-1
docker rm wallapop-wallapop-1
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
└── .env.example
```

---

## License

MIT

---

## Credits

Created by [polaupa](https://github.com/polaupa)
