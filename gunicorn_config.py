bind = '0.0.0.0:8000'  # The address and port Gunicorn should bind to
workers = 4  # The number of worker processes to spawn
module = 'app_main:app'  # Main application with full features (scraper + analytics + API)
errorlog = '/home/ubuntu/Website-Scrapper/gunicorn_error.log'