import sys
import os
import requests

import random
import string
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor


class ShutdownSignal(Exception):
    """Custom exception to signal a clean shutdown from a command."""
    pass

class RestartSignal(Exception):
    """Custom exception to signal a clean restart from a command."""
    pass


class BotUtils:
    """
    A class for standalone utility functions used by the bot.
    """
    VERSION = "2.3.3"

    @staticmethod
    def load_messages(filename="messages.txt"):
        """Loads messages from a file, stripping whitespace."""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                messages = [line.strip() for line in f]
            return messages
        except FileNotFoundError:
            return ["Welcome, {name}!"]

    _blacklist_cache = None
    _blacklist_mtime = 0

    @staticmethod
    def load_blacklist(filename="blacklist.txt"):
        """Loads a blacklist from a file, converting to lowercase. Caches based on file modification time."""
        try:
            mtime = os.path.getmtime(filename)
        except FileNotFoundError:
            return []
            
        if BotUtils._blacklist_cache is not None and BotUtils._blacklist_mtime == mtime:
            return BotUtils._blacklist_cache
            
        try:
            with open(filename, "r", encoding="utf-8") as f:
                BotUtils._blacklist_cache = [line.strip().lower() for line in f]
                BotUtils._blacklist_mtime = mtime
                return BotUtils._blacklist_cache
        except FileNotFoundError:
            return []


    @staticmethod
    def generate_password(length=None):
        """Generates a random password of specified length."""
        if length is None:
            length = random.randint(15, 32)
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    @staticmethod
    def parse_duration_string(duration_str):
        """Parses a duration string like '1h:30m:10s' into seconds."""
        if not duration_str:
            raise ValueError("Duration string cannot be empty")
        duration_seconds = 0
        for part in duration_str.replace(" ", "").split(':'):
            if not part: continue
            unit = part[-1].lower()
            try:
                value = int(part[:-1])
                if unit == 's': duration_seconds += value
                elif unit == 'm': duration_seconds += value * 60
                elif unit == 'h': duration_seconds += value * 3600
                elif unit == 'd': duration_seconds += value * 86400
                elif unit == 'w': duration_seconds += value * 604800
                else: raise ValueError(f"Invalid duration unit: {unit}")
            except (ValueError, IndexError):
                raise ValueError(f"Invalid duration part: {part}")
        return duration_seconds

    @staticmethod
    def get_user_location(ip_address):
        """Fetches country and city for a given IP address."""
        if not ip_address or ip_address == "127.0.0.1":
            return "Local", "Host"
        
        base_url = f"http://ip-api.com/json/{ip_address}"
        params = {"fields": "status,message,country,city"}
        try:
            response = requests.get(base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success":
                return data.get("country"), data.get("city")
            else:
                print(f"Error getting location for {ip_address}: {data.get('message')}")
                return None, None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching location for {ip_address}: {e}")
            return None, None

    @staticmethod
    def is_vpn(ip_address):
        """Checks if an IP address is likely a VPN/proxy."""
        if not ip_address or ip_address == "127.0.0.1":
            return False
        
        base_url = f"http://ip-api.com/json/{ip_address}"
        params = {"fields": "status,message,proxy"}
        try:
            response = requests.get(base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success":
                return data.get("proxy", False)
            return False
        except requests.exceptions.RequestException:
            return False

    @staticmethod
    def send_telegram_notification(token, chat_id, message):
        """Sends a notification to a specified Telegram chat ID."""
        if not token or not chat_id:
            return
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error sending Telegram notification: {e}")


class LoggingThreadPoolExecutor(ThreadPoolExecutor):
    """
    A ThreadPoolExecutor that automatically logs exceptions from submitted tasks.
    """
    def submit(self, fn, *args, **kwargs):
        """
        Wraps the submitted function to catch and log any exceptions.
        """
        def wrapped_fn(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                exc_info = traceback.format_exc()
                logging.error(f"Exception in thread pool for function '{fn.__name__}':\n{exc_info}")
        
        # Submit the wrapped function to the parent class's submit method
        return super().submit(wrapped_fn, *args, **kwargs)