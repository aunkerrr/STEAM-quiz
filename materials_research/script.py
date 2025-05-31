import os
import requests
from PIL import Image
from io import BytesIO
import time
import json

# All the famous people from your decision tree
FAMOUS_PEOPLE = [
    "Albert Einstein",
    "Niels Bohr",
    "Richard Feynman",
    "Isaac Newton",
    "Charles Darwin",
    "Marie Curie",
    "Rachel Carson",
    "George Washington Carver",
    "Louis Pasteur",
    "Alan Turing",
    "John von Neumann",
    "David Hilbert",
    "Thomas Edison",
    "Leonardo da Vinci",
    "Michelangelo",
    "Vincent van Gogh",
    "Pablo Picasso",
    "Ada Lovelace",
    "Grace Hopper",
    "Pythagoras",
    "Katherine Johnson",
    "Nikola Tesla",
    "Alexander Graham Bell",
    "Steve Jobs",
    "Frank Lloyd Wright",
    "Imhotep"
]

class ImageDownloader:
    def __init__(self, output_folder="famous_people_images"):
        self.output_folder = output_folder
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Create output directory
        os.makedirs(self.output_folder, exist_ok=True)

    def search_wikimedia_commons(self, person_name):
        """Search Wikimedia Commons for person images"""
        try:
            # Use Wikimedia Commons API to search for images
            search_url = "https://commons.wikimedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': f'{person_name} portrait',
                'srnamespace': 6,  # File namespace
                'srlimit': 5
            }

            response = self.session.get(search_url, params=params, timeout=10)
            data = response.json()

            if 'query' in data and 'search' in data['query']:
                for result in data['query']['search']:
                    title = result['title']
                    if any(ext in title.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        image_url = self.get_wikimedia_image_url(title)
                        if image_url:
                            return image_url
            return None

        except Exception as e:
            print(f"Error searching Wikimedia for {person_name}: {e}")
            return None

    def get_wikimedia_image_url(self, file_title):
        """Get direct URL for Wikimedia Commons image"""
        try:
            api_url = "https://commons.wikimedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'titles': file_title,
                'prop': 'imageinfo',
                'iiprop': 'url|size',
                'iiurlwidth': 400  # Request 400px width
            }

            response = self.session.get(api_url, params=params, timeout=10)
            data = response.json()

            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if 'imageinfo' in page_data:
                    imageinfo = page_data['imageinfo'][0]
                    # Prefer thumbnail URL, fallback to original
                    return imageinfo.get('thumburl', imageinfo.get('url'))

            return None

        except Exception as e:
            print(f"Error getting image URL for {file_title}: {e}")
            return None

    def download_and_process_image(self, url, person_name):
        """Download image and process it to meet requirements"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            # Open image with PIL
            img = Image.open(BytesIO(response.content))

            # Convert to RGB if necessary (for JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # Resize to 400x400 maintaining aspect ratio
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)

            # Create a square image with padding if needed
            if img.size != (400, 400):
                new_img = Image.new('RGB', (400, 400), (255, 255, 255))
                # Center the image
                x = (400 - img.size[0]) // 2
                y = (400 - img.size[1]) // 2
                new_img.paste(img, (x, y))
                img = new_img

            # Save as WebP first (better compression)
            safe_name = "".join(c for c in person_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')

            webp_path = os.path.join(self.output_folder, f"{safe_name}.webp")
            img.save(webp_path, 'WEBP', quality=85, optimize=True)

            # Check file size
            if os.path.getsize(webp_path) <= 100 * 1024:  # 100KB
                print(f"✓ Downloaded {person_name} -> {webp_path}")
                return True
            else:
                # If WebP is too large, try JPEG with lower quality
                jpeg_path = os.path.join(self.output_folder, f"{safe_name}.jpg")
                img.save(jpeg_path, 'JPEG', quality=70, optimize=True)
                os.remove(webp_path)  # Remove the large WebP

                if os.path.getsize(jpeg_path) <= 100 * 1024:
                    print(f"✓ Downloaded {person_name} -> {jpeg_path}")
                    return True
                else:
                    os.remove(jpeg_path)
                    print(f"✗ Could not compress {person_name} image under 100KB")
                    return False

        except Exception as e:
            print(f"✗ Error processing {person_name}: {e}")
            return False

    def download_all_images(self):
        """Download images for all famous people"""
        print(f"Starting download of {len(FAMOUS_PEOPLE)} famous people images...")
        print(f"Output folder: {os.path.abspath(self.output_folder)}")
        print("-" * 60)

        successful = 0
        failed = []

        for i, person in enumerate(FAMOUS_PEOPLE, 1):
            print(f"[{i}/{len(FAMOUS_PEOPLE)}] Searching for {person}...")

            # Check if already exists
            safe_name = "".join(c for c in person if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')

            webp_path = os.path.join(self.output_folder, f"{safe_name}.webp")
            jpeg_path = os.path.join(self.output_folder, f"{safe_name}.jpg")

            if os.path.exists(webp_path) or os.path.exists(jpeg_path):
                print(f"  → Already exists, skipping...")
                successful += 1
                continue

            # Search for image
            image_url = self.search_wikimedia_commons(person)

            if image_url:
                if self.download_and_process_image(image_url, person):
                    successful += 1
                else:
                    failed.append(person)
            else:
                print(f"✗ No suitable image found for {person}")
                failed.append(person)

            # Be respectful to the API
            time.sleep(1)

        print("-" * 60)
        print(f"Download complete!")
        print(f"Successful: {successful}/{len(FAMOUS_PEOPLE)}")
        if failed:
            print(f"Failed: {len(failed)} - {', '.join(failed)}")

def main():
    """Main function to run the image downloader"""
    downloader = ImageDownloader()
    downloader.download_all_images()

    print(f"\nImages saved to: {os.path.abspath(downloader.output_folder)}")
    print("\nImage specifications:")
    print("- Format: WebP (preferred) or JPEG (fallback)")
    print("- Resolution: 400x400px")
    print("- File size: Under 100KB")

if __name__ == "__main__":
    # Check required modules
    try:
        import requests
        from PIL import Image
    except ImportError as e:
        print("Missing required modules. Please install them:")
        print("pip install requests pillow")
        exit(1)

    main()
