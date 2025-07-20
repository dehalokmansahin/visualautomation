#!/usr/bin/env python3
"""
Metin2 Stone Farming Bot - Complete SellMerchant Pattern Adoption
Exact SellMerchant automation patterns with template matching stone detection
Based on proven merchant automation methods and window handling
"""

import time
import signal
import sys
import os
from typing import Optional, Tuple, List, Dict
import pyautogui
import win32gui as wn
import logging
from utils import click_on_window, find_template_location_colored, bring_window_to_foreground, is_fullscreen, toggle_fullscreen, find_all_template_locations
from constants import CLICK_DELAY, MAX_WINDOW_WAIT, WINDOW_CHECK_INTERVAL, DEFAULT_CONFIDENCE

# Configure logging following merchant automation style
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

class StoneBot:
    """Stone farming bot for Metin2 using exact SellMerchant patterns"""
    
    def __init__(self):
        """Initialize bot with merchant automation configuration - SellMerchant pattern"""
        # SellMerchant pattern: Core state variables
        self.hwnd = None
        self.all_screen_region = None
        self.running = False
        
        # SellMerchant pattern: item_locations for caching (stone_locations in our case)
        self.stone_locations: Dict[str, List[Tuple[int, int, int, int, float]]] = {}
        
        # SellMerchant pattern: Statistics tracking
        self.stats = {
            'detections': 0,
            'clicks': 0,
            'failures': 0,
            'start_time': None
        }
        
        # SellMerchant pattern: Configuration with constants
        self.stone_template_path = "ornekresim.png"
        self.scan_interval = 1.0  # Scan every 1 second
        self.click_delay = CLICK_DELAY  # From constants.py (0.5s)
        self.max_failures = 5
        self.consecutive_failures = 0
        
        # Metin2 window titles for FindWindow
        self.metin2_window_titles = ["Rüya | 1-99", "R�ya | 1-99", "Metin2", "METIN2"]
        
        # SellMerchant pattern: Find window on initialization
        self.hwnd = self._find_metin2_window()
        if not self.hwnd:
            logger.error("Metin2 window not found! Please start Metin2 first.")
        else:
            logger.info(f"StoneBot initialized with window handle: {self.hwnd}")
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C graceful shutdown"""
        logger.info("Shutdown signal received...")
        self.running = False
    
    def _find_metin2_window(self) -> Optional[int]:
        """Find Metin2 window using SellMerchant pattern - return window handle"""
        try:
            logger.info("Searching for Metin2 window using SellMerchant pattern...")
            
            # SellMerchant pattern: Try each window title
            for window_title in self.metin2_window_titles:
                hwnd = wn.FindWindow(None, window_title)
                if hwnd:
                    logger.info(f"Found Metin2 window: '{window_title}' (HWND: {hwnd})")
                    return hwnd
            
            # Fallback: Enumerate windows if direct FindWindow fails
            def enum_windows_callback(hwnd, windows):
                if wn.IsWindowVisible(hwnd):
                    window_title = wn.GetWindowText(hwnd)
                    if any(title in window_title for title in self.metin2_window_titles):
                        # Filter out editor windows
                        if "cursor" not in window_title.lower() and "vs" not in window_title.lower():
                            windows.append((hwnd, window_title))
                            logger.info(f"Found potential window: '{window_title}' (HWND: {hwnd})")
                return True
            
            windows = []
            wn.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                hwnd, title = windows[0]
                logger.info(f"Using enumerated window: '{title}' (HWND: {hwnd})")
                return hwnd
            
            logger.error("No Metin2 window found")
            return None
            
        except Exception as e:
            logger.error(f"Finding Metin2 window failed: {e}")
            return None
    
    def reset_state(self):
        """Reset bot state - SellMerchant pattern for error recovery"""
        logger.info("Resetting bot state...")
        self.__init__()
    
    def ensure_stone_screen_region(self) -> bool:
        """Ensure screen region is valid - SellMerchant pattern"""
        try:
            if not self.hwnd or not wn.IsWindow(self.hwnd):
                logger.error("Invalid window handle, resetting...")
                self.hwnd = self._find_metin2_window()
                if not self.hwnd:
                    return False
            
            # SellMerchant pattern: Bring window to foreground
            bring_window_to_foreground(self.hwnd)
            
            # SellMerchant pattern: Handle fullscreen
            if is_fullscreen(self.hwnd):
                toggle_fullscreen(self.hwnd)
                time.sleep(1)  # SellMerchant uses 1 second delay
            
            # SellMerchant pattern: Update screen region
            window_rect = wn.GetWindowRect(self.hwnd)
            self.all_screen_region = window_rect  # SellMerchant uses GetWindowRect directly
            
            logger.debug(f"Screen region updated: {self.all_screen_region}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure screen region: {e}")
            return False
    
    def find_stone_in_screen(self, stone_name: str = "stone") -> bool:
        """Find stone using SellMerchant template matching pattern"""
        try:
            # SellMerchant pattern: Ensure screen region is valid
            if not self.ensure_stone_screen_region():
                logger.error("Screen region not available")
                return False
            
            # Check if template file exists
            if not os.path.exists(self.stone_template_path):
                logger.error(f"Template file not found: {self.stone_template_path}")
                return False
            
            # SellMerchant pattern: Primary detection with find_template_location_colored
            stone_detection = find_template_location_colored(
                template_path=self.stone_template_path,
                screenshot_region=self.all_screen_region
            )
            
            if stone_detection:
                # SellMerchant format: (global_x, global_y, h, w, max_val)
                center_x, center_y, h, w, confidence = stone_detection
                
                # SellMerchant pattern: Store in locations dictionary for caching
                self.stone_locations[stone_name] = [stone_detection]
                
                self.stats['detections'] += 1
                logger.info(f"Found stone at ({center_x}, {center_y}) - confidence: {confidence:.3f}")
                return True
            else:
                # SellMerchant pattern: Try fallback method with find_all_template_locations
                logger.debug("Primary detection failed, trying find_all_template_locations...")
                
                stone_locations = find_all_template_locations(
                    template_path=self.stone_template_path,
                    screenshot_region=self.all_screen_region
                )
                
                if stone_locations:
                    # SellMerchant pattern: Store all detections
                    self.stone_locations[stone_name] = stone_locations
                    self.stats['detections'] += len(stone_locations)
                    logger.info(f"Found {len(stone_locations)} stones with fallback method")
                    return True
                else:
                    logger.debug("No stones detected with either method")
                    return False
            
        except Exception as e:
            logger.error(f"Stone detection failed: {e}", exc_info=True)
            return False
    
    
    

    def process_single_stone(self, stone_name: str = "stone") -> bool:
        """Process single stone click - SellMerchant pattern from process_single_item"""
        try:
            # SellMerchant pattern: Ensure screen region is valid
            if not self.ensure_stone_screen_region():
                logger.error("Screen region not available")
                return False
            
            # SellMerchant pattern: Find stone in screen (like find_item_in_inventory)
            if not self.find_stone_in_screen(stone_name):
                logger.debug(f"Stone '{stone_name}' not found")
                return False
            
            # SellMerchant pattern: Get cached location and process
            if stone_name not in self.stone_locations or not self.stone_locations[stone_name]:
                logger.error(f"No cached location for stone '{stone_name}'")
                return False
            
            # SellMerchant pattern: Get first detection from cache
            stone_location = self.stone_locations[stone_name].pop(0)
            center_x, center_y, h, w, confidence = stone_location
            
            # SellMerchant pattern: Move mouse to target (like process_sell_item line 168)
            pyautogui.moveTo(center_x, center_y)
            logger.debug(f"Mouse moved to stone at ({center_x}, {center_y})")
            
            # FIX: click_on_window expects CLIENT coordinates, but we have SCREEN coordinates
            # Convert screen coordinates to client coordinates for click_on_window
            try:
                # Get window rectangle
                window_rect = wn.GetWindowRect(self.hwnd)
                
                # Convert screen to client coordinates  
                client_x = center_x - window_rect[0]
                client_y = center_y - window_rect[1]
                
                logger.debug(f"Screen coords: ({center_x}, {center_y}) -> Client coords: ({client_x}, {client_y})")
                
                # SellMerchant pattern: Click using click_on_window with CLIENT coordinates
                success = click_on_window(self.hwnd, x=client_x, y=client_y, click_times=1)
                
            except Exception as coord_error:
                logger.warning(f"Coordinate conversion failed: {coord_error}, trying direct click...")
                
                # Fallback: Direct pyautogui click at screen coordinates
                try:
                    pyautogui.click(center_x, center_y)
                    success = True
                    logger.debug("Fallback pyautogui click successful")
                except Exception as click_error:
                    logger.error(f"Direct click also failed: {click_error}")
                    success = False
            
            if success:
                self.stats['clicks'] += 1
                logger.info(f"Successfully clicked stone at ({center_x}, {center_y}) - confidence: {confidence:.3f}")
                
                # SellMerchant pattern: Apply click delay from constants
                time.sleep(self.click_delay)
                return True
            else:
                logger.error(f"Click failed at ({center_x}, {center_y})")
                self.stats['failures'] += 1
                return False
            
        except Exception as e:
            logger.error(f"Process single stone failed: {e}", exc_info=True)
            self.stats['failures'] += 1
            return False
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def run_farming(self):
        """Main farming loop using exact SellMerchant pattern"""
        if not self.hwnd:
            logger.error("Cannot start farming - Metin2 window not found")
            return
        
        logger.info("Starting stone farming with SellMerchant patterns...")
        logger.info("Press Ctrl+C to stop")
        
        self.running = True
        self.stats['start_time'] = time.time()
        stone_name = "stone"  # SellMerchant pattern: item name
        
        while self.running:
            try:
                # SellMerchant pattern: Process single stone (like process_single_item)
                success = self.process_single_stone(stone_name)
                
                if success:
                    logger.info("Successfully processed stone")
                    self.consecutive_failures = 0  # Reset failure counter
                else:
                    logger.debug("Stone processing failed")
                    self.consecutive_failures += 1
                    
                    # SellMerchant pattern: Reset state on consecutive failures
                    if self.consecutive_failures >= self.max_failures:
                        logger.warning(f"Too many consecutive failures ({self.max_failures}), resetting state...")
                        self.reset_state()
                        
                        # Check if reset was successful
                        if not self.hwnd:
                            logger.error("Reset failed - no window handle. Stopping bot.")
                            break
                        else:
                            logger.info("State reset successful, continuing...")
                            self.consecutive_failures = 0
                
                # SellMerchant pattern: Wait between operations
                time.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Unexpected error in farming loop: {e}", exc_info=True)
                self.stats['failures'] += 1
                self.consecutive_failures += 1
                
                # SellMerchant pattern: Reset on persistent errors
                if self.consecutive_failures >= self.max_failures:
                    logger.error("Too many consecutive errors, resetting state...")
                    self.reset_state()
                    if not self.hwnd:
                        logger.error("Reset failed after errors. Stopping bot.")
                        break
                    self.consecutive_failures = 0
                
                # Brief delay before retry
                time.sleep(1)
        
        self.cleanup()
    
    def cleanup(self):
        """Cleanup and show final statistics - SellMerchant pattern"""
        self.running = False
        
        if self.stats['start_time']:
            runtime = time.time() - self.stats['start_time']
            logger.info("=== StoneBot Session Statistics ===")
            logger.info(f"Runtime: {runtime:.1f} seconds")
            logger.info(f"Detections: {self.stats['detections']}")
            logger.info(f"Clicks: {self.stats['clicks']}")
            logger.info(f"Failures: {self.stats['failures']}")
            
            if self.stats['detections'] > 0:
                success_rate = (self.stats['clicks'] / self.stats['detections']) * 100
                logger.info(f"Success rate: {success_rate:.1f}%")
            
            # SellMerchant pattern: Calculate efficiency metrics
            if runtime > 0:
                clicks_per_minute = (self.stats['clicks'] / runtime) * 60
                logger.info(f"Clicks per minute: {clicks_per_minute:.1f}")
        
        logger.info("StoneBot stopped successfully - SellMerchant pattern")


def main():
    """Main entry point - SellMerchant error handling pattern"""
    try:
        logger.info("Starting StoneBot with SellMerchant patterns...")
        bot = StoneBot()
        
        if not bot.hwnd:
            logger.error("Failed to initialize bot - no window handle")
            sys.exit(1)
        
        # SellMerchant pattern: Start main loop
        bot.run_farming()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("StoneBot main function completed")


if __name__ == "__main__":
    main()