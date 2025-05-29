import os
import json
import logging
import requests
from flask import jsonify
from datetime import datetime, timedelta
from prediction_service import PredictionService
from slot_game_service import SlotGameService
from language_service import LanguageService

logger = logging.getLogger(__name__)


class TelegramBotHandler:

    def __init__(self):
        """Initialize the Telegram bot handler."""
        self.telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not self.telegram_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN environment variable is not set")

        self.telegram_api_url = f"https://api.telegram.org/bot{self.telegram_token}"

        # Initialize services
        self.prediction_service = PredictionService()
        self.slot_game_service = SlotGameService()
        self.language_service = LanguageService()

        # Get either the provided WEBHOOK_URL or use the Replit domain
        webhook_url = os.environ.get("WEBHOOK_URL")
        if not webhook_url:
            # Use the Replit domain as webhook URL
            replit_domain = os.environ.get("REPLIT_DOMAINS")
            if replit_domain:
                webhook_url = f"https://{replit_domain}"
                logger.info(
                    f"Using Replit domain as webhook URL: {webhook_url}")

        # Set the webhook if we have a URL
        if webhook_url:
            self.set_webhook(webhook_url)

    def set_webhook(self, webhook_url):
        """Set the webhook for the Telegram bot."""
        url = f"{self.telegram_api_url}/setWebhook"
        data = {"url": f"{webhook_url}/webhook"}
        response = requests.post(url, data=data)
        logger.info(f"Webhook setup response: {response.json()}")

    def handle_update(self, update):
        """Process incoming updates from Telegram."""
        if 'message' in update:
            return self.handle_message(update['message'])
        elif 'callback_query' in update:
            return self.handle_callback_query(update['callback_query'])
        return jsonify({"status": "success", "message": "No action required"})

    def handle_message(self, message):
        """Process incoming messages from Telegram."""
        chat_id = message.get('chat', {}).get('id')
        if not chat_id:
            return jsonify({"status": "error", "message": "No chat ID found"})

        # Get user information
        user_id = message.get('from', {}).get('id')
        
        # Get user's preferred language
        language_code = self.language_service.get_user_language(user_id)

        # Check if this is a command
        text = message.get('text', '')
        if text.startswith('/'):
            return self.handle_command(chat_id, text, user_id)

        # For other messages, respond with help text in the appropriate language
        help_text = self.language_service.get_text("help_message", language_code)

        # Create inline keyboard for promotion and betting
        keyboard = {
            "inline_keyboard": [[{
                "text": "🎁 Khuyến mãi",
                "url": "https://nova88bet.top"
            }, {
                "text": "🎲 Đặt cược ngay",
                "url": "https://nova88bet.top"
            }], [{
                "text": "🎮 Slots RTP",
                "url": "https://nova88bet.top"
            }]]
        }

        self.send_message(chat_id, help_text, keyboard)
        return jsonify({"status": "success"})

    def handle_command(self, chat_id, command, user_id):
        """Process commands from users."""
        # Get user's preferred language
        language_code = self.language_service.get_user_language(user_id)
        
        # Standard promotion and betting keyboard with translated buttons
        promo_keyboard = {
            "inline_keyboard": [[{
                "text": self.language_service.get_text("promotion_button", language_code),
                "url": "https://nova88bet.top"
            }, {
                "text": self.language_service.get_text("bet_now_button", language_code),
                "url": "https://nova88bet.top"
            }], [{
                "text": self.language_service.get_text("slots_rtp_button", language_code),
                "url": "https://nova88bet.top"
            }]]
        }

        # Slot games keyboard with additional jackpot button (translated)
        slot_keyboard = {
            "inline_keyboard": [[{
                "text": self.language_service.get_text("promotion_button", language_code),
                "url": "https://nova88bet.top"
            }, {
                "text": self.language_service.get_text("bet_now_button", language_code),
                "url": "https://nova88bet.top"
            }], [{
                "text": self.language_service.get_text("slots_rtp_button", language_code),
                "url": "https://nova88bet.top"
            }]]
        }

        # Welcome message for /start command
        if command.startswith('/start'):
            # Send multi-language selection prompt first
            language_selection_text = """
👋 <b>Please choose your language / Vui lòng chọn ngôn ngữ / 请选择语言 / กรุณาเลือกภาษา</b>
"""
            # Create language selection keyboard
            language_keyboard = {
                "inline_keyboard": [[
                    {"text": "🇻🇳 Tiếng Việt", "callback_data": "lang_vi"},
                    {"text": "🇬🇧 English", "callback_data": "lang_en"}
                ], [
                    {"text": "🇨🇳 中文（简体）", "callback_data": "lang_zh"},
                    {"text": "🇹🇭 ภาษาไทย", "callback_data": "lang_th"}
                ]]
            }
            
            # Send language selection message
            self.send_message(chat_id, language_selection_text, language_keyboard)
            
            # Log the start command
            logger.info(f"User {user_id} started the bot and was prompted to select a language")
            
            return jsonify({"status": "success"})

        # Command for Vietnam lottery prediction - must check exact match or it will capture all du_doan variants
        elif command == '/du_doan':
            # Log which lottery type we're generating
            logger.info("Generating Vietnam lottery prediction")
            
            # Get today's Vietnam prediction in the user's language
            prediction = self.prediction_service.get_daily_prediction('vietnam', language_code)

            # Send the prediction with the inline keyboard
            self.send_message(chat_id, prediction, promo_keyboard)
            return jsonify({"status": "success"})
            
        # Command for 4D (Singapore/Malaysia) lottery prediction
        elif command.startswith('/du_doan_4d'):
            # Log which lottery type we're generating
            logger.info("Generating 4D lottery prediction")
            
            # Get today's 4D prediction in the user's language
            prediction = self.prediction_service.get_daily_prediction('4d', language_code)

            # Send the prediction with the inline keyboard
            self.send_message(chat_id, prediction, promo_keyboard)
            return jsonify({"status": "success"})
            
        # Command for Thai lottery prediction
        elif command.startswith('/du_doan_thai'):
            # Log which lottery type we're generating
            logger.info("Generating Thai lottery prediction")
            
            # Get today's Thai lottery prediction in the user's language
            prediction = self.prediction_service.get_daily_prediction('thai', language_code)

            # Send the prediction with the inline keyboard
            self.send_message(chat_id, prediction, promo_keyboard)
            return jsonify({"status": "success"})
            
        # Command for Indonesian lottery prediction
        elif command.startswith('/du_doan_indo'):
            # Log which lottery type we're generating
            logger.info("Generating Indonesian lottery prediction")
            
            # Get today's Indonesian lottery prediction in the user's language
            prediction = self.prediction_service.get_daily_prediction('indo', language_code)

            # Send the prediction with the inline keyboard
            self.send_message(chat_id, prediction, promo_keyboard)
            return jsonify({"status": "success"})

        # Command to list all PGSoft slot games
        elif command.startswith('/ds_slot'):
            # Get the list of popular games in the user's language
            result = self.slot_game_service.get_popular_games_list(language_code)
            
            # Check if we have a dict result (new format) or string (old format)
            if isinstance(result, dict):
                games_list = result.get('text', '')
            else:
                games_list = result
                
            self.send_message(chat_id, games_list, slot_keyboard)
            return jsonify({"status": "success"})

        # Command to get information about a specific slot game
        elif command.startswith('/slotgame'):
            # Extract the game name from the command
            parts = command.split(' ', 1)
            if len(parts) < 2:
                # Get error message in user's language
                help_text = self.language_service.get_text("slot_game_error", language_code)
                if not help_text or help_text == "slot_game_error":
                    # Fallback if translation is missing
                    if language_code == 'en':
                        help_text = "Please enter the game name after the /slotgame command. Example: /slotgame Mahjong Ways 2"
                    elif language_code == 'th':
                        help_text = "กรุณาป้อนชื่อเกมหลังคำสั่ง /slotgame ตัวอย่าง: /slotgame Mahjong Ways 2"
                    elif language_code == 'zh':
                        help_text = "请在 /slotgame 命令后输入游戏名称。示例：/slotgame Mahjong Ways 2"
                    else:
                        help_text = "Vui lòng nhập tên game sau lệnh /slotgame. Ví dụ: /slotgame Mahjong Ways 2"
                
                self.send_message(chat_id, help_text)
                return jsonify({"status": "success"})

            game_name = parts[1].strip()
            # Get game info in the user's language
            logger.info(f"Getting slot game info for {game_name} in {language_code}")
            result = self.slot_game_service.get_game_info(game_name, language_code)
            
            # Check if we have a dict result (new format) with image URL
            if isinstance(result, dict):
                full_text = result.get('text', '')
                image_url = result.get('image_url')
                
                # If we have an image URL, send as photo with a brief caption, then send full text
                if image_url:
                    try:
                        # Extract just the first paragraph for the short caption to avoid Telegram's 1024 char limit
                        # Find name and RTP for the short caption
                        import re
                        
                        # Try to extract RTP from the text
                        rtp_match = re.search(r'RTP: ([0-9.]+%|N/A)', full_text)
                        rtp_text = f"RTP: {rtp_match.group(1)}" if rtp_match else ""
                        
                        # Create a short caption that won't exceed Telegram's limits
                        short_caption = f"<b>{game_name}</b>\n{rtp_text}"
                        
                        # First send the image with short caption
                        self.send_photo(chat_id, image_url, short_caption, slot_keyboard)
                        
                        # Then send the full text as a separate message
                        self.send_message(chat_id, full_text, slot_keyboard)
                    except Exception as e:
                        logger.error(f"Failed to send game image: {e}")
                        # Fallback to text-only if sending photo fails
                        self.send_message(chat_id, full_text, slot_keyboard)
                else:
                    # No image, just send text
                    self.send_message(chat_id, full_text, slot_keyboard)
            else:
                # Old format, just text
                self.send_message(chat_id, result, slot_keyboard)
                
            return jsonify({"status": "success"})

        # Handle help command
        elif command.startswith('/help'):
            help_text = self.language_service.get_text("help_message", language_code)
            self.send_message(chat_id, help_text, promo_keyboard)
            return jsonify({"status": "success"})
            
        # Handle language selection command
        elif command.startswith('/language'):
            language_selection_text = self.language_service.get_text("language_selection", language_code)
            language_keyboard = self.language_service.get_language_selection_keyboard()
            self.send_message(chat_id, language_selection_text, language_keyboard)
            return jsonify({"status": "success"})

        # Handle unknown commands
        unknown_command_text = self.language_service.get_text("command_not_recognized", language_code)
        self.send_message(chat_id, unknown_command_text)
        return jsonify({"status": "success"})

    def handle_callback_query(self, callback_query):
        """Handle callback queries from inline buttons."""
        # Extract necessary information
        callback_id = callback_query.get('id')
        callback_data = callback_query.get('data', '')
        chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
        user_id = callback_query.get('from', {}).get('id')
        
        logger.info(f"Received callback query: {callback_data} from user {user_id}")
        
        # Language selection callback
        if callback_data and callback_data.startswith('lang_'):
            # Extract language code
            language_code = callback_data.split('_')[1]
            
            # Update user's language preference
            self.language_service.set_user_language(user_id, language_code)
            
            # Get the language name to display in the confirmation message
            language_name = self.language_service.get_language_name(language_code)
            
            # Get confirmation message template and format it with the language name
            confirmation_template = self.language_service.get_text("language_updated", language_code)
            confirmation_message = confirmation_template.replace("{language}", language_name)
            
            # Send confirmation message
            self.send_message(chat_id, confirmation_message)
            
            # Send welcome message in the selected language
            # Nova88 promo banner image URL
            nova88_banner_url = "https://nova88bet.top/wp-content/uploads/2025/05/photo_2025-05-08_15-19-02.jpg"
            
            # Create welcome keyboard with translated buttons
            welcome_keyboard = {
                "inline_keyboard": [[{
                    "text": self.language_service.get_text("promotion_button", language_code),
                    "url": "https://nova88bet.top"
                }, {
                    "text": self.language_service.get_text("bet_now_button", language_code),
                    "url": "https://nova88bet.top"
                }], [{
                    "text": self.language_service.get_text("jackpot_button", language_code),
                    "url": "https://nova88bet.top"
                }]]
            }
            
            # Get welcome caption and message in selected language
            short_caption = self.language_service.get_text("welcome_caption", language_code)
            full_welcome_message = self.language_service.get_text("welcome_message", language_code)
            
            try:
                # Send image with short caption
                self.send_photo(chat_id, nova88_banner_url, short_caption, welcome_keyboard)
                
                # Then send full welcome message
                self.send_message(chat_id, full_welcome_message, welcome_keyboard)
            except Exception as e:
                logger.error(f"Failed to send welcome photo: {e}")
                # If photo fails, just send the full text
                self.send_message(chat_id, full_welcome_message, welcome_keyboard)
            
            # Acknowledge the callback query
            if callback_id:
                url = f"{self.telegram_api_url}/answerCallbackQuery"
                data = {"callback_query_id": callback_id}
                requests.post(url, data=data)
            
            return jsonify({"status": "success", "message": f"Language set to {language_code}"})
        
        # For other callbacks, just acknowledge to stop the loading indicator
        if callback_id:
            url = f"{self.telegram_api_url}/answerCallbackQuery"
            data = {"callback_query_id": callback_id}
            requests.post(url, data=data)

        return jsonify({"status": "success"})

    def send_message(self, chat_id, text, reply_markup=None):
        """Send a message to a Telegram chat."""
        url = f"{self.telegram_api_url}/sendMessage"
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)

        try:
            response = requests.post(url, data=data)
            response_json = response.json()
            if not response_json.get('ok'):
                logger.error(f"Failed to send message: {response_json}")
            return response_json
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {"ok": False, "error": str(e)}

    def send_photo(self, chat_id, photo_url, caption=None, reply_markup=None):
        """Send a photo to a Telegram chat."""
        url = f"{self.telegram_api_url}/sendPhoto"
        data = {
            "chat_id": chat_id,
            "photo": photo_url,
        }

        if caption:
            data["caption"] = caption
            data["parse_mode"] = "HTML"

        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)

        try:
            response = requests.post(url, data=data)
            response_json = response.json()
            if not response_json.get('ok'):
                logger.error(f"Failed to send photo: {response_json}")
            return response_json
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            return {"ok": False, "error": str(e)}
