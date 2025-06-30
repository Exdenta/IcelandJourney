# 🖼️ Iceland Attraction Image Scraper

A Python script to automatically download high-quality images for all Iceland attractions in your trip planner.

## Features

- **Multiple Sources**: Searches Unsplash, Pexels, and Wikimedia Commons
- **High Quality**: Downloads only high-resolution images (minimum 800x600)
- **Smart Naming**: Cleans attraction names for better search results
- **Organized Storage**: Creates separate folders for each attraction
- **Rate Limiting**: Respectful delays between API calls and downloads
- **Error Handling**: Robust error handling and retry logic
- **Image Validation**: Validates image quality and size before saving

## Quick Start (No API Keys Required)

The scraper works without API keys using Wikimedia Commons, but you'll get better results with free API keys.

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Scraper

```bash
python scrape_attraction_images.py
```

This will:
- Create an `attraction_images/` directory
- Download 3 images for each attraction
- Organize images in separate folders by attraction name

## Enhanced Setup (Recommended)

For better image quality and more results, get free API keys:

### 1. Get API Keys (Free)

**Unsplash API** (50 requests/hour):
1. Go to [unsplash.com/developers](https://unsplash.com/developers)
2. Create account → Register new application
3. Copy your "Access Key"

**Pexels API** (200 requests/hour):
1. Go to [pexels.com/api](https://www.pexels.com/api/)
2. Create account → Generate API key
3. Copy your API key

### 2. Configure API Keys

Edit `config.py` and replace the placeholder keys:

```python
UNSPLASH_ACCESS_KEY = "your_actual_unsplash_key_here"
PEXELS_API_KEY = "your_actual_pexels_key_here"
```

### 3. Run Enhanced Scraper

```bash
python scrape_attraction_images.py
```

## Configuration Options

Edit `config.py` to customize:

```python
MAX_IMAGES_PER_ATTRACTION = 3      # Number of images per attraction
MIN_IMAGE_SIZE = (800, 600)        # Minimum image dimensions
DOWNLOAD_DELAY = 1                 # Seconds between downloads
API_DELAY = 0.5                   # Seconds between API calls
```

## Output Structure

```
attraction_images/
├── blue_lagoon/
│   ├── blue_lagoon_unsplash_a1b2c3d4.jpg
│   ├── blue_lagoon_pexels_e5f6g7h8.jpg
│   └── blue_lagoon_wikimedia_i9j0k1l2.jpg
├── gullfoss_waterfall/
│   ├── gullfoss_waterfall_unsplash_m3n4o5p6.jpg
│   └── gullfoss_waterfall_wikimedia_q7r8s9t0.jpg
└── ...
```

## Troubleshooting

**No images downloaded?**
- Check your internet connection
- Verify API keys are correct (if using)
- Some attractions may have limited available images

**PIL/Pillow import error?**
```bash
pip install Pillow==10.1.0
```

**Rate limiting errors?**
- The scraper includes delays to respect API limits
- Free tier limits: Unsplash (50/hour), Pexels (200/hour)
- Wikimedia has no rate limits

## Supported Attractions

The scraper automatically processes all `.md` files in the `attractions/` directory:

- Blue Lagoon
- Gullfoss Waterfall  
- Geysir Geothermal Area
- Jökulsárlón Glacier Lagoon
- Reynisfjara Black Sand Beach
- Seljalandsfoss Waterfall
- Skógafoss Waterfall
- And many more...

## Legal & Ethics

- All images are sourced from platforms that allow usage
- Unsplash: Free to use under Unsplash License
- Pexels: Free to use under Pexels License  
- Wikimedia: Various Creative Commons licenses
- Scraper includes respectful delays and rate limiting
- For commercial use, verify individual image licenses

## Tips for Best Results

1. **Use API keys** for higher quality and more diverse images
2. **Run during off-peak hours** to avoid rate limits
3. **Check image quality** manually after download
4. **Customize search terms** in the script for specific needs
5. **Respect rate limits** - don't modify delay settings too aggressively

## Need Help?

- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify your API keys are correctly set in `config.py`
- Make sure the `attractions/` directory exists with `.md` files
- Check the console output for specific error messages 