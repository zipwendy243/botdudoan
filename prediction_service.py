import os
import logging
from datetime import datetime, timedelta
from openai import OpenAI
from language_service import LanguageService

logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self):
        """Initialize the prediction service with OpenAI client."""
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Initialize OpenAI client
        self.openai = OpenAI(api_key=self.openai_api_key)
        
        # Initialize language service
        self.language_service = LanguageService()
        
        # Store predictions for different lottery types with their timestamps and languages
        # Format: {lottery_type: {language_code: {'prediction': text, 'date': date}}}
        self.predictions = {
            'vietnam': {
                'vi': {'prediction': None, 'date': None},
                'en': {'prediction': None, 'date': None},
                'th': {'prediction': None, 'date': None},
                'zh': {'prediction': None, 'date': None}
            },
            '4d': {
                'vi': {'prediction': None, 'date': None},
                'en': {'prediction': None, 'date': None},
                'th': {'prediction': None, 'date': None},
                'zh': {'prediction': None, 'date': None}
            },
            'thai': {
                'vi': {'prediction': None, 'date': None},
                'en': {'prediction': None, 'date': None},
                'th': {'prediction': None, 'date': None},
                'zh': {'prediction': None, 'date': None}
            },
            'indo': {
                'vi': {'prediction': None, 'date': None},
                'en': {'prediction': None, 'date': None},
                'th': {'prediction': None, 'date': None},
                'zh': {'prediction': None, 'date': None}
            }
        }
        
        # Log initialization
        logger.info("Prediction service initialized and ready to generate random lottery predictions")

    def generate_vietnam_prediction(self, language_code='vi'):
        """
        Generate a new Vietnam lottery prediction using OpenAI's GPT-4o Mini model.
        
        Args:
            language_code (str): The language code to generate the prediction in
            
        Returns:
            str: The formatted prediction text in the requested language
        """
        try:
            # Get the current date for reference in the prompt
            today = datetime.now().strftime("%d/%m/%Y")
            
            # Define system and user prompts for different languages
            prompts = {
                'vi': {
                    'system': "Bạn là một chuyên gia dự đoán xổ số Việt Nam với nhiều năm kinh nghiệm. Cung cấp những dự đoán chính xác và hữu ích cho người chơi. Luôn tạo các số xổ số ngẫu nhiên, không theo mẫu, các số giải đặc biệt phải là 6 chữ số ngẫu nhiên thực sự (như 578421, 309764) và các cặp số may mắn là 2 chữ số ngẫu nhiên (như 35, 72, 19). Tuyệt đối không đưa ra các số theo tuần tự hoặc mẫu đơn giản như 123456.",
                    'user': f"""
                    Hãy đưa ra dự đoán xổ số Việt Nam cho ngày {today} cho cả ba miền: Bắc, Trung, Nam với các số ngẫu nhiên, không sử dụng mẫu số đơn giản như 123456.
                    
                    Dự đoán cần bao gồm:
                    1. Miền Bắc: Giải đặc biệt (6 chữ số ngẫu nhiên) và 3-5 cặp số may mắn (2 chữ số mỗi cặp)
                    2. Miền Trung: Giải đặc biệt (6 chữ số ngẫu nhiên) và 3-5 cặp số may mắn (2 chữ số mỗi cặp) 
                    3. Miền Nam: Giải đặc biệt (6 chữ số ngẫu nhiên) và 3-5 cặp số may mắn (2 chữ số mỗi cặp)
                    
                    QUAN TRỌNG: 
                    - Số giải đặc biệt phải là 6 chữ số ngẫu nhiên (ví dụ: 651429, 783052, 247916)
                    - Mỗi cặp số may mắn phải là 2 chữ số ngẫu nhiên (ví dụ: 26, 83, 57, 14, 90)
                    - KHÔNG được sử dụng các mẫu số đơn giản và dễ đoán như 123456, 111111, 222222, v.v.
                    - Mỗi bộ số phải hoàn toàn ngẫu nhiên và khác nhau
                    
                    Sử dụng giọng điệu tự nhiên, thân thiện và hấp dẫn bằng tiếng Việt. Thêm một vài lưu ý nhỏ hoặc mẹo về cách đặt cược thông minh.
                    
                    Format response in clear, readable Vietnamese with appropriate line breaks and emphasis.
                    """,
                    'header': f"<b>🎯 DỰ ĐOÁN XỔ SỐ VIỆT NAM NGÀY {today} 🎯</b>",
                    'footer': "<i>Chúc bạn may mắn! Hãy nhớ đặt cược có trách nhiệm.</i>"
                },
                'en': {
                    'system': "You are a Vietnamese lottery prediction expert with many years of experience. Provide accurate and helpful predictions for players. Always generate random lottery numbers without patterns. Special prizes must be truly random 6-digit numbers (like 578421, 309764) and lucky pairs must be random 2-digit numbers (like 35, 72, 19). Never provide sequential numbers or simple patterns like 123456.",
                    'user': f"""
                    Provide Vietnam lottery predictions for {today} for all three regions: North, Central, and South, using random numbers without simple patterns like 123456.
                    
                    The prediction should include:
                    1. North region: Special prize (6 random digits) and 3-5 lucky number pairs (2 digits each)
                    2. Central region: Special prize (6 random digits) and 3-5 lucky number pairs (2 digits each)
                    3. South region: Special prize (6 random digits) and 3-5 lucky number pairs (2 digits each)
                    
                    IMPORTANT:
                    - Special prize numbers must be 6 random digits (e.g., 651429, 783052, 247916)
                    - Each lucky pair must be 2 random digits (e.g., 26, 83, 57, 14, 90)
                    - DO NOT use simple and predictable patterns like 123456, 111111, 222222, etc.
                    - Each set of numbers must be completely random and different from each other
                    
                    Use a natural, friendly, and engaging tone in English. Add a few small notes or tips on smart betting strategies.
                    
                    Format response in clear, readable English with appropriate line breaks and emphasis.
                    """,
                    'header': f"<b>🎯 VIETNAM LOTTERY PREDICTION FOR {today} 🎯</b>",
                    'footer': "<i>Good luck! Remember to bet responsibly.</i>"
                },
                'th': {
                    'system': "คุณเป็นผู้เชี่ยวชาญด้านการทำนายผลสลากกินแบ่งเวียดนามที่มีประสบการณ์หลายปี ให้คำทำนายที่แม่นยำและเป็นประโยชน์สำหรับผู้เล่น สร้างตัวเลขสลากกินแบ่งแบบสุ่มเสมอโดยไม่มีรูปแบบ รางวัลพิเศษต้องเป็นตัวเลข 6 หลักที่สุ่มจริง (เช่น 578421, 309764) และคู่โชคดีต้องเป็นตัวเลข 2 หลักแบบสุ่ม (เช่น 35, 72, 19) ห้ามให้ตัวเลขเรียงลำดับหรือรูปแบบง่ายๆ เช่น 123456",
                    'user': f"""
                    ให้คำทำนายสลากกินแบ่งเวียดนามสำหรับวันที่ {today} สำหรับทั้งสามภูมิภาค: เหนือ, กลาง, และใต้ โดยใช้ตัวเลขสุ่มโดยไม่มีรูปแบบง่ายๆ เช่น 123456
                    
                    คำทำนายควรประกอบด้วย:
                    1. ภาคเหนือ: รางวัลพิเศษ (6 หลักสุ่ม) และ 3-5 คู่เลขโชคดี (2 หลักต่อคู่)
                    2. ภาคกลาง: รางวัลพิเศษ (6 หลักสุ่ม) และ 3-5 คู่เลขโชคดี (2 หลักต่อคู่)
                    3. ภาคใต้: รางวัลพิเศษ (6 หลักสุ่ม) และ 3-5 คู่เลขโชคดี (2 หลักต่อคู่)
                    
                    สำคัญ:
                    - ตัวเลขรางวัลพิเศษต้องเป็น 6 หลักแบบสุ่ม (เช่น 651429, 783052, 247916)
                    - แต่ละคู่โชคดีต้องเป็น 2 หลักแบบสุ่ม (เช่น 26, 83, 57, 14, 90)
                    - ห้ามใช้รูปแบบง่ายและคาดเดาได้เช่น 123456, 111111, 222222 เป็นต้น
                    - แต่ละชุดของตัวเลขต้องสุ่มอย่างสมบูรณ์และแตกต่างจากกัน
                    
                    ใช้น้ำเสียงที่เป็นธรรมชาติ เป็นมิตร และน่าสนใจเป็นภาษาไทย เพิ่มเคล็ดลับเล็กๆ น้อยๆ เกี่ยวกับกลยุทธ์การเดิมพันที่ชาญฉลาด
                    
                    จัดรูปแบบการตอบเป็นภาษาไทยที่อ่านง่ายและชัดเจนพร้อมการขึ้นบรรทัดและการเน้นที่เหมาะสม
                    """,
                    'header': f"<b>🎯 การทำนายผลสลากกินแบ่งเวียดนามสำหรับวันที่ {today} 🎯</b>",
                    'footer': "<i>โชคดี! อย่าลืมเดิมพันอย่างมีความรับผิดชอบ</i>"
                },
                'zh': {
                    'system': "您是一位拥有多年经验的越南彩票预测专家。为玩家提供准确有用的预测。始终生成没有规律的随机彩票号码。特别奖必须是真正随机的6位数字（如578421、309764），幸运对必须是随机的2位数字（如35、72、19）。切勿提供连续数字或简单模式，如123456。",
                    'user': f"""
                    提供{today}日越南彩票预测，包括北部、中部和南部三个地区，使用随机数字，避免使用像123456这样的简单模式。
                    
                    预测应包括：
                    1. 北部地区：特别奖（6位随机数字）和3-5对幸运数字（每对2位数字）
                    2. 中部地区：特别奖（6位随机数字）和3-5对幸运数字（每对2位数字）
                    3. 南部地区：特别奖（6位随机数字）和3-5对幸运数字（每对2位数字）
                    
                    重要提示：
                    - 特别奖号码必须是6位随机数字（例如：651429、783052、247916）
                    - 每对幸运数字必须是2位随机数字（例如：26、83、57、14、90）
                    - 不要使用简单和可预测的模式，如123456、111111、222222等
                    - 每组数字必须完全随机且彼此不同
                    
                    使用自然、友好和吸引人的中文语调。添加一些关于智能投注策略的小提示。
                    
                    以清晰、易读的中文格式回应，使用适当的换行和强调。
                    """,
                    'header': f"<b>🎯 {today}越南彩票预测 🎯</b>",
                    'footer': "<i>祝您好运！请记得负责任地投注。</i>"
                }
            }
            
            # Check if language is supported
            if language_code not in prompts:
                logger.warning(f"Language {language_code} not supported for predictions, using Vietnamese")
                language_code = 'vi'
                
            # Get prompts for the requested language
            selected_prompts = prompts[language_code]
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",  # Using GPT-4o Mini as specified in requirements
                messages=[
                    {"role": "system", "content": selected_prompts['system']},
                    {"role": "user", "content": selected_prompts['user']}
                ],
                max_tokens=1000
            )
            
            prediction_text = response.choices[0].message.content
            
            # Format the prediction with a header and footer in the requested language
            formatted_prediction = f"""
{selected_prompts['header']}

{prediction_text}

{selected_prompts['footer']}
"""
            
            logger.info(f"Generated new Vietnam prediction in {language_code} for {today}")
            return formatted_prediction
            
        except Exception as e:
            logger.error(f"Error generating Vietnam prediction in {language_code}: {e}")
            error_messages = {
                'vi': f"❌ Đã xảy ra lỗi khi tạo dự đoán. Vui lòng thử lại sau. Error: {str(e)}",
                'en': f"❌ An error occurred while generating the prediction. Please try again later. Error: {str(e)}",
                'th': f"❌ เกิดข้อผิดพลาดขณะสร้างคำทำนาย โปรดลองอีกครั้งในภายหลัง ข้อผิดพลาด: {str(e)}",
                'zh': f"❌ 生成预测时出错。请稍后再试。错误：{str(e)}"
            }
            return error_messages.get(language_code, error_messages['vi'])

    def generate_4d_prediction(self, language_code='vi'):
        """
        Generate a new 4D lottery prediction (Singapore/Malaysia).
        
        Args:
            language_code (str): The language code to generate the prediction in
            
        Returns:
            str: The formatted prediction text in the requested language
        """
        try:
            # Get the current date for reference in the prompt
            today = datetime.now().strftime("%d/%m/%Y")
            
            # Define system and user prompts for different languages
            prompts = {
                'vi': {
                    'system': "Bạn là chuyên gia dự đoán xổ số 4D Singapore/Malaysia với nhiều năm kinh nghiệm. Hãy cung cấp những dự đoán ngẫu nhiên và hữu ích cho người chơi. Luôn tạo ra các số xổ số 4D hoàn toàn ngẫu nhiên (4 chữ số như 5289, 1736), không theo mẫu đơn giản nào.",
                    'user': f"""
                    Hãy đưa ra dự đoán cho xổ số 4D (Singapore/Malaysia) cho ngày {today} với các số ngẫu nhiên, không sử dụng mẫu số đơn giản.
                    
                    Dự đoán cần bao gồm:
                    1. Giải đặc biệt (4 chữ số ngẫu nhiên)
                    2. Giải nhất (4 chữ số ngẫu nhiên)
                    3. Giải nhì (4 chữ số ngẫu nhiên)
                    4. 5-7 con số may mắn khác (4 chữ số mỗi số)
                    
                    QUAN TRỌNG: 
                    - Tất cả các số phải là 4 chữ số ngẫu nhiên (ví dụ: 5492, 7830, 2479)
                    - KHÔNG sử dụng các mẫu số đơn giản và dễ đoán như 1234, 1111, 2222, v.v.
                    - Mỗi số phải hoàn toàn ngẫu nhiên và khác nhau
                    
                    Sử dụng giọng điệu tự nhiên, thân thiện và hấp dẫn bằng tiếng Việt. Thêm một vài lưu ý nhỏ hoặc mẹo về cách đặt cược 4D thông minh.
                    
                    Format response in clear, readable Vietnamese with appropriate line breaks and emphasis.
                    """,
                    'header': f"<b>🎮 DỰ ĐOÁN XỔ SỐ 4D (SINGAPORE/MALAYSIA) NGÀY {today} 🎮</b>",
                    'footer': "<i>Chúc bạn may mắn với xổ số 4D! Hãy đặt cược có trách nhiệm.</i>"
                },
                'en': {
                    'system': "You are a 4D Singapore/Malaysia lottery prediction expert with many years of experience. Provide random and helpful predictions for players. Always generate completely random 4D lottery numbers (4 digits like 5289, 1736), not following any simple pattern.",
                    'user': f"""
                    Provide predictions for 4D (Singapore/Malaysia) lottery for {today} with random numbers, not using simple number patterns.
                    
                    The prediction should include:
                    1. Special prize (4 random digits)
                    2. First prize (4 random digits)
                    3. Second prize (4 random digits)
                    4. 5-7 other lucky numbers (4 digits each)
                    
                    IMPORTANT: 
                    - All numbers must be 4 random digits (e.g., 5492, 7830, 2479)
                    - DO NOT use simple and predictable patterns like 1234, 1111, 2222, etc.
                    - Each number must be completely random and different from each other
                    
                    Use a natural, friendly, and engaging tone in English. Add a few small notes or tips on smart 4D betting strategies.
                    
                    Format response in clear, readable English with appropriate line breaks and emphasis.
                    """,
                    'header': f"<b>🎮 4D LOTTERY PREDICTION (SINGAPORE/MALAYSIA) FOR {today} 🎮</b>",
                    'footer': "<i>Good luck with your 4D lottery! Remember to bet responsibly.</i>"
                },
                'th': {
                    'system': "คุณเป็นผู้เชี่ยวชาญด้านการทำนายผลสลาก 4D สิงคโปร์/มาเลเซียที่มีประสบการณ์หลายปี ให้คำทำนายแบบสุ่มและเป็นประโยชน์สำหรับผู้เล่น สร้างตัวเลขสลาก 4D แบบสุ่มสมบูรณ์ (4 หลักเช่น 5289, 1736) ไม่ตามรูปแบบง่ายๆ ใดๆ",
                    'user': f"""
                    ให้คำทำนายสำหรับสลาก 4D (สิงคโปร์/มาเลเซีย) สำหรับวันที่ {today} ด้วยตัวเลขสุ่ม ไม่ใช้รูปแบบตัวเลขแบบง่าย
                    
                    คำทำนายควรประกอบด้วย:
                    1. รางวัลพิเศษ (4 หลักสุ่ม)
                    2. รางวัลที่หนึ่ง (4 หลักสุ่ม)
                    3. รางวัลที่สอง (4 หลักสุ่ม)
                    4. 5-7 ตัวเลขโชคดีอื่นๆ (4 หลักแต่ละตัว)
                    
                    สำคัญ: 
                    - ตัวเลขทั้งหมดต้องเป็น 4 หลักแบบสุ่ม (เช่น 5492, 7830, 2479)
                    - ห้ามใช้รูปแบบง่ายและทำนายได้เช่น 1234, 1111, 2222 เป็นต้น
                    - แต่ละตัวเลขต้องสุ่มอย่างสมบูรณ์และแตกต่างจากกัน
                    
                    ใช้น้ำเสียงที่เป็นธรรมชาติ เป็นมิตร และน่าสนใจเป็นภาษาไทย เพิ่มบันทึกเล็กๆ หรือเคล็ดลับเกี่ยวกับกลยุทธ์การเดิมพัน 4D อย่างชาญฉลาด
                    
                    จัดรูปแบบการตอบเป็นภาษาไทยที่อ่านง่ายและชัดเจนพร้อมการขึ้นบรรทัดและการเน้นที่เหมาะสม
                    """,
                    'header': f"<b>🎮 การทำนายสลาก 4D (สิงคโปร์/มาเลเซีย) สำหรับวันที่ {today} 🎮</b>",
                    'footer': "<i>โชคดีกับสลาก 4D! อย่าลืมเดิมพันอย่างมีความรับผิดชอบ</i>"
                },
                'zh': {
                    'system': "您是一位拥有多年经验的新加坡/马来西亚4D彩票预测专家。为玩家提供随机且有用的预测。始终生成完全随机的4D彩票号码（4位数字，如5289、1736），不遵循任何简单模式。",
                    'user': f"""
                    为{today}日的4D彩票（新加坡/马来西亚）提供预测，使用随机数字，不使用简单的数字模式。
                    
                    预测应包括：
                    1. 特别奖（4位随机数字）
                    2. 一等奖（4位随机数字）
                    3. 二等奖（4位随机数字）
                    4. 其他5-7个幸运数字（每个4位数字）
                    
                    重要事项：
                    - 所有数字必须是4位随机数字（例如：5492、7830、2479）
                    - 不要使用简单且可预测的模式，如1234、1111、2222等
                    - 每个数字必须完全随机且彼此不同
                    
                    使用自然、友好和引人入胜的中文语调。添加一些关于智能4D投注策略的小提示。
                    
                    以清晰、易读的中文格式回应，使用适当的换行和强调。
                    """,
                    'header': f"<b>🎮 {today}日4D彩票预测（新加坡/马来西亚）🎮</b>",
                    'footer': "<i>祝您4D彩票好运！请记得负责任地投注。</i>"
                }
            }
            
            # Check if language is supported
            if language_code not in prompts:
                logger.warning(f"Language {language_code} not supported for predictions, using Vietnamese")
                language_code = 'vi'
                
            # Get prompts for the requested language
            selected_prompts = prompts[language_code]
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": selected_prompts['system']},
                    {"role": "user", "content": selected_prompts['user']}
                ],
                max_tokens=1000
            )
            
            prediction_text = response.choices[0].message.content
            
            # Format the prediction with a header and footer in the requested language
            formatted_prediction = f"""
{selected_prompts['header']}

{prediction_text}

{selected_prompts['footer']}
"""
            
            logger.info(f"Generated new 4D prediction in {language_code} for {today}")
            return formatted_prediction
            
        except Exception as e:
            logger.error(f"Error generating 4D prediction in {language_code}: {e}")
            error_messages = {
                'vi': f"❌ Đã xảy ra lỗi khi tạo dự đoán 4D. Vui lòng thử lại sau. Error: {str(e)}",
                'en': f"❌ An error occurred while generating the 4D prediction. Please try again later. Error: {str(e)}",
                'th': f"❌ เกิดข้อผิดพลาดขณะสร้างคำทำนาย 4D โปรดลองอีกครั้งในภายหลัง ข้อผิดพลาด: {str(e)}",
                'zh': f"❌ 生成4D预测时出错。请稍后再试。错误：{str(e)}"
            }
            return error_messages.get(language_code, error_messages['vi'])

    def generate_thai_prediction(self, language_code='vi'):
        """
        Generate a new Thai lottery prediction.
        
        Args:
            language_code (str): The language code to generate the prediction in
            
        Returns:
            str: The formatted prediction text in the requested language
        """
        try:
            # Get the current date for reference in the prompt
            today = datetime.now().strftime("%d/%m/%Y")
            
            # Define language-specific prompts and templates
            prompts = {
                'vi': {
                    'system': "Bạn là chuyên gia dự đoán xổ số Thái Lan với nhiều năm kinh nghiệm. Hãy cung cấp những dự đoán ngẫu nhiên và hữu ích cho người chơi bằng tiếng Việt. Luôn tạo các số xổ số ngẫu nhiên, đặc biệt là giải đặc biệt 6 chữ số phải hoàn toàn ngẫu nhiên.",
                    'user': f"""
                    Hãy đưa ra dự đoán cho xổ số Thái Lan (หวยรัฐบาลไทย) cho ngày {today} với các số ngẫu nhiên.
                    
                    Dự đoán cần bao gồm:
                    1. Giải đặc biệt (6 chữ số ngẫu nhiên)
                    2. Giải nhất (3 chữ số ngẫu nhiên)
                    3. Giải nhì (2 chữ số ngẫu nhiên)
                    4. 5-7 số may mắn khác (2 chữ số mỗi số)
                    
                    QUAN TRỌNG: 
                    - Số đặc biệt phải là 6 chữ số ngẫu nhiên (ví dụ: 867294)
                    - Các giải khác phải là 2-3 chữ số ngẫu nhiên tùy theo yêu cầu
                    - KHÔNG sử dụng các mẫu số đơn giản như 123, 111, 222, v.v.
                    - Mỗi số phải hoàn toàn ngẫu nhiên và khác nhau
                    
                    Sử dụng giọng điệu tự nhiên, thân thiện và hấp dẫn bằng tiếng Việt. Thêm một vài lưu ý nhỏ hoặc mẹo về cách đặt cược xổ số Thái Lan thông minh.
                    """,
                    'header': f"<b>🇹🇭 DỰ ĐOÁN XỔ SỐ THÁI LAN NGÀY {today} 🇹🇭</b>",
                    'footer': "<i>Chúc bạn may mắn với xổ số Thái Lan! Hãy đặt cược có trách nhiệm.</i>"
                },
                'en': {
                    'system': "You are a Thai lottery prediction expert with many years of experience. Provide random and helpful predictions for players in English. Always generate completely random lottery numbers, especially the special prize 6-digit number.",
                    'user': f"""
                    Provide predictions for the Thai lottery (หวยรัฐบาลไทย) for {today} with random numbers.
                    
                    The prediction should include:
                    1. Special prize (6 random digits)
                    2. First prize (3 random digits)
                    3. Second prize (2 random digits)
                    4. 5-7 other lucky numbers (2 digits each)
                    
                    IMPORTANT:
                    - The special prize must be 6 random digits (e.g., 867294)
                    - Other prizes must be 2-3 random digits as required
                    - DO NOT use simple patterns like 123, 111, 222, etc.
                    - Each number must be completely random and different from each other
                    
                    Use a natural, friendly, and engaging tone in English. Add a few small notes or tips on smart Thai lottery betting strategies.
                    """,
                    'header': f"<b>🇹🇭 THAI LOTTERY PREDICTION FOR {today} 🇹🇭</b>",
                    'footer': "<i>Good luck with the Thai lottery! Remember to bet responsibly.</i>"
                },
                'th': {
                    'system': "คุณเป็นผู้เชี่ยวชาญในการทำนายหวยรัฐบาลไทยที่มีประสบการณ์หลายปี ให้คำทำนายที่สุ่มและเป็นประโยชน์สำหรับผู้เล่นในภาษาไทย สร้างตัวเลขหวยที่สุ่มอย่างสมบูรณ์ โดยเฉพาะตัวเลขรางวัลพิเศษ 6 หลัก",
                    'user': f"""
                    ให้คำทำนายสำหรับหวยรัฐบาลไทย สำหรับวันที่ {today} ด้วยตัวเลขที่สุ่ม
                    
                    คำทำนายควรมี:
                    1. รางวัลพิเศษ (เลข 6 หลักที่สุ่ม)
                    2. รางวัลที่หนึ่ง (เลข 3 หลักที่สุ่ม)
                    3. รางวัลที่สอง (เลข 2 หลักที่สุ่ม)
                    4. ตัวเลขโชคดีอื่นๆ 5-7 ตัว (เลข 2 หลักแต่ละตัว)
                    
                    สำคัญ:
                    - รางวัลพิเศษต้องเป็นเลข 6 หลักที่สุ่ม (เช่น 867294)
                    - รางวัลอื่นๆ ต้องเป็นเลข 2-3 หลักที่สุ่มตามที่กำหนด
                    - อย่าใช้รูปแบบง่ายๆ เช่น 123, 111, 222 เป็นต้น
                    - แต่ละตัวเลขต้องสุ่มอย่างสมบูรณ์และแตกต่างกัน
                    
                    ใช้น้ำเสียงที่เป็นธรรมชาติ เป็นมิตร และน่าสนใจในภาษาไทย เพิ่มบันทึกหรือเคล็ดลับเล็กๆน้อยๆ เกี่ยวกับกลยุทธ์การแทงหวยไทยที่ชาญฉลาด
                    """,
                    'header': f"<b>🇹🇭 คำทำนายหวยรัฐบาลไทยสำหรับวันที่ {today} 🇹🇭</b>",
                    'footer': "<i>โชคดีกับหวยรัฐบาลไทย! โปรดเล่นอย่างมีความรับผิดชอบ</i>"
                },
                'zh': {
                    'system': "您是一位拥有多年经验的泰国彩票预测专家。用中文为玩家提供随机且有用的预测。始终生成完全随机的彩票号码，尤其是6位数的特别奖号码。",
                    'user': f"""
                    提供 {today} 泰国彩票 (หวยรัฐบาลไทย) 的预测，使用随机数字。
                    
                    预测应包括：
                    1. 特别奖（6位随机数字）
                    2. 一等奖（3位随机数字）
                    3. 二等奖（2位随机数字）
                    4. 其他5-7个幸运数字（每个2位数字）
                    
                    重要事项：
                    - 特别奖必须是6位随机数字（例如：867294）
                    - 其他奖项必须是按要求的2-3位随机数字
                    - 不要使用简单的模式，如123、111、222等
                    - 每个数字必须完全随机且彼此不同
                    
                    请使用自然、友好和吸引人的中文语调。添加一些关于智能泰国彩票投注策略的小提示。
                    """,
                    'header': f"<b>🇹🇭 {today} 泰国彩票预测 🇹🇭</b>",
                    'footer': "<i>祝您在泰国彩票中好运！请记得负责任地投注。</i>"
                }
            }
            
            # Check if language is supported, default to Vietnamese if not
            if language_code not in prompts:
                logger.warning(f"Language {language_code} not supported for Thai prediction, using Vietnamese")
                language_code = 'vi'
                
            # Get prompts for the requested language
            selected_prompt = prompts[language_code]
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": selected_prompt['system']},
                    {"role": "user", "content": selected_prompt['user']}
                ],
                max_tokens=1000
            )
            
            prediction_text = response.choices[0].message.content
            
            # Format the prediction with a header
            formatted_prediction = f"""
{selected_prompt['header']}

{prediction_text}

{selected_prompt['footer']}
"""
            
            logger.info(f"Generated new Thai lottery prediction in {language_code} for {today}")
            return formatted_prediction
            
        except Exception as e:
            logger.error(f"Error generating Thai prediction in {language_code}: {e}")
            error_messages = {
                'vi': f"❌ Đã xảy ra lỗi khi tạo dự đoán xổ số Thái Lan. Vui lòng thử lại sau. Error: {str(e)}",
                'en': f"❌ An error occurred while generating the Thai lottery prediction. Please try again later. Error: {str(e)}",
                'th': f"❌ เกิดข้อผิดพลาดขณะสร้างคำทำนายหวยไทย โปรดลองอีกครั้งในภายหลัง ข้อผิดพลาด: {str(e)}",
                'zh': f"❌ 生成泰国彩票预测时出错。请稍后再试。错误：{str(e)}"
            }
            return error_messages.get(language_code, error_messages['vi'])

    def generate_indo_prediction(self, language_code='vi'):
        """
        Generate a new Indonesian Togel lottery prediction.
        
        Args:
            language_code (str): The language code to generate the prediction in
            
        Returns:
            str: The formatted prediction text in the requested language
        """
        try:
            # Get the current date for reference in the prompt
            today = datetime.now().strftime("%d/%m/%Y")
            
            # Define language-specific prompts and templates
            prompts = {
                'vi': {
                    'system': "Bạn là chuyên gia dự đoán xổ số Togel Indonesia với nhiều năm kinh nghiệm. Hãy cung cấp những dự đoán ngẫu nhiên và hữu ích cho người chơi bằng tiếng Việt. Luôn tạo các số xổ số ngẫu nhiên, không theo mẫu nào.",
                    'user': f"""
                    Hãy đưa ra dự đoán cho xổ số Indonesia (Togel) cho ngày {today} với các số ngẫu nhiên.
                    
                    Dự đoán cần bao gồm:
                    1. Giải 4D (4 chữ số ngẫu nhiên)
                    2. Giải 3D (3 chữ số ngẫu nhiên)
                    3. Giải 2D (2 chữ số ngẫu nhiên)
                    4. 5-7 con số may mắn khác (2 chữ số mỗi số)
                    
                    QUAN TRỌNG: 
                    - Tất cả các số phải là số ngẫu nhiên với số lượng chữ số tương ứng theo yêu cầu
                    - KHÔNG được sử dụng các mẫu số đơn giản và dễ đoán như 1234, 123, 12, 111, v.v.
                    - Mỗi số phải hoàn toàn ngẫu nhiên và khác nhau
                    
                    Sử dụng giọng điệu tự nhiên, thân thiện và hấp dẫn bằng tiếng Việt. Thêm một vài lưu ý nhỏ hoặc mẹo về cách đặt cược Togel Indonesia thông minh.
                    """,
                    'header': f"<b>🇮🇩 DỰ ĐOÁN XỔ SỐ TOGEL INDONESIA NGÀY {today} 🇮🇩</b>",
                    'footer': "<i>Chúc bạn may mắn với xổ số Togel Indonesia! Hãy đặt cược có trách nhiệm.</i>"
                },
                'en': {
                    'system': "You are an Indonesian Togel lottery prediction expert with many years of experience. Provide random and helpful predictions for players in English. Always generate completely random predictions, not following any simple patterns.",
                    'user': f"""
                    Provide predictions for the Indonesian Togel lottery for {today} with random numbers.
                    
                    The prediction should include:
                    1. 4D prize (4 random digits)
                    2. 3D prize (3 random digits)
                    3. 2D prize (2 random digits)
                    4. 5-7 other lucky numbers (2 digits each)
                    
                    IMPORTANT:
                    - All numbers must be random with the corresponding number of digits as required
                    - DO NOT use simple and predictable patterns like 1234, 123, 12, 111, etc.
                    - Each number must be completely random and different from each other
                    
                    Use a natural, friendly, and engaging tone in English. Add a few small notes or tips on smart Indonesian Togel betting strategies.
                    """,
                    'header': f"<b>🇮🇩 INDONESIAN TOGEL LOTTERY PREDICTION FOR {today} 🇮🇩</b>",
                    'footer': "<i>Good luck with the Indonesian Togel lottery! Remember to bet responsibly.</i>"
                },
                'th': {
                    'system': "คุณเป็นผู้เชี่ยวชาญในการทำนายลอตเตอรี่โทเกลของอินโดนีเซียที่มีประสบการณ์หลายปี ให้คำทำนายที่สุ่มและเป็นประโยชน์สำหรับผู้เล่นในภาษาไทย สร้างคำทำนายที่สุ่มอย่างสมบูรณ์ ไม่ตามรูปแบบง่ายๆ",
                    'user': f"""
                    ให้คำทำนายสำหรับลอตเตอรี่โทเกลของอินโดนีเซียสำหรับวันที่ {today} ด้วยตัวเลขที่สุ่ม
                    
                    คำทำนายควรประกอบด้วย:
                    1. รางวัล 4D (เลข 4 หลักที่สุ่ม)
                    2. รางวัล 3D (เลข 3 หลักที่สุ่ม)
                    3. รางวัล 2D (เลข 2 หลักที่สุ่ม)
                    4. ตัวเลขโชคดีอื่นๆ 5-7 ตัว (เลข 2 หลักแต่ละตัว)
                    
                    สำคัญ:
                    - ตัวเลขทั้งหมดต้องเป็นตัวเลขสุ่มโดยมีจำนวนหลักตามที่กำหนด
                    - อย่าใช้รูปแบบง่ายๆ และคาดเดาได้ เช่น 1234, 123, 12, 111 เป็นต้น
                    - แต่ละตัวเลขต้องสุ่มอย่างสมบูรณ์และแตกต่างกัน
                    
                    ใช้น้ำเสียงที่เป็นธรรมชาติ เป็นมิตร และน่าสนใจในภาษาไทย เพิ่มบันทึกเล็กๆ น้อยๆ หรือเคล็ดลับเกี่ยวกับกลยุทธ์การแทงโทเกลอินโดนีเซียที่ชาญฉลาด
                    """,
                    'header': f"<b>🇮🇩 คำทำนายลอตเตอรี่โทเกลอินโดนีเซียสำหรับวันที่ {today} 🇮🇩</b>",
                    'footer': "<i>โชคดีกับลอตเตอรี่โทเกลอินโดนีเซีย! โปรดเล่นอย่างมีความรับผิดชอบ</i>"
                },
                'zh': {
                    'system': "您是一位拥有多年经验的印度尼西亚多格彩票预测专家。用中文为玩家提供随机且有用的预测。始终生成完全随机的预测，不遵循任何简单模式。",
                    'user': f"""
                    提供{today}日印度尼西亚多格彩票的预测，使用随机数字。
                    
                    预测应包括：
                    1. 4D奖（4位随机数字）
                    2. 3D奖（3位随机数字）
                    3. 2D奖（2位随机数字）
                    4. 其他5-7个幸运数字（每个2位数字）
                    
                    重要事项：
                    - 所有数字必须是按要求具有相应位数的随机数字
                    - 不要使用简单和可预测的模式，如1234、123、12、111等
                    - 每个数字必须完全随机且彼此不同
                    
                    使用自然、友好和吸引人的中文语调。添加一些关于智能印度尼西亚多格彩票投注策略的小提示。
                    """,
                    'header': f"<b>🇮🇩 {today}印度尼西亚多格彩票预测 🇮🇩</b>",
                    'footer': "<i>祝您在印度尼西亚多格彩票中好运！请记得负责任地投注。</i>"
                }
            }
            
            # Check if language is supported, default to Vietnamese if not
            if language_code not in prompts:
                logger.warning(f"Language {language_code} not supported for Indonesian prediction, using Vietnamese")
                language_code = 'vi'
                
            # Get prompts for the requested language
            selected_prompt = prompts[language_code]
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": selected_prompt['system']},
                    {"role": "user", "content": selected_prompt['user']}
                ],
                max_tokens=1000
            )
            
            prediction_text = response.choices[0].message.content
            
            # Format the prediction with a header
            formatted_prediction = f"""
{selected_prompt['header']}

{prediction_text}

{selected_prompt['footer']}
"""
            
            logger.info(f"Generated new Indonesian lottery prediction in {language_code} for {today}")
            return formatted_prediction
            
        except Exception as e:
            logger.error(f"Error generating Indonesian prediction in {language_code}: {e}")
            error_messages = {
                'vi': f"❌ Đã xảy ra lỗi khi tạo dự đoán xổ số Indonesia. Vui lòng thử lại sau. Error: {str(e)}",
                'en': f"❌ An error occurred while generating the Indonesian lottery prediction. Please try again later. Error: {str(e)}",
                'th': f"❌ เกิดข้อผิดพลาดขณะสร้างคำทำนายลอตเตอรี่อินโดนีเซีย โปรดลองอีกครั้งในภายหลัง ข้อผิดพลาด: {str(e)}",
                'zh': f"❌ 生成印度尼西亚彩票预测时出错。请稍后再试。错误：{str(e)}"
            }
            return error_messages.get(language_code, error_messages['vi'])

    def get_daily_prediction(self, prediction_type='vietnam', language_code='vi'):
        """
        Get the daily prediction for a specific lottery type in the specified language. 
        If no prediction exists for today or it's after midnight, generate a new one.
        
        Args:
            prediction_type (str): The type of lottery prediction to get
                                  ('vietnam', '4d', 'thai', 'indo')
            language_code (str): The language code for the prediction
                               ('vi', 'en', 'th', 'zh')
        
        Returns:
            str: The formatted prediction text in the requested language
        """
        now = datetime.now()
        today = now.date()
        
        # Validate language code
        if language_code not in ['vi', 'en', 'th', 'zh']:
            logger.warning(f"Invalid language code: {language_code}, defaulting to Vietnamese")
            language_code = 'vi'
            
        # Log which lottery type and language we're retrieving
        logger.info(f"Retrieving {prediction_type} lottery prediction in {language_code}")
        
        # Check if prediction exists and is from today
        if (self.predictions[prediction_type][language_code]['date'] is None or 
            self.predictions[prediction_type][language_code]['date'] != today or 
            self.predictions[prediction_type][language_code]['prediction'] is None):
            
            # Generate new prediction based on the type and language
            logger.info(f"Generating new {prediction_type} lottery prediction in {language_code}")
            
            # Generate the prediction in the specified language
            if prediction_type == 'vietnam':
                prediction = self.generate_vietnam_prediction(language_code)
                logger.info(f"Generated new Vietnam prediction in {language_code} for {today}")
            elif prediction_type == '4d':
                prediction = self.generate_4d_prediction(language_code)
                logger.info(f"Generated new 4D prediction in {language_code} for {today}")
            elif prediction_type == 'thai':
                prediction = self.generate_thai_prediction(language_code)
                logger.info(f"Generated new Thai prediction in {language_code} for {today}")
            elif prediction_type == 'indo':
                prediction = self.generate_indo_prediction(language_code)
                logger.info(f"Generated new Indonesian prediction in {language_code} for {today}")
            else:
                # Default to Vietnam prediction if type is invalid
                prediction = self.generate_vietnam_prediction(language_code)
                logger.warning(f"Unknown prediction type: {prediction_type}, defaulting to Vietnam in {language_code}")
            
            # Store the prediction and update the date
            self.predictions[prediction_type][language_code]['prediction'] = prediction
            self.predictions[prediction_type][language_code]['date'] = today
            logger.info(f"Created new {prediction_type} prediction in {language_code} for {today}")
        else:
            logger.info(f"Using cached {prediction_type} prediction in {language_code} from {today}")
        
        # Return the prediction
        return self.predictions[prediction_type][language_code]['prediction']
