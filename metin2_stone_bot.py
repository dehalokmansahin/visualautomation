#!/usr/bin/env python3
"""
MVP 1: Metin2 Stone Farming Bot - Educational Implementation
Simple single-file implementation using Google Vertex AI Gemini
"""

import os
import time
import base64
import pyautogui
from google import genai
from google.genai.types import HttpOptions, Part
from PIL import Image
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleStoneBot:
    """MVP 1 Metin2 Stone Bot - Basic functionality only"""
    
    # MVP 1 Configuration
    MAX_DAILY_REQUESTS = 500
    REQUEST_DELAY = 3
    DAILY_COST_LIMIT = 1.0
    
    # Simple stone detection prompt
    STONE_DETECTION_PROMPT = """
    Look at this Metin2 game screen and find stones/minerals that can be mined.
    Return ONLY coordinates in this format: X,Y
    If multiple stones, return the closest to screen center.
    If no stones found, return coordinates of the closest stone to screen center.
    Example: 450,320
    """
    
    def __init__(self, project_id):
        """Initialize with minimal setup"""
        self.project_id = project_id
        self.request_count = 0
        self.setup_gemini()
        print("✅ MVP 1 Stone Bot initialized")
        print(f"📊 Daily request limit: {self.MAX_DAILY_REQUESTS}")
    
    def setup_gemini(self):
        """Basic Gemini setup"""
        try:
            self.client = genai.Client(
                http_options=HttpOptions(api_version="v1"),
                project=self.project_id,
                location="us-central1"
            )
            print("✅ Gemini client initialized")
        except Exception as e:
            print(f"❌ Failed to setup Gemini: {e}")
            raise
    
    def take_screenshot(self):
        """Simple full screen screenshot"""
        try:
            screenshot = pyautogui.screenshot()
            print(f"📸 Screenshot taken: {screenshot.size}")
            return screenshot
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None
    
    def image_to_base64(self, image):
        """Convert PIL image to base64 for Gemini"""
        try:
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            image_bytes = buffer.getvalue()
            return base64.b64encode(image_bytes).decode('utf-8')
        except Exception as e:
            print(f"❌ Image conversion failed: {e}")
            return None
    
    def analyze_screen(self, image):
        """Basic stone detection with Gemini Flash"""
        try:
            # Check daily limits
            if self.request_count >= self.MAX_DAILY_REQUESTS:
                print("⛔ Daily request limit reached!")
                return None
            
            # Convert image to base64
            image_b64 = self.image_to_base64(image)
            if not image_b64:
                return None
            
            # Create image part for Gemini
            image_part = Part.from_bytes(
                data=base64.b64decode(image_b64),
                mime_type="image/png"
            )
            
            # Send to Gemini Flash
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=[self.STONE_DETECTION_PROMPT, image_part]
            )
            
            self.request_count += 1
            print(f"🤖 Gemini request #{self.request_count}")
            
            # Extract response text
            if response.candidates and response.candidates[0].content:
                result = response.candidates[0].content.parts[0].text.strip()
                print(f"🔍 Gemini response: {result}")
                return result
            else:
                print("❌ No response from Gemini")
                return None
                
        except Exception as e:
            print(f"❌ Gemini analysis failed: {e}")
            return None
    
    def extract_coordinates(self, response):
        """Parse coordinates from Gemini response"""
        try:
            if not response or response == "NONE":
                return None, None
            
            # Simple coordinate parsing
            if "," in response:
                parts = response.split(",")
                if len(parts) >= 2:
                    x = int(parts[0].strip())
                    y = int(parts[1].strip())
                    
                    # Basic validation
                    screen_width, screen_height = pyautogui.size()
                    if 0 <= x <= screen_width and 0 <= y <= screen_height:
                        return x, y
                    else:
                        print(f"⚠️ Coordinates out of bounds: ({x}, {y})")
                        return None, None
            
            print(f"⚠️ Invalid coordinate format: {response}")
            return None, None
            
        except Exception as e:
            print(f"❌ Coordinate extraction failed: {e}")
            return None, None
    
    def click_stone(self, x, y):
        """Simple click with basic validation"""
        try:
            pyautogui.click(x, y)
            print(f"🖱️ Clicked stone at ({x}, {y})")
            time.sleep(1)  # Brief pause after clicking
        except Exception as e:
            print(f"❌ Click failed: {e}")
    
    def run_basic_loop(self):
        """Main execution loop - keep it simple"""
        print("🎮 Starting Metin2 Stone Bot MVP 1")
        print("⏹️ Press Ctrl+C to stop")
        
        try:
            while True:
                print(f"\n--- Cycle {self.request_count + 1} ---")
                
                # Check daily limits
                if self.request_count >= self.MAX_DAILY_REQUESTS:
                    print("⛔ Daily request limit reached, stopping...")
                    break
                
                # Take screenshot
                screenshot = self.take_screenshot()
                if not screenshot:
                    print("⚠️ Screenshot failed, retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                
                # Analyze for stones
                response = self.analyze_screen(screenshot)
                if not response:
                    print("⚠️ Analysis failed, retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                
                # Extract coordinates
                x, y = self.extract_coordinates(response)
                
                if x is not None and y is not None:
                    # Click on stone
                    self.click_stone(x, y)
                    print("✅ Stone clicked successfully")
                else:
                    print("🔍 No stones found, waiting...")
                
                # Delay between requests
                print(f"⏱️ Waiting {self.REQUEST_DELAY} seconds...")
                time.sleep(self.REQUEST_DELAY)
                
        except KeyboardInterrupt:
            print("\n⏹️ Bot stopped by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        
        print(f"📊 Total requests made: {self.request_count}")
        print("🏁 Bot session ended")

def test_mvp1():
    """Quick MVP 1 functionality test"""
    print("🧪 Testing MVP 1 Stone Bot...")
    
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT not set in environment")
        return False
    
    try:
        # Initialize bot
        bot = SimpleStoneBot(project_id)
        
        # Test screenshot
        img = bot.take_screenshot()
        if img:
            print(f"✅ Screenshot test passed: {img.size}")
        else:
            print("❌ Screenshot test failed")
            return False
        
        # Test image conversion
        b64 = bot.image_to_base64(img)
        if b64:
            print("✅ Image conversion test passed")
        else:
            print("❌ Image conversion test failed")
            return False
        
        print("🎮 Ready for Metin2 testing!")
        print("💡 Use bot.run_basic_loop() to start farming")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main entry point"""
    print("🚀 Metin2 Stone Bot MVP 1")
    print("=" * 40)
    
    # Check environment
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        print("❌ Please set GOOGLE_CLOUD_PROJECT in your .env file")
        print("💡 Example: GOOGLE_CLOUD_PROJECT=your-project-id")
        return
    
    # Run test first
    if not test_mvp1():
        print("❌ Tests failed, please check your setup")
        return
    
    # Ask user to start
    print("\n" + "=" * 40)
    start = input("🎯 Start stone farming? (y/N): ").lower().strip()
    
    if start == 'y':
        bot = SimpleStoneBot(project_id)
        bot.run_basic_loop()
    else:
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()