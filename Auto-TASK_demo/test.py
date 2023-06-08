# encoding:utf-8
import json
from typing import Dict

from prompt import PromptGenerator
from command import CommandRegistry, Command
from chat import chat_with_claude
from json_fix import fix_json_using_multiple_techniques
def get_memory():
    with open("memory.txt", "r") as file:
        content = file.read()
        return content


def clear_memory():
    with open("memory.txt", "w") as file:
        file.truncate(0)
def map_command_synonyms(command_name: str):
    """Takes the original command name given by the AI, and checks if the
    string matches a list of common/known hallucinations
    """
    synonyms = [
        ("write_file", "write_to_file"),
        ("create_file", "write_to_file"),
        ("search", "google"),
    ]
    for seen_command, actual_command_name in synonyms:
        if command_name == seen_command:
            return actual_command_name
    return command_name

def execute_command(
    command_registry: CommandRegistry,
    command_name: str,
    arguments,
    prompt: PromptGenerator,
):
    """Execute the command and return the result

    Args:
        command_name (str): The name of the command to execute
        arguments (dict): The arguments for the command

    Returns:
        str: The result of the command
    """
    try:
        cmd = command_registry.commands.get(command_name)

        # If the command is found, call it with the provided arguments
        if cmd:
            return cmd(**arguments)

        # TODO: Remove commands below after they are moved to the command registry.
        command_name = map_command_synonyms(command_name.lower())

        if command_name == "memory_add":
            return get_memory()

        # TODO: Change these to take in a file rather than pasted code, if
        # non-file is given, return instructions "Input should be a python
        # filepath, write your code to file and try again
        else:
            for command in prompt.commands:
                if (
                    command_name == command["label"].lower()
                    or command_name == command["name"].lower()
                ):
                    return command["function"](**arguments)
            return (
                f"Unknown command '{command_name}'. Please refer to the 'COMMANDS'"
                " list for available commands and only respond in the specified JSON"
                " format."
            )
    except Exception as e:
        return f"Error: {str(e)}"


def get_command(response_json: Dict):
    """Parse the response and return the command name and arguments

    Args:
        response_json (json): The response from the AI

    Returns:
        tuple: The command name and arguments

    Raises:
        json.decoder.JSONDecodeError: If the response is not valid JSON

        Exception: If any other error occurs
    """
    try:
        if "command" not in response_json:
            return "Error:", "Missing 'command' object in JSON"

        if not isinstance(response_json, dict):
            return "Error:", f"'response_json' object is not dictionary {response_json}"

        command = response_json["command"]
        if not isinstance(command, dict):
            return "Error:", "'command' object is not a dictionary"

        if "name" not in command:
            return "Error:", "Missing 'name' field in 'command' object"

        command_name = command["name"]

        # Use an empty dictionary if 'args' field is not present in 'command' object
        arguments = command.get("args", {})

        return command_name, arguments
    except json.decoder.JSONDecodeError:
        return "Error:", "Invalid JSON"
    # All other errors, return "Error: + error message"
    except Exception as e:
        return "Error:", str(e)


def append_memory(txt):
    with open("memory.txt", "a+") as file:
        file.write(txt+'\n')



command_registry = CommandRegistry()
command_categories1 = [
    "autogpt.commands.analyze_code",
    "autogpt.commands.audio_text",
    "autogpt.commands.execute_code",
    "autogpt.commands.file_operations",
    "autogpt.commands.git_operations",
    "autogpt.commands.google_search",
    "autogpt.commands.image_gen",
    "autogpt.commands.improve_code",
    "autogpt.commands.twitter",
    "autogpt.commands.web_selenium",
    "autogpt.commands.write_tests",
    "autogpt.app",
    "autogpt.commands.task_statuses",
]
command_categories = [
    "autogpt.commands.google_search"

]
for command_category in command_categories:
    command_registry.import_commands(command_category)


prompt_start = (
            "Your decisions must always be made independently without"
            " seeking user assistance. Play to your strengths as an LLM and pursue"
            " simple strategies with no legal complications."
            ""
        )
prompt_generator = PromptGenerator()
prompt_generator.name = 'asd'
prompt_generator.goals = ['查看成都的天气']
prompt_generator.command_registry = command_registry
prompt_start += f"\nThe OS you are running on is: windows"
# print(prompt_generator.generate_prompt_string())
full_prompt = f"You are {prompt_generator.name}, {prompt_generator.role}\n{prompt_start}\n\nGOALS:\n\n"
for i, goal in enumerate(prompt_generator.goals):
    full_prompt += f"{i+1}. {goal}\n"
full_prompt += f"\n\n{prompt_generator.generate_prompt_string()}"
print(full_prompt)
a = chat_with_claude(full_prompt)
res = fix_json_using_multiple_techniques(a)
print(res)
# print(res['command'])
command_name, arguments = get_command(res)
command_result = execute_command(
                    command_registry,
                    command_name,
                    arguments,
                    prompt_generator,
                )
print(command_result)

