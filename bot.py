import os
import logging
from datetime import datetime, timezone

import discord
from supabase import create_client, Client

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("discord_bot")

# ── Environment variables ─────────────────────────────────────────────────────
SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]
DISCORD_TOKEN: str = os.environ["DISCORD_TOKEN"]

# Comma-separated list of channel names to monitor, e.g.:
#   MONITORED_CHANNELS=general,blox-fruits-codes,announcements
_raw_channels = os.getenv("MONITORED_CHANNELS", "general")
MONITORED_CHANNELS: set[str] = {
    ch.strip().lower() for ch in _raw_channels.split(",") if ch.strip()
}

# ── Supabase client ───────────────────────────────────────────────────────────
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Discord client ────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True          # Required to read message bodies
intents.messages = True

client = discord.Client(intents=intents)


# ── Events ────────────────────────────────────────────────────────────────────
@client.event
async def on_ready() -> None:
    log.info("Logged in as %s (ID: %s)", client.user, client.user.id)
    log.info("Monitoring channels: %s", MONITORED_CHANNELS)


@client.event
async def on_message(message: discord.Message) -> None:
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Only process messages from monitored channels
    channel_name: str = message.channel.name.lower()
    if channel_name not in MONITORED_CHANNELS:
        return

    log.info(
        "Message received | channel=%s | author_id=%s | content_length=%d",
        channel_name,
        message.author.id,
        len(message.content),
    )

    # ── Save to Supabase ──────────────────────────────────────────────────────
    payload = {
        "channel_name": channel_name,
        "user_id": str(message.author.id),
        "message_content": message.content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        response = (
            supabase.table("discord_messages")
            .insert(payload)
            .execute()
        )
        log.info("Inserted row(s): %s", response.data)
    except Exception as exc:
        log.error(
            "Failed to insert message into Supabase | channel=%s | error=%s",
            channel_name,
            exc,
            exc_info=True,
        )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    client.run(DISCORD_TOKEN, log_handler=None)   # We manage logging ourselves
