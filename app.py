import os
import logging
from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the base for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# Import these after db is defined to avoid circular imports
from bot_handler import TelegramBotHandler
from prediction_service import PredictionService

# Initialize the Telegram bot handler
telegram_bot_handler = TelegramBotHandler()

# Initialize the prediction service for direct use
prediction_service = PredictionService()

@app.route('/')
def index():
    """Render the homepage with basic bot information."""
    # Get 4 popular games for the homepage
    popular_games = [
        {
            'name': 'Mahjong Ways 2',
            'image': 'https://pgsoftlb.com/wp-content/uploads/2021/02/Mahjong-Ways-2-min-1.jpg',
            'rtp': '96.95%'
        },
        {
            'name': 'Fortune Mouse',
            'image': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/fortune-mouse-1536x864.jpg',
            'rtp': '96.75%'
        },
        {
            'name': 'Lucky Neko',
            'image': 'https://pgslot.cc/wp-content/uploads/2020/12/lucky-neko.jpg',
            'rtp': '96.74%'
        },
        {
            'name': 'Treasures of Aztec',
            'image': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/treasures-of-aztec-1536x864.jpg',
            'rtp': '96.88%'
        }
    ]
    
    return render_template('index.html', popular_games=popular_games)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming updates from Telegram."""
    try:
        update = request.get_json()
        logger.debug(f"Received update: {update}")
        return telegram_bot_handler.handle_update(update)
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return {"status": "error", "message": str(e)}, 500

@app.route('/test-prediction')
def test_prediction():
    """Generate a test prediction to verify the OpenAI integration."""
    try:
        # Get lottery type from query parameters, default to Vietnam
        lottery_type = request.args.get('type', 'vietnam')
        
        # Get a prediction from the service based on the selected type
        prediction = prediction_service.get_daily_prediction(lottery_type)
        
        # Return prediction as HTML for better display
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dự Đoán Xổ Số</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <style>
                body {{ padding: 20px; }}
                .prediction-box {{ 
                    background-color: #212529; 
                    padding: 20px; 
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .type-btn {{
                    margin-right: 10px;
                    margin-bottom: 10px;
                }}
                .type-active {{
                    border: 2px solid #fff;
                }}
            </style>
        </head>
        <body class="bg-dark text-light">
            <div class="container">
                <h1 class="mt-4 mb-4">Dự Đoán Xổ Số</h1>
                
                <div class="mb-4">
                    <h3>Chọn loại xổ số:</h3>
                    <a href="/test-prediction?type=vietnam" class="btn btn-primary type-btn {'type-active' if lottery_type == 'vietnam' else ''}">🇻🇳 Việt Nam</a>
                    <a href="/test-prediction?type=4d" class="btn btn-success type-btn {'type-active' if lottery_type == '4d' else ''}">🇸🇬 4D (SG/MY)</a>
                    <a href="/test-prediction?type=thai" class="btn btn-warning type-btn {'type-active' if lottery_type == 'thai' else ''}">🇹🇭 Thái Lan</a>
                    <a href="/test-prediction?type=indo" class="btn btn-info type-btn {'type-active' if lottery_type == 'indo' else ''}">🇮🇩 Indonesia</a>
                </div>
                
                <div class="prediction-box">
                    {prediction.replace('<b>', '<h2>').replace('</b>', '</h2>').replace('<i>', '<p class="text-muted">').replace('</i>', '</p>')}
                </div>
                
                <div class="text-center mt-4">
                    <a href="/" class="btn btn-secondary">Về trang chủ</a>
                    <a href="/test-prediction?type={lottery_type}" class="btn btn-primary ms-2">Tạo dự đoán mới</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    except Exception as e:
        logger.error(f"Error generating test prediction: {e}")
        return f"Lỗi: {str(e)}", 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return {"status": "ok"}
    
@app.route('/test-slot-game')
def test_slot_game():
    """Test the PGSoft slot game information retrieval."""
    try:
        from slot_game_service import SlotGameService
        
        # Initialize the service
        slot_service = SlotGameService()
        
        # Get the game name from the query parameter, default to Mahjong Ways 2
        game_name = request.args.get('game', 'Mahjong Ways 2')
        
        # Test popular games list
        games_result = slot_service.get_popular_games_list()
        
        # Test specific game info
        game_info = slot_service.get_game_info(game_name)
        
        return jsonify({
            "popular_games": games_result.get('text', '') if isinstance(games_result, dict) else games_result,
            "game_info": {
                "text": game_info.get('text', '') if isinstance(game_info, dict) else game_info,
                "image_url": game_info.get('image_url', '') if isinstance(game_info, dict) else None
            }
        })
    except Exception as e:
        logger.error(f"Error in test_slot_game: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
        
@app.route('/test-mahjong')
def test_mahjong():
    """Test page to display Mahjong Ways 2 information and image."""
    try:
        from slot_game_service import SlotGameService
        import re
        
        # Initialize the service
        slot_service = SlotGameService()
        
        # Get Mahjong Ways 2 info
        game_name = request.args.get('game', 'Mahjong Ways 2')
        game_info_result = slot_service.get_game_info(game_name)
        
        # Extract the information
        if isinstance(game_info_result, dict):
            text = game_info_result.get('text', '')
            image_url = game_info_result.get('image_url', '')
        else:
            text = game_info_result
            image_url = None
            
        # Try to extract RTP from the text
        rtp_match = re.search(r'RTP: ([0-9.]+%|N/A)', text)
        rtp = rtp_match.group(1) if rtp_match else 'N/A'
            
        # Get related games information for the template
        related_games = [
            {
                'name': 'Mahjong Ways 2',
                'image': 'https://pgsoftlb.com/wp-content/uploads/2021/02/Mahjong-Ways-2-min-1.jpg',
            },
            {
                'name': 'Fortune Mouse',
                'image': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/fortune-mouse-1536x864.jpg',
            },
            {
                'name': 'Lucky Neko',
                'image': 'https://pgslot.cc/wp-content/uploads/2020/12/lucky-neko.jpg',
            },
            {
                'name': 'Treasures of Aztec',
                'image': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/treasures-of-aztec-1536x864.jpg',
            }
        ]
        
        # Render the template
        return render_template(
            'game_info.html',
            game_name=game_name,
            game_info=text,
            image_url=image_url,
            rtp=rtp,
            related_games=related_games
        )
    except Exception as e:
        logger.error(f"Error in test_mahjong: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    # Start the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
