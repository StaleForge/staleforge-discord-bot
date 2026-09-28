import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
BOT_PREFIX = os.getenv("BOT_PREFIX", "!")
BOT_STATUS_TEXT = os.getenv("BOT_STATUS_TEXT", "staleforge.dev")
BOT_STATUS_URL = os.getenv("BOT_STATUS_URL", "https://staleforge.dev")

LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", "0"))
BOOST_CHANNEL_ID = int(os.getenv("BOOST_CHANNEL_ID", "0"))
ANNOUNCEMENT_CHANNEL_ID = int(os.getenv("ANNOUNCEMENT_CHANNEL_ID", "0"))
PROMOTION_CHANNEL_ID = int(os.getenv("PROMOTION_CHANNEL_ID", "0"))
POLL_CHANNEL_ID = int(os.getenv("POLL_CHANNEL_ID", "0"))
GIVEAWAY_CHANNEL_ID = int(os.getenv("GIVEAWAY_CHANNEL_ID", "0"))
RULES_CHANNEL_ID = int(os.getenv("RULES_CHANNEL_ID", "0"))
TICKET_ALERT_CHANNEL_ID = int(os.getenv("TICKET_ALERT_CHANNEL_ID", "0"))
AUTO_DELETE_CHANNEL_ID = int(os.getenv("AUTO_DELETE_CHANNEL_ID", "0"))
PRICING_CHANNEL_ID = int(os.getenv("PRICING_CHANNEL_ID", "0"))

STATS_MEMBERS_VC_ID = int(os.getenv("STATS_MEMBERS_VC_ID", "0"))
STATS_BANS_VC_ID = int(os.getenv("STATS_BANS_VC_ID", "0"))
STATS_LATEST_VC_ID = int(os.getenv("STATS_LATEST_VC_ID", "0"))

VERIFIED_ROLE_ID = int(os.getenv("VERIFIED_ROLE_ID", "0"))
MEMBER_ROLE_ID = int(os.getenv("MEMBER_ROLE_ID", "0"))

TICKET_STAFF_ROLE_IDS = [
    int(r.strip()) for r in os.getenv("TICKET_STAFF_ROLE_IDS", "0").split(",") if r.strip()
]
REROLL_ROLE_IDS = [
    int(r.strip()) for r in os.getenv("REROLL_ROLE_IDS", "0").split(",") if r.strip()
]
TICKET_LOG_CATEGORY_NAME = os.getenv("TICKET_LOG_CATEGORY_NAME", "TICKET LOGS")

FOOTER_TEXT = "made by staleforge ~2023"
