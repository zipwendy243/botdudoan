from datetime import datetime
from app import db

class PGSoftGame(db.Model):
    """Model for storing PGSoft game information."""
    __tablename__ = 'pgsoft_games'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    rtp = db.Column(db.String(20))
    detail_url = db.Column(db.String(500))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PGSoftGame {self.name}>'
    
    def to_dict(self):
        """Convert game to dictionary."""
        return {
            'id': self.id,
            'game_id': self.game_id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'rtp': self.rtp,
            'detail_url': self.detail_url,
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S') if self.last_updated else None
        }
    
    @classmethod
    def is_cache_valid(cls, game_id):
        """Check if the cached data for a game is still valid (less than a month old)."""
        game = cls.query.filter_by(game_id=game_id).first()
        if not game:
            return False
            
        now = datetime.utcnow()
        delta = now - game.last_updated
        # Cache is valid for one month (30 days)
        return delta.days < 30