import argparse
import logging
import sys
import os
import threading
import TeamTalk5 as teamtalk
from TeamTalk5 import ttstr
from bot.tt_utilities import TTUtilities
from bot.config_handler import ConfigHandler
from bot.account import Account
from bot.utils import BotUtils as utils, ShutdownSignal, RestartSignal

def main():
    """
    Main function to set up and run the bot.
    """
    parser = argparse.ArgumentParser(description="TeamTalk Utilities Bot")
    parser.add_argument("-f", "--configfile", help="Path to a custom configuration file.")
    args = parser.parse_args()

    # If a config file path is provided, check if it actually exists.
    if args.configfile and not os.path.isfile(args.configfile):
        print(f"Error: The specified configuration file was not found at: {args.configfile}")
        sys.exit(1)

    logging.basicConfig(filename='errors.log', level=logging.ERROR, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

    while True:  # Outer loop for restarting
        print("Initializing bot components...")
        try:
            config_path = args.configfile if args.configfile else "config.ini"
            config = ConfigHandler(config_path)
            accounts = Account()

            bot = TTUtilities(
                config_handler=config, 
                account_creator=accounts
            )
        except Exception as e:
            logging.error(f"Failed to initialize the bot: {e}")
            print(f"FATAL: Failed to initialize the bot. Check errors.log for details. Error: {e}")
            break  # Exit on fatal initialization error

        if bot.bot_config.get("random_message_interval", 0) > 0:
            messages = utils.load_messages("messages.txt")
            if messages:
                message_thread = threading.Thread(
                    target=bot.send_broadcast_messages_at_intervals, 
                    args=(messages,), 
                    daemon=True
                )
                message_thread.start()

        restart = False
        while True:  # Inner loop for event handling
            try:
                bot.runEventLoop(100) # Wait 100ms to allow Python to catch signals like Ctrl+C
            except KeyboardInterrupt:
                print("\nShutting down bot...")
                bot.shutdown()
                sys.exit(0)  # Cleanly exit the entire program
            except ShutdownSignal:
                print("\nShutdown signal received.")
                bot.shutdown()
                sys.exit(0)  # Cleanly exit the entire program
            except RestartSignal:
                print("\nRestart signal received. Restarting...")
                bot.shutdown()
                restart = True
                break  # Break inner loop to trigger restart
            except Exception as e:
                logging.exception(f"An error occurred in the main event loop: {e}")
                # Depending on the error, you might want to restart or shutdown
                # For now, we'll log it and continue if possible
        
        if not restart:
            break  # Break the outer loop if we are not restarting


if __name__ == "__main__":
    main()