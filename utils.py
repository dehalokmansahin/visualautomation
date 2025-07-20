
import win32gui as wn
import win32api, win32con
import pyautogui as ag
from time import sleep,time
import asyncio
import io
from constants import CLICK_DELAY, MAX_WINDOW_WAIT, WINDOW_CHECK_INTERVAL, ICONS, APPROVAL_TIMEOUT,DEFAULT_CONFIDENCE
import cv2
import numpy as np
from typing import List, Tuple,Optional
import logging

logger = logging.getLogger(__name__)
def click_on_window(hwnd, x, y, click_times=1):
    try:
        sleep(1)
        # Validate window handle
        if not wn.IsWindow(hwnd):
            raise ValueError("Invalid window handle")
            
        # Get window state
        window_rect = wn.GetWindowRect(hwnd)
        client_rect = wn.GetClientRect(hwnd)
        
        # Calculate scaling
        scale_x = (window_rect[2] - window_rect[0]) / client_rect[2]
        scale_y = (window_rect[3] - window_rect[1]) / client_rect[3]
        
        # Apply scaling to coordinates
        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)
        
        # Convert to screen coordinates
        screen_x, screen_y = wn.ClientToScreen(hwnd, (scaled_x, scaled_y))
        
        # Set cursor position and perform clicks
        win32api.SetCursorPos((screen_x, screen_y))
        sleep(0.2)
        
        for _ in range(click_times):
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            sleep(0.1)
            
        return True
        
    except Exception as e:
        logger.error(f"Click operation failed: {str(e)}")
        return False

def scroll_down(clicks=3):
    for _ in range(clicks):
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -120, 0)
        sleep(0.5)

def is_fullscreen(hwnd):
    try:
        f = win32api.GetSystemMetrics
        return (wn.GetWindowRect(hwnd)[2:] == (f(0), f(1)))
    except:
        return False

def toggle_fullscreen(hwnd):
    win32api.SendMessage(hwnd, win32con.WM_SYSKEYDOWN, win32con.VK_RETURN, 0x20000000)
    sleep(1)
    win32api.SendMessage(hwnd, win32con.WM_SYSKEYUP, win32con.VK_RETURN, 0x20000000)

def wait_for_window(image_path,region ,max_wait=MAX_WINDOW_WAIT, check_interval=WINDOW_CHECK_INTERVAL,confidence=DEFAULT_CONFIDENCE):
    start_time = time.time()
    while time.time() - start_time < max_wait:
        window = ag.locateOnScreen(image_path,region=region, confidence=confidence)
        if window:
            return window
        sleep(check_interval)
    return None

async def process_approval(update, context, chat_id, screen_region, hwnd):
    approval_received = await wait_for_approval(chat_id, context)
    
    if approval_received:
        okButton = ag.locateCenterOnScreen(ICONS['OK_BUTTON'], region=screen_region, confidence=0.8)
        if okButton:
            click_on_window(hwnd, okButton.x, okButton.y, click_times=1)
            await context.bot.send_message(chat_id=chat_id, text="İşlem tamamlandı.")
        else:
            await context.bot.send_message(chat_id=chat_id, text="Son onay aşamasında OK butonu bulunamadı.")
    else:
        await context.bot.send_message(chat_id=chat_id, text="İşlem kullanıcı tarafından onaylanmadı veya zaman aşımına uğradı.")

async def send_screenshot(update, context):
    screenshot = ag.screenshot()
    
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img_byte_arr, caption="Anlık ekran görüntüsü")

async def wait_for_approval(chat_id, context):
    approval_event = asyncio.Event()
    
    try:
        await asyncio.wait_for(approval_event.wait(), timeout=APPROVAL_TIMEOUT)
        await context.bot.send_message(chat_id=chat_id, text="Onay alındı. İşlem devam ediyor.")
        return True
    except asyncio.TimeoutError:
        await context.bot.send_message(chat_id=chat_id, text="Onay zaman aşımına uğradı. İşlem iptal ediliyor.")
        return False

async def check_approval(update, context, approval_events):
    chat_id = update.effective_chat.id
    if chat_id in approval_events:
        approval_events[chat_id].set()
        await update.message.reply_text("Onay alındı. İşlem devam ediyor.")
    else:
        await update.message.reply_text("Şu anda onay bekleyen bir işlem yok.")

def get_window_region(hwnd):
    return (hwnd.left, hwnd.top, hwnd.width, hwnd.height)
 

def drag_and_drop(hwnd, start_x, start_y, end_x, end_y):
    # Pencere koordinatlarını ekran koordinatlarına dönüştür
    start_x, start_y = wn.ClientToScreen(hwnd, (start_x, start_y))
    end_x, end_y = wn.ClientToScreen(hwnd, (end_x, end_y))

    # Başlangıç pozisyonuna git
    win32api.SetCursorPos((start_x, start_y))
    sleep(0.2)

    # Sol mouse tuşuna bas
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    sleep(0.2)

    # Hedef pozisyona sürükle
    win32api.SetCursorPos((end_x, end_y))
    sleep(0.5)

    # Sol mouse tuşunu bırak
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    sleep(0.2)


async def send_screenshot_direct(update, context,screenshot):
    screenshot = screenshot
    
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img_byte_arr, caption="Ekran",read_timeout=30)

def find_template_location(template_path: str, screenshot_region: Tuple[int, int, int, int]) -> Optional[Tuple[int, int]]:
    """
    CV2 template matching kullanarak belirtilen bölgede şablonu arar ve en iyi eşleşmenin konumunu döndürür.

    :param template_path: Aranacak şablon görüntünün dosya yolu
    :param screenshot_region: Arama yapılacak bölgenin (x, y, width, height) tuple'ı
    :return: Eşleşen konumun (x, y) koordinatları veya None
    """
    # Şablonu yükle
    template = cv2.imread(template_path, 0)
    
    # Belirtilen bölgenin ekran görüntüsünü al
    screenshot = ag.screenshot(region=screenshot_region)
    screenshot_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    
    # Template matching uygula
    result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # Eşleşme eşik değeri (SellMerchant pattern için düşük threshold)
    threshold = 0.4
    
    if max_val >= threshold:
        # Şablon boyutlarını al
        h, w = template.shape
        
        # Merkez noktayı hesapla
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        
        # Global koordinatlara dönüştür
        global_x = screenshot_region[0] + center_x
        global_y = screenshot_region[1] + center_y
        
        return (global_x, global_y,h,w)
    else:
        return None 

def find_template_location_colored(template_path: str, screenshot_region: tuple) -> tuple:
    # Şablonu yükle
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    
    if template is None:
        raise FileNotFoundError(f"Template image not found: {template_path}")

    # Belirtilen bölgenin ekran görüntüsünü al
    screenshot = ag.screenshot(region=screenshot_region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Template matching uygula
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # Eşleşme eşik değeri (SellMerchant pattern için düşük threshold)
    threshold = 0.4
    
    if max_val >= threshold:
        # Şablon boyutlarını al
        h, w = template.shape[:2]
        
        # Merkez noktayı hesapla
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        
        # Global koordinatlara dönüştür
        global_x = screenshot_region[0] + center_x
        global_y = screenshot_region[1] + center_y
        
        return (global_x, global_y, h, w, max_val)
    else:
        return None


def preprocess_image(image):
    """Görüntüyü ön işlemden geçirir."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 200)
    return edges


def find_all_template_locations(
    template_path: str, 
    screenshot_region: Tuple[int, int, int, int],
    start_confidence: float = 0.70,
    min_confidence: float = 0.65,
    step: float = 0.02
) -> List[Tuple[int, int, int, int, float]]:
    """
    PyAutoGUI kullanarak belirtilen bölgede şablonun tüm eşleşmelerini bulur ve merkez noktalarını hesaplar.

    :param template_path: Aranacak şablon görüntünün dosya yolu
    :param screenshot_region: Arama yapılacak bölgenin (x, y, width, height) tuple'ı
    :param start_confidence: Başlangıç confidence değeri
    :param min_confidence: Minimum confidence değeri
    :param step: Confidence değerini düşürme adımı
    :return: Eşleşen konumların [(center_x, center_y, w, h, confidence), ...] listesi. Eşleşme yoksa boş liste.
    """
    all_matches = []
    current_confidence = start_confidence

    while current_confidence >= min_confidence:
        try:
            matches = list(ag.locateAllOnScreen(
                template_path,
                region=screenshot_region,
                confidence=current_confidence,
                grayscale=True  # Gri tonlamalı arama için eklendi
            ))
           
            if matches:
                for match in matches:
                    center_x = match.left + match.width // 2
                    center_y = match.top + match.height // 2
                    all_matches.append((center_x, center_y, match.width, match.height, current_confidence))
                break  # Eşleşme bulunduğunda döngüyü sonlandır
           
            current_confidence -= step
        except Exception as e:
            logger.error(f"Error in locateAllOnScreen: {str(e)}")
            break

    # Çakışan konumları birleştir ve en iyi skorları tut
    filtered_matches = []
    for match in sorted(all_matches, key=lambda x: x[4], reverse=True):
        if not any(is_significant_overlap(match, existing_match) for existing_match in filtered_matches):
            filtered_matches.append(match)

    logger.info(f"{len(filtered_matches)} eşleşme bulundu. Şablon: {template_path}, En iyi confidence: {current_confidence}")
    return filtered_matches

def is_significant_overlap(match1: Tuple[int, int, int, int, float], match2: Tuple[int, int, int, int, float], overlap_threshold: float = 0.7) -> bool:
    """
    İki eşleşme arasında önemli bir çakışma olup olmadığını kontrol eder.

    :param match1: Birinci eşleşme (x, y, w, h, confidence)
    :param match2: İkinci eşleşme (x, y, w, h, confidence)
    :param overlap_threshold: Çakışma için eşik değeri
    :return: Önemli çakışma varsa True, yoksa False
    """
    x1, y1, w1, h1, _ = match1
    x2, y2, w2, h2, _ = match2

    overlap_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
    overlap_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
    overlap_area = overlap_x * overlap_y
    
    min_area = min(w1 * h1, w2 * h2)
    
    return overlap_area / min_area > overlap_threshold

import ctypes
import time
from ctypes import wintypes

# Windows API constants
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002

# Load Windows API functions
user32 = ctypes.WinDLL('user32', use_last_error=True)

# Set up GetKeyboardLayout function
GetKeyboardLayout = user32.GetKeyboardLayout
GetKeyboardLayout.argtypes = [wintypes.DWORD]
GetKeyboardLayout.restype = wintypes.HKL

# Turkish Q keyboard layout
turkish_shift_chars = set('ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ!"^%&/()=?_:;>£')
turkish_altgr_chars = set('@€₺~æß´`\'"<>|¬½#$½{[]}')

# US QWERTY keyboard layout
us_shift_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+{}|:"<>?~')
us_altgr_chars = set()  # US QWERTY typically doesn't use AltGr, but you can add any if needed

def key_press(scancode, extended=False):
    flags = KEYEVENTF_SCANCODE
    if extended:
        flags |= 0x0001  # Extended key flag
    user32.keybd_event(0, scancode, flags, 0)

def key_release(scancode, extended=False):
    flags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP
    if extended:
        flags |= 0x0001  # Extended key flag
    user32.keybd_event(0, scancode, flags, 0)

def key_press_and_release(scancode, extended=False):
    key_press(scancode, extended)
    sleep(0.4)
    key_release(scancode, extended)

def key_press_with_modifier(scancode, modifier_scancode):
    key_press(modifier_scancode)
    sleep(0.05)
    key_press_and_release(scancode)
    sleep(0.05)
    key_release(modifier_scancode)

def get_keyboard_layout():
    hkl = GetKeyboardLayout(0)
    return hkl & 0xFFFF  # Get the language identifier

def type_text(text):
    # Determine the keyboard layout
    layout = get_keyboard_layout()
    print('layout'+str(layout))
    if layout == 1055:  # Turkish Q layout
        shift_chars = turkish_shift_chars
        altgr_chars = turkish_altgr_chars
        scancode_map = {
            'a': 0x1e, 'b': 0x30, 'c': 0x2e, 'ç': 0x2e, 'd': 0x20, 'e': 0x12, 'f': 0x21, 'g': 0x22,
            'ğ': 0x26, 'h': 0x23, 'ı': 0x17, 'i': 0x17, 'j': 0x24, 'k': 0x25, 'l': 0x26, 'm': 0x32,
            'n': 0x31, 'o': 0x18, 'ö': 0x19, 'p': 0x19, 'r': 0x13, 's': 0x1f, 'ş': 0x1f, 't': 0x14,
            'u': 0x16, 'ü': 0x16, 'v': 0x2f, 'y': 0x15, 'z': 0x2c,
            '0': 0x0b, '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06, '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0a,
            '!': 0x02, "'": 0x28, '+': 0x0d, '%': 0x06, '&': 0x07, '/': 0x08, '(': 0x09, ')': 0x0a,
            '=': 0x0d, '?': 0x0d, '_': 0x35, '-': 0x0c, '.': 0x34, ':': 0x33, ',': 0x33, ';': 0x33,
            '<': 0x56, '>': 0x56, ' ': 0x39, '\n': 0x1c  # Enter key
        }
    else:  # Default to US QWERTY layout
        shift_chars = us_shift_chars
        altgr_chars = us_altgr_chars
        scancode_map = {
            'a': 0x1e, 'b': 0x30, 'c': 0x2e, 'd': 0x20, 'e': 0x12, 'f': 0x21, 'g': 0x22,
            'h': 0x23, 'i': 0x17, 'j': 0x24, 'k': 0x25, 'l': 0x26, 'm': 0x32,
            'n': 0x31, 'o': 0x18, 'p': 0x19, 'q': 0x10, 'r': 0x13, 's': 0x1f, 't': 0x14,
            'u': 0x16, 'v': 0x2f, 'w': 0x11, 'x': 0x2d, 'y': 0x15, 'z': 0x2c,
            '0': 0x0b, '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06, '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0a,
            '!': 0x02, '@': 0x03, '#': 0x04, '$': 0x05, '%': 0x06, '^': 0x07, '&': 0x08, '*': 0x09, '(': 0x0a, ')': 0x0b,
            '-': 0x0c, '_': 0x0c, '=': 0x0d, '+': 0x0d, '[': 0x1a, '{': 0x1a, ']': 0x1b, '}': 0x1b,
            '\\': 0x2b, '|': 0x2b, ';': 0x27, ':': 0x27, "'": 0x28, '"': 0x28, ',': 0x33, '<': 0x33,
            '.': 0x34, '>': 0x34, '/': 0x35, '?': 0x35, '`': 0x29, '~': 0x29, ' ': 0x39, '\n': 0x1c  # Enter key
        }

    for char in text:
        if char == '\n':
            key_press_and_release(scancode_map['\n'])
        elif char in shift_chars:
            key_press_with_modifier(scancode_map[char.lower()], 0x2A)  # Left Shift
        elif char in altgr_chars:
            key_press_with_modifier(scancode_map[char.lower()], 0x38)  # Right Alt (AltGr)
        else:
            key_press_and_release(scancode_map[char.lower()])
        sleep(0.05)


# Load necessary Windows DLLs
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Windows API constants
SW_RESTORE = 9
KEYEVENTF_KEYUP = 0x0002

# Define necessary structures and types
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [("length", wintypes.UINT),
                ("flags", wintypes.UINT),
                ("showCmd", wintypes.UINT),
                ("ptMinPosition", wintypes.POINT),
                ("ptMaxPosition", wintypes.POINT),
                ("rcNormalPosition", RECT)]

def bring_window_to_foreground(hwnd):
    # Check if the window is minimized
    placement = WINDOWPLACEMENT()
    placement.length = ctypes.sizeof(placement)
    user32.GetWindowPlacement(hwnd, ctypes.byref(placement))
    
    if placement.showCmd == 2:  # SW_SHOWMINIMIZED
        user32.ShowWindow(hwnd, SW_RESTORE)
    
    # Try to bring the window to foreground
    user32.SetForegroundWindow(hwnd)
    
    # If SetForegroundWindow fails, try more aggressive methods
    if user32.GetForegroundWindow() != hwnd:
        # Get current foreground window
        current_foreground = user32.GetForegroundWindow()
        
        # Get the current thread ID
        current_thread = kernel32.GetCurrentThreadId()
        
        # Get the thread of the foreground window
        foreground_thread = user32.GetWindowThreadProcessId(current_foreground, None)
        
        # Attach both threads
        user32.AttachThreadInput(current_thread, foreground_thread, True)
        
        # Force focus and activate
        user32.SetFocus(hwnd)
        user32.SetActiveWindow(hwnd)
        
        # Try SetForegroundWindow again
        user32.SetForegroundWindow(hwnd)
        
        # Detach threads
        user32.AttachThreadInput(current_thread, foreground_thread, False)
    
    # Simulate Alt key press and release
    user32.keybd_event(0x12, 0, 0, 0)  # Alt key down
    sleep(0.05)
    user32.keybd_event(0x12, 0, KEYEVENTF_KEYUP, 0)  # Alt key up
    
    # Give some time for the window to come to the foreground
    sleep(0.1)
    
    # Ensure the window is not minimized
    user32.ShowWindow(hwnd, SW_RESTORE)
    
    # Optional: You can add a small delay here to ensure the window is fully in focus
    sleep(0.2)
    
    return user32.GetForegroundWindow() == hwnd

# Usage example:
# success = bring_window_to_foreground(hwnd)
# if success:
#     print("Window successfully brought to foreground")
# else:
#     print("Failed to bring window to foreground")