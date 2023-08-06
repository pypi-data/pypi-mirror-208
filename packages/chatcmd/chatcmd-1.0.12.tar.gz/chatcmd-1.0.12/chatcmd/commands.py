import os
import sqlite3
import datetime
from .helpers import *


def add_cmd(conn, cursor, prompt, command):
    try:
        cursor.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, prompt TEXT, command TEXT, created_at DATETIME)')
        conn.commit()

        cursor.execute("INSERT INTO history (prompt,command,created_at) VALUES(?,?,?)", (prompt, command, datetime.datetime.now()))
        conn.commit()

        return True
    except sqlite3.Error as e:
        error_msg(f"Error 1012: Failed to add command to history: {e}")
    return False

def get_cmd(conn, cursor):
    try:
        cursor.execute("SELECT prompt, command, created_at FROM history ORDER BY id DESC LIMIT 1")
        command = cursor.fetchone()

        if command is not None:
            print("Latest Command:\n\n "+color_text(command[0],'white')+": "+color_text(command[1],'green')+"\n")
        else:
            warning_msg("History is empty.")

    except sqlite3.Error as e:
        error_msg(f"Error 1013: Failed to get last command from history: {e}")

def get_last_num_cmd(conn, cursor, number):
    try:
        number = int(number)
        if number < 1:
            warning_msg('History is empty.')
        cursor.execute("SELECT prompt, command, created_at FROM history ORDER BY id DESC LIMIT ?", (number,))
        commands = cursor.fetchall()
        if len(commands) > 0:
            number = min(number, len(commands))
            print(color_text('Latest Command:\n','white') if number == 1 else color_text(f'Last {number} Commands:\n','white'))

            for command in commands:
                print(f'  - {color_text(command[1], "green")}')
        else:
            warning_msg("History is empty.")
        return True
    except ValueError as ve:
        warning_msg(str(ve))
    except sqlite3.Error as e:
        error_msg(f"Error 1014: Failed to get last command from history: {e}")
    return False

def delete_cmd(conn, cursor):
    try:
       cursor.execute("DELETE FROM history ORDER BY id DESC LIMIT 1")
       conn.commit()
       success_msg("Command deleted successfully.")
    except sqlite3.Error as e:
        error_msg(f"Error 1015: Failed deleting last command: {e}")
    return False

def delete_last_num_cmd(conn, cursor, number):
    try:
        if get_commands_count(conn,cursor) == 0:
            warning_msg('History is empty.')
        else:
            number = int(number)
            if number < 1:
                error_msg('Please enter a correct number.')
            else:
                cursor.execute("DELETE FROM history ORDER BY id DESC LIMIT "+str(number))
                delete = conn.commit()
                if number > 1:
                    success_msg("All "+str(number)+" commands deleted successfully")
                else:
                    success_msg("Command deleted successfully")
    except sqlite3.Error as e:
        error_msg(f"Error 1016: Failed to get last command from history: {e}")

def clear_history(conn, cursor):
    try:
        cursor.execute('DELETE FROM history')
        conn.commit()
        print(color_text(f"\nAll command lookup has been cleared.",'green'))
        return True
    except sqlite3.Error as e:
        error_msg(f"Error 1017: Failed clearing history: {e}")
    return False

def get_db_size():
    file_size_bytes = os.path.getsize('data/db.sqlite')
    units = ['bytes', 'KB', 'MB', 'GB']
    size = file_size_bytes
    unit_index = 0

    while size >= 1024 and unit_index < len(units)-1:
        size /= 1024
        unit_index += 1

    print(f"\nDB File size: \033[32m{size:.2f} {units[unit_index]}\033[0m\n")

def get_commands_count(conn, cursor):
    cursor.execute('SELECT COUNT(*) FROM history')
    count = cursor.fetchone()[0]
    return count