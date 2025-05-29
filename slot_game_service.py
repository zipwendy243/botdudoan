import os
import logging
import re
from openai import OpenAI
from pgsoft_scraper import PGSoftScraper
from models import PGSoftGame
from app import db
from language_service import LanguageService

logger = logging.getLogger(__name__)

class SlotGameService:
    def __init__(self):
        """Initialize the slot game service with OpenAI client and PGSoft scraper."""
        # Initialize OpenAI client
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.openai = OpenAI(api_key=self.openai_api_key)
        
        # Initialize PGSoft scraper
        self.scraper = PGSoftScraper()
        
        # Initialize language service
        self.language_service = LanguageService()
        
        # Popular PGSoft slot games
        self.popular_games = [
            "Mahjong Ways",
            "Mahjong Ways 2",
            "Fortune Mouse",
            "Lucky Neko",
            "Treasures of Aztec",
            "Wild Bandito",
            "Ganesha Fortune",
            "Queen of Bounty",
            "Dragon Hatch",
            "Gem Saviour Sword",
            "Phoenix Rises",
            "Dreams of Macau",
            "Leprechaun Riches",
            "Medusa 2",
            "Buffalo Win",
            "Dragon Tiger Luck",
            "Candy Burst",
            "Piggy Gold",
            "The Great Icescape",
            "Jungle Delight"
        ]
        
        # Build the game ID mapping
        self.game_id_mapping = {
            "mahjong ways": "pg-soft-mahjong-ways",
            "mahjong ways 2": "pg-soft-mahjong-ways-2",
            "fortune mouse": "pg-soft-fortune-mouse",
            "lucky neko": "pg-soft-lucky-neko",
            "treasures of aztec": "pg-soft-treasures-of-aztec",
            "wild bandito": "pg-soft-wild-bandito",
            "ganesha fortune": "pg-soft-ganesha-fortune",
            "queen of bounty": "pg-soft-queen-of-bounty",
            "dragon hatch": "pg-soft-dragon-hatch",
            "gem saviour sword": "pg-soft-gem-saviour-sword",
            "phoenix rises": "pg-soft-phoenix-rises",
            "dreams of macau": "pg-soft-dreams-of-macau",
            "leprechaun riches": "pg-soft-leprechaun-riches",
            "medusa 2": "pg-soft-medusa-2",
            "buffalo win": "pg-soft-buffalo-win",
            "dragon tiger luck": "pg-soft-dragon-tiger-luck",
            "candy burst": "pg-soft-candy-burst",
            "piggy gold": "pg-soft-piggy-gold",
            "the great icescape": "pg-soft-the-great-icescape",
            "jungle delight": "pg-soft-jungle-delight"
        }
        
        logger.info("Slot game service initialized")

    def get_game_info(self, game_name, language_code='vi'):
        """
        Get detailed information about a PGSoft slot game using real data from
        the official website combined with GPT-4o Mini analysis.
        
        Args:
            game_name (str): The name of the PGSoft slot game
            language_code (str): The language code to generate the information in
            
        Returns:
            str: Detailed information about the game in the requested language with image URL
        """
        try:
            # Convert game name to standardized format for lookup
            game_name_lower = game_name.lower().strip()
            
            # Find the game ID by using our mapping or constructing it
            game_id = None
            if game_name_lower in self.game_id_mapping:
                game_id = self.game_id_mapping[game_name_lower]
            else:
                # Try to construct a likely game ID format
                game_id = f"pg-soft-{re.sub(r'[^a-z0-9]+', '-', game_name_lower)}"
            
            # Fetch game details from our scraper or database
            game_data = None
            
            # Check database first
            cached_game = PGSoftGame.query.filter_by(game_id=game_id).first()
            if cached_game and PGSoftGame.is_cache_valid(game_id):
                logger.info(f"Using cached game data for: {game_name}")
                game_data = cached_game.to_dict()
            else:
                # Fetch fresh data if no cache or cache is expired
                logger.info(f"Fetching fresh game data for: {game_name}")
                game_data = self.scraper.fetch_game_details(game_id)
                
            # If we couldn't find the game, try a more generic approach
            if not game_data:
                logger.warning(f"Could not find game data for {game_name}, using generic info")
                return self._generate_generic_game_info(game_name, language_code)
                
            # Extract game details
            name = game_data.get('name', game_name)
            description = game_data.get('description', '')
            
            # Handle fallback image URLs for known games
            image_url = game_data.get('image_url', '')
            if not image_url:
                fallback_images = {
                    'pg-soft-mahjong-ways': 'https://45.76.150.54/wp-content/uploads/2025/05/1.jpg',
                    'pg-soft-mahjong-ways-2': 'https://45.76.150.54/wp-content/uploads/2025/05/1.jpg',
                    'pg-soft-fortune-mouse': 'https://45.76.150.54/wp-content/uploads/2025/05/2.jpg',
                    'pg-soft-lucky-neko': 'https://pgslot.cc/wp-content/uploads/2020/12/lucky-neko.jpg',
                    'pg-soft-dragon-tiger-luck': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/dragon-tiger-luck-1536x864.jpg',
                    'pg-soft-treasures-of-aztec': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/treasures-of-aztec-1536x864.jpg',
                    'pg-soft-ganesha-fortune': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/ganesha-fortune-1536x864.jpg'
                }
                
                game_id = game_data.get('game_id', '')
                if game_id and game_id in fallback_images:
                    image_url = fallback_images[game_id]
                elif game_name.lower() == 'mahjong ways 2':
                    image_url = fallback_images['pg-soft-mahjong-ways-2']
                elif game_name.lower() == 'mahjong ways':
                    image_url = fallback_images['pg-soft-mahjong-ways']
            
            rtp = game_data.get('rtp', 'N/A')
            detail_url = game_data.get('detail_url', '')
            
            # Define language-specific templates
            templates = {
                'vi': {
                    'system_content': "Bạn là một chuyên gia về game slot PGSoft với kiến thức chuyên sâu về cách chơi, chiến thuật và thông số kỹ thuật của tất cả các game. Bạn luôn cung cấp thông tin chính xác, đầy đủ và hữu ích bằng tiếng Việt tự nhiên.",
                    'prompt_template': f"""
                    Hãy viết một bài giới thiệu tổng quan về game slot PGSoft có tên "{name}" dựa trên
                    các thông tin thực từ trang web chính thức:
                    
                    Tên game: {name}
                    Mô tả: {description}
                    Tỷ lệ trả thưởng (RTP): {rtp}
                    Link chi tiết: {detail_url}
                    
                    Bài viết phải bao gồm các thông tin sau:
                    1. Giới thiệu tổng quan về game và chủ đề của game
                    2. Cách kích hoạt tính năng free spin hoặc bonus game
                    3. Tỷ lệ trả thưởng (RTP) trích dẫn chính xác từ nguồn
                    4. Các mẹo và chiến thuật để tăng cơ hội thắng
                    
                    Hãy viết bằng tiếng Việt tự nhiên, thân thiện và dễ hiểu. Sử dụng emoji phù hợp để làm nổi bật thông tin.
                    Giới hạn bài viết trong khoảng 150-200 từ.
                    """,
                    'header': f"<b>🎮 THÔNG TIN GAME: {name.upper()} 🎮</b>",
                    'rtp_label': f"<b>🔍 RTP: {rtp}</b>",
                    'footer': "<i>Chúc bạn may mắn và chơi game vui vẻ! Hãy nhớ chơi có trách nhiệm.</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 Chơi ngay tại NOVA88BET 💎</a>"
                },
                'en': {
                    'system_content': "You are an expert on PGSoft slot games with deep knowledge of gameplay, strategies, and technical specifications of all games. You always provide accurate, complete, and useful information in natural English.",
                    'prompt_template': f"""
                    Please write an overview of the PGSoft slot game named "{name}" based on
                    real information from the official website:
                    
                    Game name: {name}
                    Description: {description}
                    Return to Player (RTP): {rtp}
                    Detail link: {detail_url}
                    
                    The article must include the following information:
                    1. General introduction to the game and its theme
                    2. How to activate free spin or bonus game features
                    3. Return to Player (RTP) rate quoted accurately from source
                    4. Tips and strategies to increase chances of winning
                    
                    Please write in natural, friendly, and easy-to-understand English. Use appropriate emojis to highlight information.
                    Limit the article to about 150-200 words.
                    """,
                    'header': f"<b>🎮 GAME INFORMATION: {name.upper()} 🎮</b>",
                    'rtp_label': f"<b>🔍 RTP: {rtp}</b>",
                    'footer': "<i>Good luck and have fun playing! Remember to play responsibly.</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 Play now at NOVA88BET 💎</a>"
                },
                'th': {
                    'system_content': "คุณเป็นผู้เชี่ยวชาญเกมสล็อต PGSoft ที่มีความรู้ลึกซึ้งเกี่ยวกับวิธีการเล่น กลยุทธ์ และข้อมูลจำเพาะทางเทคนิคของเกมทั้งหมด คุณให้ข้อมูลที่ถูกต้อง ครบถ้วน และเป็นประโยชน์ในภาษาไทยที่เป็นธรรมชาติเสมอ",
                    'prompt_template': f"""
                    กรุณาเขียนภาพรวมของเกมสล็อต PGSoft ชื่อ "{name}" โดยอิงจาก
                    ข้อมูลจริงจากเว็บไซต์ทางการ:
                    
                    ชื่อเกม: {name}
                    คำอธิบาย: {description}
                    อัตราการจ่ายเงินคืนผู้เล่น (RTP): {rtp}
                    ลิงก์รายละเอียด: {detail_url}
                    
                    บทความต้องมีข้อมูลต่อไปนี้:
                    1. บทนำทั่วไปเกี่ยวกับเกมและธีมของเกม
                    2. วิธีเปิดใช้งานฟีเจอร์ฟรีสปินหรือโบนัสเกม
                    3. อัตราการจ่ายเงินคืนผู้เล่น (RTP) อ้างอิงอย่างถูกต้องจากแหล่งที่มา
                    4. เคล็ดลับและกลยุทธ์เพื่อเพิ่มโอกาสในการชนะ
                    
                    กรุณาเขียนเป็นภาษาไทยที่เป็นธรรมชาติ เป็นมิตร และเข้าใจง่าย ใช้อิโมจิที่เหมาะสมเพื่อเน้นข้อมูล
                    จำกัดบทความไว้ที่ประมาณ 150-200 คำ
                    """,
                    'header': f"<b>🎮 ข้อมูลเกม: {name.upper()} 🎮</b>",
                    'rtp_label': f"<b>🔍 RTP: {rtp}</b>",
                    'footer': "<i>โชคดีและสนุกกับการเล่น! อย่าลืมเล่นอย่างมีความรับผิดชอบ</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 เล่นเลยที่ NOVA88BET 💎</a>"
                },
                'zh': {
                    'system_content': "您是PGSoft老虎机游戏专家，对所有游戏的玩法、策略和技术规格有深入了解。您始终以自然的中文提供准确、完整和有用的信息。",
                    'prompt_template': f"""
                    请根据官方网站的真实信息，编写关于PGSoft老虎机游戏"{name}"的概述：
                    
                    游戏名称：{name}
                    描述：{description}
                    玩家回报率(RTP)：{rtp}
                    详情链接：{detail_url}
                    
                    文章必须包含以下信息：
                    1. 游戏及其主题的一般介绍
                    2. 如何激活免费旋转或奖励游戏功能
                    3. 准确引用来源的玩家回报率(RTP)
                    4. 增加获胜机会的技巧和策略
                    
                    请用自然、友好和易于理解的中文写作。使用适当的表情符号突出信息。
                    将文章限制在约150-200字。
                    """,
                    'header': f"<b>🎮 游戏信息：{name.upper()} 🎮</b>",
                    'rtp_label': f"<b>🔍 RTP: {rtp}</b>",
                    'footer': "<i>祝您好运，玩得开心！请记得负责任地游戏。</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 立即在NOVA88BET上玩 💎</a>"
                }
            }
            
            # Select the appropriate language template or default to Vietnamese
            if language_code not in templates:
                logger.warning(f"Language code '{language_code}' not supported for slot game info, using Vietnamese")
                language_code = 'vi'
                
            template = templates[language_code]
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",  # Using GPT-4o Mini as specified in requirements
                messages=[
                    {"role": "system", "content": template['system_content']},
                    {"role": "user", "content": template['prompt_template']}
                ],
                max_tokens=500
            )
            
            game_info = response.choices[0].message.content
            
            # Format the response with a header and the actual image URL
            formatted_info = f"""
{template['header']}

{game_info}

{template['rtp_label']}

{template['footer']}

{template['play_button']}
"""
            
            logger.info(f"Generated slot game info with real data for: {game_name}")
            
            # Return both the formatted info text and image URL so the bot handler can use it
            return {"text": formatted_info, "image_url": image_url}
            
        except Exception as e:
            logger.error(f"Error generating slot game info: {e}")
            return {"text": f"❌ Đã xảy ra lỗi khi tìm thông tin về game '{game_name}'. Vui lòng thử lại sau. Error: {str(e)}", "image_url": None}

    def _generate_generic_game_info(self, game_name, language_code='vi'):
        """Generate generic game info when specific data cannot be found."""
        try:
            # Try to find a fallback image based on game name
            fallback_image_url = None
            fallback_images = {
                'mahjong ways': 'https://45.76.150.54/wp-content/uploads/2025/05/1.jpg',
                'mahjong ways 2': 'https://45.76.150.54/wp-content/uploads/2025/05/1.jpg',
                'fortune mouse': 'https://45.76.150.54/wp-content/uploads/2025/05/2.jpg',
                'lucky neko': 'https://pgslot.cc/wp-content/uploads/2020/12/lucky-neko.jpg',
                'dragon tiger luck': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/dragon-tiger-luck-1536x864.jpg',
                'treasures of aztec': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/treasures-of-aztec-1536x864.jpg',
                'ganesha fortune': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/ganesha-fortune-1536x864.jpg',
                'wild bandito': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/wild-bandito-1536x864.jpg',
                'queen of bounty': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/queen-of-bounty-1536x864.jpg'
            }
            
            game_name_lower = game_name.lower()
            if game_name_lower in fallback_images:
                fallback_image_url = fallback_images[game_name_lower]
            else:
                # Use a generic PGSoft image as default fallback
                fallback_image_url = "https://www.pgslot9999.com/wp-content/uploads/2020/02/pgslot99-01.jpg"
            
            # Define language-specific templates
            templates = {
                'vi': {
                    'system_content': "Bạn là một chuyên gia về game slot PGSoft với kiến thức chuyên sâu về cách chơi, chiến thuật và thông số kỹ thuật của tất cả các game. Bạn luôn cung cấp thông tin chính xác, đầy đủ và hữu ích bằng tiếng Việt tự nhiên.",
                    'prompt_template': f"""
                    Hãy mô tả chi tiết về game slot PGSoft có tên "{game_name}" bao gồm các thông tin sau:
                    
                    1. Hình ảnh và chủ đề của game
                    2. Cách kích hoạt tính năng free spin hoặc bonus game
                    3. Ước tính tỷ lệ trả thưởng (RTP) dựa trên các game PGSoft tương tự
                    4. Các mẹo và chiến thuật để tăng cơ hội thắng
                    
                    Hãy viết bằng tiếng Việt tự nhiên, thân thiện và dễ hiểu. Sử dụng emoji phù hợp để làm nổi bật thông tin.
                    """,
                    'header': f"<b>🎮 THÔNG TIN GAME: {game_name.upper()} 🎮</b>",
                    'footer': "<i>Chúc bạn may mắn và chơi game vui vẻ! Hãy nhớ chơi có trách nhiệm.</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 Chơi ngay tại NOVA88BET 💎</a>"
                },
                'en': {
                    'system_content': "You are an expert on PGSoft slot games with deep knowledge of gameplay, strategies, and technical specifications of all games. You always provide accurate, complete, and useful information in natural English.",
                    'prompt_template': f"""
                    Please provide a detailed description of the PGSoft slot game named "{game_name}" including the following information:
                    
                    1. Visuals and theme of the game
                    2. How to activate free spin or bonus game features
                    3. Estimated Return to Player (RTP) based on similar PGSoft games
                    4. Tips and strategies to increase chances of winning
                    
                    Please write in natural, friendly, and easy-to-understand English. Use appropriate emojis to highlight information.
                    """,
                    'header': f"<b>🎮 GAME INFORMATION: {game_name.upper()} 🎮</b>",
                    'footer': "<i>Good luck and have fun playing! Remember to play responsibly.</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 Play now at NOVA88BET 💎</a>"
                },
                'th': {
                    'system_content': "คุณเป็นผู้เชี่ยวชาญเกมสล็อต PGSoft ที่มีความรู้ลึกซึ้งเกี่ยวกับวิธีการเล่น กลยุทธ์ และข้อมูลจำเพาะทางเทคนิคของเกมทั้งหมด คุณให้ข้อมูลที่ถูกต้อง ครบถ้วน และเป็นประโยชน์ในภาษาไทยที่เป็นธรรมชาติเสมอ",
                    'prompt_template': f"""
                    กรุณาให้คำอธิบายโดยละเอียดเกี่ยวกับเกมสล็อต PGSoft ชื่อ "{game_name}" โดยรวมข้อมูลต่อไปนี้:
                    
                    1. ภาพและธีมของเกม
                    2. วิธีเปิดใช้งานฟีเจอร์ฟรีสปินหรือโบนัสเกม
                    3. ประมาณการอัตราการจ่ายเงินคืนผู้เล่น (RTP) ตามเกม PGSoft ที่คล้ายกัน
                    4. เคล็ดลับและกลยุทธ์เพื่อเพิ่มโอกาสในการชนะ
                    
                    กรุณาเขียนเป็นภาษาไทยที่เป็นธรรมชาติ เป็นมิตร และเข้าใจง่าย ใช้อิโมจิที่เหมาะสมเพื่อเน้นข้อมูล
                    """,
                    'header': f"<b>🎮 ข้อมูลเกม: {game_name.upper()} 🎮</b>",
                    'footer': "<i>โชคดีและสนุกกับการเล่น! อย่าลืมเล่นอย่างมีความรับผิดชอบ</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 เล่นเลยที่ NOVA88BET 💎</a>"
                },
                'zh': {
                    'system_content': "您是PGSoft老虎机游戏专家，对所有游戏的玩法、策略和技术规格有深入了解。您始终以自然的中文提供准确、完整和有用的信息。",
                    'prompt_template': f"""
                    请详细描述名为"{game_name}"的PGSoft老虎机游戏，包括以下信息：
                    
                    1. 游戏的视觉效果和主题
                    2. 如何激活免费旋转或奖励游戏功能
                    3. 根据类似的PGSoft游戏估计的玩家回报率(RTP)
                    4. 增加获胜机会的技巧和策略
                    
                    请用自然、友好和易于理解的中文写作。使用适当的表情符号突出信息。
                    """,
                    'header': f"<b>🎮 游戏信息：{game_name.upper()} 🎮</b>",
                    'footer': "<i>祝您好运，玩得开心！请记得负责任地游戏。</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 立即在NOVA88BET上玩 💎</a>"
                }
            }
            
            # Select the appropriate language template or default to Vietnamese
            if language_code not in templates:
                logger.warning(f"Language code '{language_code}' not supported for generic slot game info, using Vietnamese")
                language_code = 'vi'
                
            template = templates[language_code]
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",  # Using GPT-4o Mini as specified in requirements
                messages=[
                    {"role": "system", "content": template['system_content']},
                    {"role": "user", "content": template['prompt_template']}
                ],
                max_tokens=500
            )
            
            game_info = response.choices[0].message.content
            
            # Format the response with a header
            formatted_info = f"""
{template['header']}

{game_info}

{template['footer']}

{template['play_button']}
"""
            
            logger.info(f"Generated generic slot game info for: {game_name} in {language_code}")
            return {"text": formatted_info, "image_url": fallback_image_url}
            
        except Exception as e:
            logger.error(f"Error generating generic game info: {e}")
            return {"text": f"❌ Đã xảy ra lỗi khi tìm thông tin về game '{game_name}'. Vui lòng thử lại sau.", "image_url": None}

    def get_popular_games_list(self, language_code='vi'):
        """
        Get a formatted list of popular PGSoft slot games in the specified language.
        
        Args:
            language_code (str): The language code to generate the list in
            
        Returns:
            dict: Contains formatted text list and a list of game data
        """
        try:
            # Try to fetch real game data from scraper
            games_data = []
            for game_name in self.popular_games:
                game_name_lower = game_name.lower()
                if game_name_lower in self.game_id_mapping:
                    game_id = self.game_id_mapping[game_name_lower]
                    
                    # Check if we have cached data
                    cached_game = PGSoftGame.query.filter_by(game_id=game_id).first()
                    if cached_game:
                        games_data.append(cached_game.to_dict())
            
            # If we don't have enough games from cache, fetch some from the website
            if len(games_data) < 5:
                try:
                    fetched_games = self.scraper.fetch_game_list()
                    if fetched_games:
                        for game in fetched_games[:20]:  # Limit to 20 games
                            games_data.append(game)
                except Exception as e:
                    logger.error(f"Error fetching game list: {e}")
            
            # Make sure we have at least the popular games list even if scraping failed
            if not games_data:
                games_data = [{"name": game} for game in self.popular_games]
            
            # Define language-specific templates
            templates = {
                'vi': {
                    'header': "<b>🎯 DANH SÁCH CÁC GAME SLOT PGSOFT PHỔ BIẾN 🎯</b>",
                    'usage_info': "<i>Sử dụng lệnh /slotgame tên_game để xem thông tin chi tiết về một game cụ thể.</i>",
                    'example': "<i>Ví dụ: /slotgame Mahjong Ways 2</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 Chơi ngay tại NOVA88BET 💎</a>"
                },
                'en': {
                    'header': "<b>🎯 LIST OF POPULAR PGSOFT SLOT GAMES 🎯</b>",
                    'usage_info': "<i>Use the /slotgame game_name command to view detailed information about a specific game.</i>",
                    'example': "<i>Example: /slotgame Mahjong Ways 2</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 Play now at NOVA88BET 💎</a>"
                },
                'th': {
                    'header': "<b>🎯 รายชื่อเกมสล็อต PGSOFT ยอดนิยม 🎯</b>",
                    'usage_info': "<i>ใช้คำสั่ง /slotgame ชื่อเกม เพื่อดูข้อมูลโดยละเอียดเกี่ยวกับเกมเฉพาะ</i>",
                    'example': "<i>ตัวอย่าง: /slotgame Mahjong Ways 2</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 เล่นเลยที่ NOVA88BET 💎</a>"
                },
                'zh': {
                    'header': "<b>🎯 热门PGSOFT老虎机游戏列表 🎯</b>",
                    'usage_info': "<i>使用 /slotgame 游戏名称 命令查看特定游戏的详细信息。</i>",
                    'example': "<i>示例：/slotgame Mahjong Ways 2</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 立即在NOVA88BET上玩 💎</a>"
                }
            }
            
            # Select the appropriate language template or default to Vietnamese
            if language_code not in templates:
                logger.warning(f"Language code '{language_code}' not supported for game list, using Vietnamese")
                language_code = 'vi'
                
            template = templates[language_code]
            
            # Create a formatted list string
            game_list = "\n".join([f"🎮 {i+1}. {game.get('name')}" for i, game in enumerate(games_data[:20])])
            
            formatted_list = f"""
{template['header']}

{game_list}

{template['usage_info']}
{template['example']}

{template['play_button']}
"""
            logger.info(f"Generated popular games list in {language_code}")
            return {"text": formatted_list, "games": games_data}
            
        except Exception as e:
            logger.error(f"Error generating game list: {e}")
            
            # Define language-specific error templates
            error_templates = {
                'vi': {
                    'header': "<b>🎯 DANH SÁCH CÁC GAME SLOT PGSOFT PHỔ BIẾN 🎯</b>",
                    'usage_info': "<i>Sử dụng lệnh /slotgame tên_game để xem thông tin chi tiết về một game cụ thể.</i>",
                    'example': "<i>Ví dụ: /slotgame Mahjong Ways 2</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 Chơi ngay tại NOVA88BET 💎</a>"
                },
                'en': {
                    'header': "<b>🎯 LIST OF POPULAR PGSOFT SLOT GAMES 🎯</b>",
                    'usage_info': "<i>Use the /slotgame game_name command to view detailed information about a specific game.</i>",
                    'example': "<i>Example: /slotgame Mahjong Ways 2</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 Play now at NOVA88BET 💎</a>"
                },
                'th': {
                    'header': "<b>🎯 รายชื่อเกมสล็อต PGSOFT ยอดนิยม 🎯</b>",
                    'usage_info': "<i>ใช้คำสั่ง /slotgame ชื่อเกม เพื่อดูข้อมูลโดยละเอียดเกี่ยวกับเกมเฉพาะ</i>",
                    'example': "<i>ตัวอย่าง: /slotgame Mahjong Ways 2</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 เล่นเลยที่ NOVA88BET 💎</a>"
                },
                'zh': {
                    'header': "<b>🎯 热门PGSOFT老虎机游戏列表 🎯</b>",
                    'usage_info': "<i>使用 /slotgame 游戏名称 命令查看特定游戏的详细信息。</i>",
                    'example': "<i>示例：/slotgame Mahjong Ways 2</i>",
                    'play_button': "<a href=\"https://nova88bet.top/\">💎 立即在NOVA88BET上玩 💎</a>"
                }
            }
            
            # Select the appropriate error template or default to Vietnamese
            if language_code not in error_templates:
                language_code = 'vi'
                
            error_template = error_templates[language_code]
            
            # Fallback to simple list if anything fails
            game_list = "\n".join([f"🎮 {i+1}. {game}" for i, game in enumerate(self.popular_games)])
            
            formatted_list = f"""
{error_template['header']}

{game_list}

{error_template['usage_info']}
{error_template['example']}

{error_template['play_button']}
"""
            logger.info(f"Generated fallback popular games list in {language_code}")
            return {"text": formatted_list, "games": []}