#!/usr/bin/env python
"""
\033[32m
     ######  ##     ##    ###    ########  ######  ##     ## ########
    ##    ## ##     ##   ## ##      ##    ##    ## ###   ### ##     ##
    ##       ##     ##  ##   ##     ##    ##       #### #### ##     ##
    ##       ######### ##     ##    ##    ##       ## ### ## ##     ##
    ##       ##     ## #########    ##    ##       ##     ## ##     ##
    ##    ## ##     ## ##     ##    ##    ##    ## ##     ## ##     ##
     ######  ##     ## ##     ##    ##     ######  ##     ## ########
   --------------------------------------------------------------------
                AI-driven CLI command lookup using ChatGPT
          Boost Your Productivity, Say Goodbye to Manual Searches
   --------------------------------------------------------------------
\033[37m               Developed By: Naif Alshaye | https://naif.io\033[0m

\033[33mUsage:\033[0m
    \033[32mchatcmd\033[0m [options]

\033[33mOptions:\033[0m
  -k, --set-key                     set or update ChatGPT API key.
  -o, --get-key                     display ChatGPT API key.
  -g, --get-cmd                     display the last command.
  -G, --get-last=<value>            display the last [number] of commands.
  -d, --delete-cmd                  delete the last command.
  -D, --delete-last-cmd=<value>     delete the last [number] of commands.
  -t, --cmd-total                   display the total number of commands.
  -c, --clear-history               clear all history records.
  -s, --db-size                     display the database size.
  -h, --help                        display this screen.
  -v, --version                     display ChatCMD version.
  -i, --library-info                display library information.
"""

import sqlite3
from docopt import docopt
from .helpers import *
from .lookup import *
from .api import *

def main():
    try:
        args = docopt(__doc__)
        try:
            BASE_DIR = os.path.dirname(os.path.dirname(__file__))
            db_path = os.path.join(BASE_DIR, "chatcmd/db.sqlite")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
        except sqlite3.Error as e:
            error_msg(f"Error 1002: Failed to connect to database: {e}")

        api_key = get_api_key(conn, cursor)

        if api_key is None:
            api_key = ask_for_api_key(conn, cursor)

        openai.api_key = api_key

        if args['--version']:
            print('ChatCMD \033[32m1.0.10\033[0m')
        elif args['--set-key']:
            ask_for_api_key(conn, cursor)
        elif args['--get-key']:
            output_api_key(conn, cursor)
        elif args['--get-cmd']:
            get_cmd(conn, cursor)
        elif args['--get-last']:
            get_last_num_cmd(conn, cursor, args['--get-last'])
        elif args['--cmd-total']:
            print('\nTotal of ' + color_text(get_commands_count(conn, cursor), 'green') + ' commands\n')
        elif args['--delete-cmd']:
            delete_cmd(conn, cursor)
        elif args['--delete-last-cmd']:
            delete_last_num_cmd(conn, cursor, args['--delete-last-cmd'])
        elif args['--clear-history']:
            clear_history(conn, cursor)
        elif args['--db-size']:
            get_db_size()
        elif args['--library-info']:
            library_info()
        else:
            prompt(conn, cursor, api_key)

        cursor.close()
        conn.close()
    except Exception as e:
        error_msg(f"Error 1001: {e}")


if __name__ == '__main__':
    main()
