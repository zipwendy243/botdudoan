import logging
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from models import PGSoftGame
from app import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PGSoftScraper:
    """Service for scraping PGSoft game data from their official website."""
    
    BASE_URL = "https://www.pgsoft.com/en/games/"
    
    def __init__(self):
        """Initialize the PGSoft scraper."""
        logger.info("PGSoft scraper initialized")
    
    def fetch_game_list(self):
        """
        Fetch the list of PGSoft games from their official website.
        
        Returns:
            list: List of game data dictionaries
        """
        try:
            logger.info(f"Fetching game list from {self.BASE_URL}")
            response = requests.get(self.BASE_URL)
            if response.status_code != 200:
                logger.error(f"Failed to fetch game list: {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            game_elements = soup.select('.game-card')
            
            games = []
            for game_element in game_elements:
                try:
                    # Extract game details
                    game_link = game_element.find('a')
                    if not game_link:
                        continue
                        
                    # Get href attribute safely
                    detail_url = None
                    if game_link and hasattr(game_link, 'attrs') and 'href' in game_link.attrs:
                        detail_url = game_link['href']
                    
                    if not detail_url:
                        continue
                        
                    game_id = self._extract_game_id(detail_url)
                    
                    # Get src attribute safely
                    image_element = game_element.find('img')
                    image_url = None
                    if image_element and hasattr(image_element, 'attrs') and 'src' in image_element.attrs:
                        image_url = image_element['src']
                    
                    name_element = game_element.select_one('.game-card-title')
                    name = name_element.text.strip() if name_element else "Unknown Game"
                    
                    # Add to games list
                    games.append({
                        'game_id': game_id,
                        'name': name,
                        'image_url': image_url,
                        'detail_url': detail_url,
                    })
                except Exception as e:
                    logger.error(f"Error parsing game element: {e}")
                    continue
            
            logger.info(f"Found {len(games)} PGSoft games")
            return games
        except Exception as e:
            logger.error(f"Failed to fetch game list: {e}")
            return []
    
    def fetch_game_details(self, game_id):
        """
        Fetch detailed information about a specific PGSoft game.
        
        Args:
            game_id (str): The ID of the game to fetch details for
            
        Returns:
            dict: Game details including description and RTP
        """
        try:
            # Check if we have valid cached data
            cached_game = PGSoftGame.query.filter_by(game_id=game_id).first()
            if cached_game and PGSoftGame.is_cache_valid(game_id):
                logger.info(f"Using cached data for game {game_id}")
                return cached_game.to_dict()
            
            # Format the game name from the ID for better display
            formatted_name = self._format_game_name_from_id(game_id)
            
            # Build the detail URL
            detail_url = f"{self.BASE_URL}{game_id}/"
            logger.info(f"Fetching game details from {detail_url}")
            
            # Set fallback data
            game_data = {
                'game_id': game_id,
                'name': formatted_name,
                'description': "",
                'image_url': self._get_fallback_image_url(game_id),
                'rtp': "N/A",
                'detail_url': detail_url,
                'last_updated': datetime.utcnow()
            }
            
            try:
                response = requests.get(detail_url, allow_redirects=True, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract game information
                    name_element = soup.select_one('.game-detail-title h1')
                    if name_element:
                        game_data['name'] = name_element.text.strip()
                    
                    image_element = soup.select_one('.game-banner img')
                    if image_element and hasattr(image_element, 'attrs') and 'src' in image_element.attrs:
                        game_data['image_url'] = image_element['src']
                    
                    description_element = soup.select_one('.game-description')
                    if description_element:
                        game_data['description'] = description_element.text.strip()
                    
                    # Try to find RTP information
                    rtp = self._extract_rtp_from_page(soup)
                    if rtp != "N/A":
                        game_data['rtp'] = rtp
            except Exception as e:
                logger.error(f"Error parsing game details page: {e}")
            
            # Update or create the database record
            self._update_game_database(game_data)
            
            return game_data
        except Exception as e:
            logger.error(f"Failed to fetch game details for {game_id}: {e}")
            
            # Return basic data even if fetching fails
            basic_data = {
                'game_id': game_id,
                'name': self._format_game_name_from_id(game_id),
                'description': "",
                'image_url': self._get_fallback_image_url(game_id),
                'rtp': "N/A",
                'detail_url': f"{self.BASE_URL}{game_id}/",
                'last_updated': datetime.utcnow()
            }
            
            # Try to update database with basic data
            try:
                self._update_game_database(basic_data)
            except Exception:
                pass
                
            return basic_data
            
    def _format_game_name_from_id(self, game_id):
        """Format a readable game name from the game ID."""
        if not game_id:
            return "Unknown Game"
            
        # Remove pg-soft- prefix if present
        name = game_id.replace('pg-soft-', '')
        
        # Replace hyphens with spaces
        name = name.replace('-', ' ')
        
        # Capitalize words
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name
        
    def _get_fallback_image_url(self, game_id):
        """Get a fallback image URL based on the game ID."""
        # Mapping of game IDs to known image URLs
        image_mapping = {
            'pg-soft-mahjong-ways': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/mahjong-ways-1536x864.jpg',
            'pg-soft-mahjong-ways-2': 'https://pgsoftlb.com/wp-content/uploads/2021/02/Mahjong-Ways-2-min-1.jpg',
            'pg-soft-fortune-mouse': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/fortune-mouse-1536x864.jpg',
            'pg-soft-lucky-neko': 'https://pgslot.cc/wp-content/uploads/2020/12/lucky-neko.jpg',
            'pg-soft-dragon-tiger-luck': 'https://www.pgslot9999.com/wp-content/uploads/2020/02/dragon-tiger-luck-1536x864.jpg'
        }
        
        # Return specific image URL if available
        if game_id in image_mapping:
            return image_mapping[game_id]
            
        # Default fallback for games not in the mapping
        return "https://www.pgslot9999.com/wp-content/uploads/2020/02/pgslot99-01.jpg"
    
    def _extract_game_id(self, url):
        """Extract the game ID from a URL."""
        if not url:
            return None
            
        # Extract the game ID from the URL path
        # Example URL: https://www.pgsoft.com/en/games/pg-soft-mahjong-ways/
        match = re.search(r'/games/([^/]+)/?', url)
        if match:
            return match.group(1)
        return None
    
    def _extract_rtp_from_page(self, soup):
        """Extract the RTP information from the game detail page."""
        try:
            # Look for RTP in various parts of the page
            # Method 1: Look for specific sections that might contain RTP
            rtp_sections = soup.select('.game-info-item')
            for section in rtp_sections:
                text = section.text.lower()
                if 'rtp' in text:
                    match = re.search(r'(\d+\.\d+)%', text)
                    if match:
                        return f"{match.group(1)}%"
            
            # Method 2: Look for RTP in the game description
            description = soup.select_one('.game-description')
            if description:
                text = description.text.lower()
                if 'rtp' in text:
                    match = re.search(r'rtp\D*(\d+\.\d+)%', text, re.IGNORECASE)
                    if match:
                        return f"{match.group(1)}%"
            
            # Method 3: Search for any mention of percentage in game features
            features = soup.select('.game-feature')
            for feature in features:
                text = feature.text.lower()
                if 'rtp' in text or 'return to player' in text:
                    match = re.search(r'(\d+\.\d+)%', text)
                    if match:
                        return f"{match.group(1)}%"
            
            return "N/A"  # RTP not found
        except Exception as e:
            logger.error(f"Failed to extract RTP: {e}")
            return "N/A"
    
    def _update_game_database(self, game_data):
        """Update or create a game record in the database."""
        try:
            game = PGSoftGame.query.filter_by(game_id=game_data['game_id']).first()
            
            if game:
                # Update existing record
                for key, value in game_data.items():
                    setattr(game, key, value)
            else:
                # Create new record
                game = PGSoftGame(**game_data)
                db.session.add(game)
                
            db.session.commit()
            logger.info(f"Updated database for game {game_data['name']}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update database: {e}")