from .commands import *
import pyperclip
import openai

def prompt(conn, cursor, api_key):
    print("""

     ######  ##     ##    ###    ########  ######  ##     ## ########
    ##    ## ##     ##   ## ##      ##    ##    ## ###   ### ##     ##
    ##       ##     ##  ##   ##     ##    ##       #### #### ##     ##
    ##       ######### ##     ##    ##    ##       ## ### ## ##     ##
    ##       ##     ## #########    ##    ##       ##     ## ##     ##
    ##    ## ##     ## ##     ##    ##    ##    ## ##     ## ##     ##
     ######  ##     ## ##     ##    ##     ######  ##     ## ########

    """)
    if validate_api_key(api_key) is False:
        error_msg("Error 1009: API key is invalid or missing")
    prompt = clear_input(input("Prompt: "))

    if prompt == '':
        prompt(conn, cursor, api_key)
    if prompt == 'exit':
        print(color_text('bye...', 'green'))
        exit()
    elif validateInput(prompt):
        command = lookup(prompt, api_key)
        if command is not None:
            pyperclip.copy(command)
            command = clear_input(command)

            if command.find('there is no command') is True and command.find('There is no specific command') is True:
                warning_msg('there is no command for this!')
            else:
                history = add_cmd(conn, cursor, prompt, command.strip())
                if history is False:
                    print(color_text("Error 1008 Failed to add command to history", 'cyan'))
                print(color_text(" " + command.strip(), 'green'))
                print('')
    else:
        warning_msg("Please type in more than two words.\n")


def lookup(prompt, api_key):
    try:
        if validate_api_key(api_key) is False:
            error_msg("Error 1009: API key is invalid or missing")
            exit()

        prompt = prompt
        print(color_text(f'Looking up: "{prompt}"...' + "\n", 'yellow'))

        stop_keywords = ["###", "END", "stop", "Command:", "Syntax:", "Usage:"]
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f"Please help me with a CLI command lookup, I only need the command without any extra information: Show me the command for {prompt}",
            max_tokens=70,
            n=1,
            stop=None,
            temperature=0.7)
        message = response.choices[0].text.strip()
        return message

    except openai.error.OpenAIError as e:
        error_msg(f"Error 1010: OpenAI API error occurred: {e}")
    except Exception as e:
        error_msg(f"Error 1011: Unhandled exception occurred: {e}")
