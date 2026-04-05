"""Application entry point."""
import os
from app import create_app

# Get environment
env = os.getenv('FLASK_ENV', 'development')

# Create app
app = create_app(env)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True') == 'True'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
