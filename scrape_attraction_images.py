import os
import requests
import json
import time
from urllib.parse import quote, urlencode
import hashlib
from PIL import Image
import io
import re
from bs4 import BeautifulSoup

# Directory to save images
os.makedirs("attraction_images", exist_ok=True)

# Import configuration
try:
    from config import (
        UNSPLASH_ACCESS_KEY, 
        PEXELS_API_KEY, 
        MAX_IMAGES_PER_ATTRACTION, 
        MIN_IMAGE_SIZE, 
        DOWNLOAD_DELAY, 
        API_DELAY
    )
except ImportError:
    # Fallback values if config.py doesn't exist
    UNSPLASH_ACCESS_KEY = "YOUR_UNSPLASH_ACCESS_KEY"
    PEXELS_API_KEY = "YOUR_PEXELS_API_KEY"
    MAX_IMAGES_PER_ATTRACTION = 3
    MIN_IMAGE_SIZE = (800, 600)
    DOWNLOAD_DELAY = 1
    API_DELAY = 0.5

class ImageScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def clean_attraction_name(self, attraction_name):
        """Clean attraction name for better search results"""
        # Remove underscores and common suffixes
        cleaned = attraction_name.replace('_', ' ')
        # Remove common file suffixes that might interfere with search
        suffixes_to_remove = [' waterfall', ' volcano', ' canyon', ' mountain', ' lagoon', ' beach', ' cliffs']
        for suffix in suffixes_to_remove:
            if cleaned.lower().endswith(suffix):
                cleaned = cleaned[:-len(suffix)]
        return cleaned.title()
    
    def get_search_terms(self, attraction_name):
        """Generate multiple search terms for better results"""
        base_name = self.clean_attraction_name(attraction_name)
        terms = [
            f"{base_name} Iceland",
            f"{attraction_name.replace('_', ' ')} Iceland",
            f"{base_name} Iceland landscape",
            f"{attraction_name.replace('_', ' ')} Iceland nature"
        ]
        return list(set(terms))  # Remove duplicates
    
    def validate_image(self, image_data, min_size=None):
        """Validate image quality and size"""
        if min_size is None:
            min_size = MIN_IMAGE_SIZE
            
        try:
            img = Image.open(io.BytesIO(image_data))
            width, height = img.size
            
            # Check minimum size
            if width < min_size[0] or height < min_size[1]:
                return False
                
            # Check if image is not corrupted
            img.verify()
            return True
        except Exception:
            return False
    
    def download_image(self, url, filename):
        """Download and validate image"""
        try:
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Get image data
            image_data = b''
            for chunk in response.iter_content(chunk_size=8192):
                image_data += chunk
            
            # Validate image
            if not self.validate_image(image_data):
                print(f"  Image validation failed for {filename}")
                return False
            
            # Save image
            with open(filename, 'wb') as f:
                f.write(image_data)
            
            print(f"  ✓ Downloaded: {filename}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to download {filename}: {str(e)}")
            return False
    
    def search_unsplash(self, query, per_page=5):
        """Search Unsplash for images"""
        if UNSPLASH_ACCESS_KEY == "YOUR_UNSPLASH_ACCESS_KEY":
            return []
            
        url = "https://api.unsplash.com/search/photos"
        params = {
            'query': query,
            'per_page': per_page,
            'orientation': 'landscape',
            'order_by': 'relevant'
        }
        headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            images = []
            for photo in data.get('results', []):
                images.append({
                    'url': photo['urls']['regular'],  # High quality but not too large
                    'source': 'unsplash',
                    'id': photo['id']
                })
            return images
        except Exception as e:
            print(f"  Unsplash search failed: {str(e)}")
            return []
    
    def search_pexels(self, query, per_page=5):
        """Search Pexels for images"""
        if PEXELS_API_KEY == "YOUR_PEXELS_API_KEY":
            return []
            
        url = "https://api.pexels.com/v1/search"
        params = {
            'query': query,
            'per_page': per_page,
            'orientation': 'landscape'
        }
        headers = {'Authorization': PEXELS_API_KEY}
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            images = []
            for photo in data.get('photos', []):
                images.append({
                    'url': photo['src']['large'],  # High quality
                    'source': 'pexels',
                    'id': photo['id']
                })
            return images
        except Exception as e:
            print(f"  Pexels search failed: {str(e)}")
            return []
    
    def search_wikimedia(self, query):
        """Search Wikimedia Commons for images using OpenSearch API"""
        try:
            # Use the OpenSearch API which is more reliable
            search_url = "https://commons.wikimedia.org/w/api.php"
            params = {
                'action': 'opensearch',
                'search': query,
                'limit': 5,
                'namespace': 6,  # File namespace
                'format': 'json'
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if len(data) < 2:
                return []
                
            titles = data[1]  # List of file titles
            images = []
            
            for title in titles[:3]:  # Limit to 3 images
                if title.startswith('File:'):
                    # Get the direct file URL
                    filename = title.replace('File:', '')
                    # Use the direct file URL from Wikimedia
                    img_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{quote(filename)}?width=1200"
                    images.append({
                        'url': img_url,
                        'source': 'wikimedia',
                        'id': filename
                    })
            
            return images
            
        except Exception as e:
            print(f"  Wikimedia search failed: {str(e)}")
            return []
    
    def search_simple_web(self, query):
        """Simple web scraping fallback for finding images"""
        try:
            # Use DuckDuckGo Images (more permissive than Google)
            search_url = "https://duckduckgo.com/"
            params = {
                'q': f"{query} filetype:jpg OR filetype:jpeg OR filetype:png",
                'iax': 'images',
                'ia': 'images'
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            images = []
            
            # Look for image URLs in the page
            img_tags = soup.find_all('img', src=True)
            for img in img_tags[:5]:
                src = img.get('src')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png']):
                    if src.startswith('http'):
                        images.append({
                            'url': src,
                            'source': 'web',
                            'id': hashlib.md5(src.encode()).hexdigest()[:8]
                        })
            
            return images[:2]  # Limit results
            
        except Exception as e:
            print(f"  Web search failed: {str(e)}")
            return []
    
    def scrape_images_for_attraction(self, attraction_name, max_images=None):
        """Main function to scrape images for an attraction"""
        if max_images is None:
            max_images = MAX_IMAGES_PER_ATTRACTION
            
        print(f"\n🔍 Searching for images: {attraction_name}")
        
        # Create attraction-specific directory
        attraction_dir = os.path.join("attraction_images", attraction_name)
        os.makedirs(attraction_dir, exist_ok=True)
        
        # Check if we already have enough images
        existing_images = [f for f in os.listdir(attraction_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if len(existing_images) >= max_images:
            print(f"  ✓ Already have {len(existing_images)} images for {attraction_name}")
            return
        
        search_terms = self.get_search_terms(attraction_name)
        all_images = []
        
        # Search multiple sources
        for term in search_terms[:2]:  # Limit search terms to avoid rate limiting
            print(f"  Searching for: {term}")
            
            # Try different sources
            sources = [
                ('Unsplash', self.search_unsplash),
                ('Pexels', self.search_pexels),
                ('Wikimedia', self.search_wikimedia),
                ('Web', self.search_simple_web)
            ]
            
            for source_name, search_func in sources:
                try:
                    images = search_func(term)
                    if images:
                        print(f"    Found {len(images)} images from {source_name}")
                        all_images.extend(images)
                        break  # Stop after first successful source
                except Exception as e:
                    print(f"    {source_name} search failed: {str(e)}")
                
                # Add delay to be respectful to APIs
                time.sleep(API_DELAY)
        
        # Download unique images
        downloaded = 0
        seen_urls = set()
        
        for img in all_images:
            if downloaded >= max_images:
                break
                
            url = img['url']
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Generate filename
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"{attraction_name}_{img['source']}_{url_hash}.jpg"
            filepath = os.path.join(attraction_dir, filename)
            
            if self.download_image(url, filepath):
                downloaded += 1
                time.sleep(DOWNLOAD_DELAY)  # Be respectful with downloads
        
        print(f"  📁 Downloaded {downloaded} images for {attraction_name}")
        
        if downloaded == 0:
            print(f"  ⚠️  No images could be downloaded for {attraction_name}")

def main():
    """Main function to scrape images for all attractions"""
    scraper = ImageScraper()
    
    print("🖼️  Iceland Attraction Image Scraper")
    print("=" * 50)
    
    # Check if API keys are set
    if UNSPLASH_ACCESS_KEY == "YOUR_UNSPLASH_ACCESS_KEY":
        print("⚠️  Unsplash API key not set. Get one free at: https://unsplash.com/developers")
    if PEXELS_API_KEY == "YOUR_PEXELS_API_KEY":
        print("⚠️  Pexels API key not set. Get one free at: https://www.pexels.com/api/")
    
    print("\n🚀 Starting image scraping...")
    
    # Get all attraction files
    attractions_dir = "attractions"
    if not os.path.exists(attractions_dir):
        print(f"❌ Attractions directory not found: {attractions_dir}")
        return
    
    attraction_files = [f for f in os.listdir(attractions_dir) if f.endswith('.md')]
    attraction_files.sort()
    
    print(f"📋 Found {len(attraction_files)} attractions to process")
    
    successful = 0
    failed = 0
    
    for filename in attraction_files:
        attraction_name = filename[:-3]  # Remove .md extension
        try:
            scraper.scrape_images_for_attraction(attraction_name)
            successful += 1
        except Exception as e:
            print(f"❌ Failed to process {attraction_name}: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Completed! Processed {successful} attractions successfully")
    if failed > 0:
        print(f"❌ Failed to process {failed} attractions")
    
    print(f"\n📁 Images saved in: attraction_images/")
    print("💡 Tip: Set API keys for better results and higher quality images!")

if __name__ == "__main__":
    main() 