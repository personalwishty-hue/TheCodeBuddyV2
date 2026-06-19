# Discord → Supabase Message Logger

A lightweight Discord bot that listens to specific channels and stores every
message in a Supabase `discord_messages` table.

---

## Project structure

```
discord_bot/
├── bot.py                  # Main bot code
├── supabase_migration.sql  # Run once in Supabase to create the table
├── requirements.txt
├── .env.example            # Template – copy to .env and fill in values
└── README.md
```

---

## 1 – Create the Supabase table

Open the **SQL Editor** in your Supabase dashboard and run the contents of
`supabase_migration.sql`. This creates:

| Column            | Type         | Notes                        |
|-------------------|--------------|------------------------------|
| `id`              | bigint (PK)  | Auto-generated identity      |
| `channel_name`    | text         | e.g. `"blox-fruits-codes"`   |
| `user_id`         | text         | Discord snowflake as string  |
| `message_content` | text         | Raw message body             |
| `timestamp`       | timestamptz  | UTC time of insertion        |

---

## 2 – Create the Discord bot

1. Go to <https://discord.com/developers/applications> and create a new application.
2. Under **Bot**, click **Add Bot** and copy the **Token** → `DISCORD_TOKEN`.
3. Enable the following **Privileged Gateway Intents**:
   - **Message Content Intent** ✅
   - **Server Members Intent** (optional)
4. Invite the bot to your server using the OAuth2 URL generator with the
   `bot` scope and `Read Messages / View Channels` + `Read Message History`
   permissions.

---

## 3 – Configure environment variables

```bash
cp .env.example .env
# Edit .env with your real values
```

**Never commit `.env` to version control.**  Add it to `.gitignore`:

```
.env
```

---

## 4 – Install dependencies & run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Load .env automatically (python-dotenv is already in requirements.txt)
python -c "from dotenv import load_dotenv; load_dotenv()"
# … or simply prefix the run command:
python -m dotenv run -- python bot.py
```

Or export vars manually:

```bash
export DISCORD_TOKEN=...
export SUPABASE_URL=...
export SUPABASE_KEY=...
export MONITORED_CHANNELS=general,blox-fruits-codes
python bot.py
```

---

## 5 – Extending the monitored channels

Edit `MONITORED_CHANNELS` in your `.env` file – no code change needed:

```
MONITORED_CHANNELS=general,blox-fruits-codes,announcements,trading
```

---

## Error handling

All Supabase insertion errors are caught and logged with full tracebacks:

```
2024-01-15 12:00:01 [ERROR] discord_bot: Failed to insert message into Supabase | channel=general | error=...
```

The bot continues running even if the database is temporarily unavailable.
