import os
from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename
from config.settings import Config
from models.database import DatabaseManager
from models.hotel_bot import HotelConciergeBot
import secrets

# Global bot instances cache
bot_instances = {}

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))
    
    # Initialize database
    db = DatabaseManager()
    
    @app.route('/')
    def home():
        """Main page with hotel selection"""
        hotels = db.get_all_hotels()
        return render_template('index.html', hotels=hotels)
    
    @app.route('/select_hotel', methods=['POST'])
    def select_hotel():
        """Handle hotel selection"""
        try:
            data = request.get_json()
            hotel_id = data.get('hotel_id')
            
            if not hotel_id:
                return jsonify({'error': 'No hotel selected'}), 400
            
            hotel = db.get_hotel_by_id(hotel_id)
            if not hotel:
                return jsonify({'error': 'Hotel not found'}), 404
            
            # Store hotel selection in session
            session['selected_hotel'] = hotel
            session['bot_initialized'] = False
            
            return jsonify({
                'success': True,
                'hotel': hotel,
                'message': f'Welcome to {hotel["name"]}! I\'m your personal concierge ready to assist you.'
            })
            
        except Exception as e:
            return jsonify({'error': f'Error selecting hotel: {str(e)}'}), 500
    
    @app.route('/chat', methods=['POST'])
    def chat():
        """Handle chat messages"""
        try:
            # Check if hotel is selected
            if 'selected_hotel' not in session:
                return jsonify({'error': 'Please select a hotel first'}), 400
            
            data = request.get_json()
            message = data.get('message', '')
            
            if not message:
                return jsonify({'error': 'No message provided'}), 400
            
            # Get or create bot for the selected hotel
            hotel = session['selected_hotel']
            bot = get_or_create_bot(hotel)
            
            # Process message
            response = bot.process_message(message, "Esteemed Guest")
            
            return jsonify({'response': response})
            
        except Exception as e:
            return jsonify({'error': f'Error processing message: {str(e)}'}), 500
    
    @app.route('/hotels', methods=['GET'])
    def get_hotels():
        """Get all hotels"""
        hotels = db.get_all_hotels()
        return jsonify({'hotels': hotels})
    
    @app.route('/admin/add_hotel', methods=['POST'])
    def add_hotel():
        """Add new hotel (admin function)"""
        try:
            data = request.get_json()
            hotel_data = {
                'name': data.get('name'),
                'location': data.get('location'), 
                'description': data.get('description'),
                'pdf_filename': data.get('pdf_filename')
            }
            
            hotel_id = db.add_hotel(hotel_data)
            return jsonify({'success': True, 'hotel_id': hotel_id})
            
        except Exception as e:
            return jsonify({'error': f'Error adding hotel: {str(e)}'}), 500
    
    @app.route('/history')
    def history():
        """Get booking and task history"""
        try:
            if 'selected_hotel' not in session:
                return jsonify({'error': 'No hotel selected'}), 400
            
            hotel = session['selected_hotel']
            bot = get_or_create_bot(hotel)
            
            bookings = bot.get_booking_history()
            tasks = bot.get_task_history()
            
            return jsonify({
                'bookings': bookings,
                'tasks': tasks
            })
            
        except Exception as e:
            return jsonify({'error': f'Error getting history: {str(e)}'}), 500
    
    @app.route('/reset_session', methods=['POST'])
    def reset_session():
        """Reset session to select different hotel"""
        session.clear()
        return jsonify({'success': True, 'message': 'Session reset successfully'})
    
    def get_or_create_bot(hotel_info):
        """Get or create bot instance for hotel"""
        hotel_id = hotel_info['id']
        
        # Check if bot already exists in cache
        if hotel_id not in bot_instances:
            pdf_path = os.path.join('pdfs', hotel_info.get('pdf_filename', ''))
            
            # Create new bot instance
            bot_instances[hotel_id] = HotelConciergeBot(
                gemini_api_key=os.getenv('GEMINI_API_KEY'),
                google_cloud_api_key=os.getenv('GOOGLE_CLOUD_API_KEY'),
                pdf_path=pdf_path,
                hotel_info=hotel_info
            )
        
        return bot_instances[hotel_id]
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))