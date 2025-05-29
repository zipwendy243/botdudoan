import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LanguageService:
    """Service for handling multilingual support in the Telegram bot."""
    
    # Available languages
    VIETNAMESE = 'vi'
    ENGLISH = 'en'
    THAI = 'th'
    CHINESE = 'zh'
    
    # Default language
    DEFAULT_LANGUAGE = VIETNAMESE
    
    def __init__(self):
        """Initialize the language service."""
        # Dictionary to store user language preferences: {user_id: language_code}
        self.user_languages = {}
        
        # Load language data from file if it exists
        self.data_file = 'user_languages.json'
        self._load_user_languages()
        
        # Load translations
        self.translations = {
            self.VIETNAMESE: self._load_translations(self.VIETNAMESE),
            self.ENGLISH: self._load_translations(self.ENGLISH),
            self.THAI: self._load_translations(self.THAI),
            self.CHINESE: self._load_translations(self.CHINESE)
        }
        
        logger.info(f"Language service initialized with {len(self.translations)} languages")
    
    def _load_user_languages(self):
        """Load user language preferences from file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.user_languages = json.load(f)
                logger.info(f"Loaded language preferences for {len(self.user_languages)} users")
            else:
                logger.info("No existing language preferences file found")
        except Exception as e:
            logger.error(f"Error loading user languages: {e}")
    
    def _save_user_languages(self):
        """Save user language preferences to file."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_languages, f)
            logger.info(f"Saved language preferences for {len(self.user_languages)} users")
        except Exception as e:
            logger.error(f"Error saving user languages: {e}")
    
    def _load_translations(self, language_code):
        """Load translations for a specific language."""
        try:
            translations_file = f'translations_{language_code}.json'
            if os.path.exists(translations_file):
                with open(translations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # If no translation file exists, create a basic structure
                logger.warning(f"No translation file found for {language_code}, creating default structure")
                return {}
        except Exception as e:
            logger.error(f"Error loading translations for {language_code}: {e}")
            return {}
    
    def get_user_language(self, user_id):
        """
        Get the preferred language for a user.
        
        Args:
            user_id (int): The Telegram user ID
            
        Returns:
            str: The language code (vi, en, th, zh)
        """
        # Convert user_id to string for JSON serialization
        user_id = str(user_id)
        return self.user_languages.get(user_id, self.DEFAULT_LANGUAGE)
    
    def set_user_language(self, user_id, language_code):
        """
        Set the preferred language for a user.
        
        Args:
            user_id (int): The Telegram user ID
            language_code (str): The language code to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        if language_code not in [self.VIETNAMESE, self.ENGLISH, self.THAI, self.CHINESE]:
            logger.warning(f"Invalid language code: {language_code}")
            return False
        
        # Convert user_id to string for JSON serialization
        user_id = str(user_id)
        self.user_languages[user_id] = language_code
        self._save_user_languages()
        return True
    
    def get_text(self, key, language_code=None):
        """
        Get translated text for a specific key and language.
        
        Args:
            key (str): The translation key
            language_code (str): The language code (defaults to Vietnamese)
            
        Returns:
            str: The translated text or the key itself if not found
        """
        if not language_code:
            language_code = self.DEFAULT_LANGUAGE
            
        # Try to get translation in the requested language
        translations = self.translations.get(language_code, {})
        if key in translations:
            return translations[key]
        
        # If not found and not using default language, try default language
        if language_code != self.DEFAULT_LANGUAGE:
            logger.warning(f"Translation key '{key}' not found in {language_code}, trying default language")
            default_translations = self.translations.get(self.DEFAULT_LANGUAGE, {})
            if key in default_translations:
                return default_translations[key]
        
        # If still not found, return the key itself
        logger.warning(f"Translation key '{key}' not found in any language")
        return key
    
    def get_language_selection_keyboard(self):
        """
        Get the inline keyboard for language selection.
        
        Returns:
            dict: Inline keyboard markup
        """
        return {
            "inline_keyboard": [
                [
                    {"text": "🇻🇳 Tiếng Việt", "callback_data": f"lang_{self.VIETNAMESE}"},
                    {"text": "🇬🇧 English", "callback_data": f"lang_{self.ENGLISH}"}
                ],
                [
                    {"text": "🇹🇭 ภาษาไทย", "callback_data": f"lang_{self.THAI}"},
                    {"text": "🇨🇳 简体中文", "callback_data": f"lang_{self.CHINESE}"}
                ]
            ]
        }
    
    def get_language_name(self, language_code):
        """
        Get the display name for a language code.
        
        Args:
            language_code (str): The language code
            
        Returns:
            str: The language name
        """
        language_names = {
            self.VIETNAMESE: "Tiếng Việt",
            self.ENGLISH: "English",
            self.THAI: "ภาษาไทย",
            self.CHINESE: "简体中文"
        }
        return language_names.get(language_code, "Unknown")
        
    def translate_prediction(self, prediction, language_code):
        """
        Translate a prediction to the target language.
        
        For now, we're using the OpenAI Translation service in the prediction_service,
        so this is just a placeholder that returns the original prediction.
        
        Args:
            prediction (str): The prediction text in Vietnamese
            language_code (str): The language code to translate to
            
        Returns:
            str: The translated prediction or original if same language
        """
        # If target language is already Vietnamese, return as-is
        if language_code == self.VIETNAMESE:
            return prediction
            
        # In a real implementation, this would call a translation service or use pre-translated templates
        # For now, we'll rely on the prediction_service to generate predictions in different languages
        return prediction