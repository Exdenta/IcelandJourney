# Configuration file for Iceland Image Scraper
# 
# To get better quality images, sign up for free API keys:
# 
# 1. Unsplash API (Free - 50 requests/hour):
#    - Go to: https://unsplash.com/developers
#    - Create an account and register a new application
#    - Copy your "Access Key" and paste it below
#
# 2. Pexels API (Free - 200 requests/hour):
#    - Go to: https://www.pexels.com/api/
#    - Create an account and generate an API key
#    - Copy your API key and paste it below

# API Keys - Replace with your actual keys
UNSPLASH_ACCESS_KEY = "YOUR_UNSPLASH_ACCESS_KEY"
PEXELS_API_KEY = "NbA6hD9ve1zk1jNeV5lMWrpDg9NjvSCknbsYpQru17GHobrM23Yf8qEg"

# Scraper Settings
MAX_IMAGES_PER_ATTRACTION = 3
MIN_IMAGE_SIZE = (800, 600)  # (width, height) in pixels
DOWNLOAD_DELAY = 1  # seconds between downloads
API_DELAY = 0.5  # seconds between API calls 