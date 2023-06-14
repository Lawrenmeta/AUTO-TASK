# encoding:utf-8
# encoding:utf-8
import json
from typing import Dict
import gradio as gr
import time
from prmpt.prompt import PromptGenerator
from plughcontrol.command import CommandRegistry
from llm.chat import chat_with_claude
from utils.json_fix import fix_json_using_multiple_techniques


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
        file.write(txt + '\n')


command_registry = CommandRegistry()
command_categories1 = [
    "plughcontrol.commands.analyze_code",
    "plughcontrol.commands.audio_text",
    "plughcontrol.commands.execute_code",
    "plughcontrol.commands.file_operations",
    "plughcontrol.commands.git_operations",
    "plughcontrol.commands.google_search",
    "plughcontrol.commands.image_gen",
    "plughcontrol.commands.improve_code",
    "plughcontrol.commands.twitter",
    "plughcontrol.commands.web_selenium",
    "plughcontrol.commands.write_tests",
    "plughcontrol.app",
    "plughcontrol.commands.task_statuses",
]
command_categories = [
    "plughcontrol.commands.crawler_selenium",
    "plughcontrol.commands.paper_selenium",
    "plughcontrol.commands.google_search"

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

num_plan = 0


def test_api(string, num_plan):
    # goal = input('what you want:')
    goal = string
    prompt_generator.goals = [goal]
    prompt_start = (
        "Your decisions must always be made independently without"
        " seeking user assistance. Play to your strengths as an LLM and pursue"
        " simple strategies with no legal complications."
        ""
    )
    prompt_generator.command_registry = command_registry
    prompt_start += f"\nThe OS you are running on is: windows"
    # print(prompt_generator.generate_prompt_string())

    plan_list = ['0', '2', '总结之前的所有内容回答问题，不执行命令']
    while num_plan < 3:
        full_prompt = ''
        full_prompt = f"You are {prompt_generator.name}, {prompt_generator.role}\n{prompt_start}\n\nGOALS:\n\n"
        # if num_plan > 0 and plan_list[i]:
        #     prompt_generator.goals[0] = plan_list[i]
        # else:
        #     if num_plan != 0:
        #         break
        if num_plan == 2:
            prompt_generator.goals[0] = '总结之前的所有内容回答问题，不执行命令'
        for i, goal in enumerate(prompt_generator.goals):
            full_prompt += f"{i + 1}. {goal}\n"
        full_prompt += f"\n\n{prompt_generator.generate_prompt_string()}"
        print(full_prompt)
        a = chat_with_claude(full_prompt)
        print(a)
        res = fix_json_using_multiple_techniques(a)

        if num_plan == 0:
            plan = str(res['thoughts']['plan'])
            plan_list = plan.split('\n')
            # 打印提取的结果
            for item in plan_list:
                print(item)
        # print(res['command'])
        command_name, arguments = get_command(res)
        if command_name == 'download paper':
            num_plan = 2

        command_result = execute_command(
            command_registry,
            command_name,
            arguments,
            prompt_generator,
        )
        print(command_result)
        if num_plan == 2:
            try:
                print(res['thoughts']['text'])
                return f"{res['thoughts']['text']}"
            except:
                return "返回格式错误"
        prompt_generator.performance_evaluation.append(
            f"the command '{command_name}' with the arg '{arguments}' have finished, result {command_result[:4000]}")
        num_plan = num_plan + 1


with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clr = gr.Button("Clear")


    def respond(message, chat_history):
        bot_msg = test_api(message, 0)
        chat_history.append((message, bot_msg))
        time.sleep(1)
        return "", chat_history


    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clr.click(lambda: None, None, chatbot, queue=False)

demo.launch()
