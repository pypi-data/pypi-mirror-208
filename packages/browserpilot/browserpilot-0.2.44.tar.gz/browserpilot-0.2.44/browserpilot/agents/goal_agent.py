"""GoalAgent class."""
import time
import logging
from typing import Dict
import yaml
from bs4.element import Tag
from .gpt_selenium_agent import GPTSeleniumAgent, By

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""For the chatbot mode."""
CHATBOT_COMMANDS = {
    "help": "Shows this message.",
    "save": "Save all the code generated so far to a yaml file.",
    "exit or quit": "Exits the chatbot. Alternatively, you can also press ctrl+c.",
}


"""Set up all the prompt variables."""
# Beginning prompt.
PROMPT_FOR_FIRST_INSTRUCTION = """You are given a command to do a task using a web browser.

Let's reason step by step about what sequence of actions you have would to take in order to accomplish a task.

If no direction about which webpage to start on is given, you must (1) extract the relevant keywords from the command to search in Google and (2) begin with the lines

Go to google.com
Find the input element with title "Search".
Type <keywords> and press enter.

where <keywords> are the extracted keywords from the below command. 
For example, if the command is "Order me a pizza on DoorDash", then <keywords> could be "pizza DoorDash".

If direction about the webpage is given (e.g., "Go to https://www.example.com"), simply return "Go to <url>."

Return your answers directly, succinctly, and without prefaces or suffixes. Let's start with the first step ONLY. Don't narrate what you are doing in your answer.
Command: "{command}"
Answer:"""

# Thank you to Nat Friedman for inspiration for this prompt.
# Source: https://github.com/nat/natbot/blob/main/natbot.py
DONE_TOKEN = "<DONE!>"
PROMPT_FOR_REST_OF_INSTRUCTIONS = """You are an agent controlling a browser. You are given:
1. An objective that you are trying to achieve.
2. A simplified text description of what's visible in the browser window (more on that below)
3. The current url.
4. A list of human-readable commands that you have already issued. Their format is readable to humans (e.g., "CLICK <element>") as opposed to the format you should use to issue commands to the browser (e.g., "CLICK 5"). See more below.

You can issue these commands: 
- SCROLL UP|DOWN - Either  scroll up or scroll down one page.
- CLICK X - Click on the element with id X where X is an int. You can only click on links, buttons, and inputs.
- TYPE X <TEXT> - Type the specified text into the input with id X (where X is an int).
- TYPESUBMIT X <TEXT> - Same as TYPE above, except it presses ENTER to submit the form.
- CLEAR X - Clear the input with id X (where X is an int).
- WAIT n - Wait for `n` seconds where `n` is an int.
- SCREENSHOT <FILENAME> - Take a screenshot of the page and save it to <FILENAME>.
- <DONE!> - Declare that we are done with the task!

The format of the browser content is highly simplified; all formatting elements are stripped.
Interactive elements such as links, inputs, buttons are represented like this:
		<a id=1>text</link>
		<button id=2>text</button>
		<input id=3>text</input>
Images are rendered as their alt text like this:
		<img id=4 alt=""/>

Based on your given objective, issue whatever command you believe will get you closest to achieving your goal.
==================================================
The current browser content and objective are below. Reply with your next command(s) to the browser. 
Ideally, do not repeat yourself. Your command can only be formatted according to the directions above.
CURRENT BROWSER CONTENT:
------------------
{html}
------------------
OBJECTIVE: {objective}
CURRENT URL: {curr_url}
ACTIONS SO FAR (human readable):
{commands}
YOUR NEXT COMMAND(S):"""


ASK_LLM_PROMPT_TEMPLATE = """You are on a webpage. The text content of the webpage is below.
Please answer the question below.

CURRENT BROWSER CONTENT:
------------------
{text}
------------------
QUESTION: {question}
ANSWER:"""


class GoalAgent:
    def __init__(
        self,
        command=None,
        chromedriver_path=None,
        max_steps=100,
        memory_folder=None,
        model="gpt-3.5-turbo",
        debug=False,
    ):
        """Initialize the agent. It uses GPTSeleniumAgent to do the actual
        actions.

        Args:
            command (str): The instructions to compile.
            chromedriver_path (str): The path to the chromedriver.
            max_steps (int): The maximum number of times to ask for the next
                instruction. Used to prevent infinite loops.
            memoy_file (str): The path to the memory file.
            model (str): The model to use.
        """
        assert (
            chromedriver_path is not None
        ), "Please provide a path to the chromedriver."

        """Instance variables."""
        self.model = model
        self.max_steps = max_steps
        self.memory_folder = memory_folder  # TODO.
        self.debug = debug  # For GPTSeleniumAgent below.

        # Vars for `run` mode.
        self.objective = command
        self.commands_so_far_human_readable = []
        self.commands_code = []  # The actual code to execute.

        # Vars for `chatbot` mode.
        self.objectives_in_chatbot_mode = []
        self.commands_code_in_chatbot_mode = []

        # Accounting for the current state of the web browser.
        self.browser_element_mapping = {}

        # Vars for GPTSeleniumAgent.
        self.chromedriver_path = chromedriver_path
        _blank_instruction = ""
        self.browsing_agent = GPTSeleniumAgent(
            _blank_instruction,
            self.chromedriver_path,
            memory_folder=self.memory_folder,
            close_after_completion=False,
            debug=self.debug,
            retry=False,  # Not compatible.
        )

    """Helper functions."""

    def _get_completion(
        self,
        prompt,
        model=None,
        temperature=0,
        max_tokens=1024,
        stop=["```"],
        use_cache=True,
    ) -> str:
        """Get the completion from OpenAI."""
        if model is None:
            model = self.model

        # So this is kind of hacky, but just use the get_completion function
        # from the GPTSeleniumAgent's InstructionCompiler. I just want to
        # keep the number of times I rewrite the same code to a minimum.
        return self.browsing_agent.instruction_compiler.get_completion(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            use_cache=use_cache,
            stop=stop,
        )

    def _feed_instruction_to_agent(self, instruction, is_code=False):
        """Feed the instruction to the Selenium agent. This is an important
        function because it will help us iteratively generate instructions
        based on the environment and then feed them to the agent.

        If `is_code`, then the instruction is a Python code snippet. Otherwise,
        it is a natural language instruction."""
        if is_code:
            instruction = {
                "instructions": "",
                "compiled": [instruction],
            }
        self.browsing_agent.set_instructions(instruction)
        self.browsing_agent.run()

    def __preprocess_html_for_prompt(self) -> Dict:
        """Preprocess the HTML. Returns a Dict of the form:
        {
            "int": {
                "original": <original tag>,
                "transformed": <transformed tag>,
                "text": <text of the tag>
            }
        }
        """
        logger.info("Preprocessing HTML for AI to read...")
        # Get all of inputs, textareas, anchors, buttons, and imgs using
        # self.browsing_agent.driver, the Selenium driver.
        inputs = self.browsing_agent.driver.find_elements(by=By.TAG_NAME, value="input")
        textareas = self.browsing_agent.driver.find_elements(
            by=By.TAG_NAME, value="textarea"
        )
        anchors = self.browsing_agent.driver.find_elements(by=By.TAG_NAME, value="a")
        buttons = self.browsing_agent.driver.find_elements(
            by=By.TAG_NAME, value="button"
        )
        imgs = self.browsing_agent.driver.find_elements(by=By.TAG_NAME, value="img")
        # Also get the divs that have a role of button or textbox.
        divs = self.browsing_agent.driver.find_elements(by=By.TAG_NAME, value="div")
        divs = [
            div for div in divs if div.get_attribute("role") in ["button", "textbox"]
        ]
        # Combine all of the elements.
        elements = inputs + textareas + anchors + buttons + imgs + divs

        mapping = {}
        curr_idx = 1
        for element in elements:
            # If the element is not visible, then don't include it.
            if not element.is_displayed():
                continue
            if not self.browsing_agent.is_element_visible_in_viewport(element):
                continue
            old_element = element.get_attribute("outerHTML")

            # Select the attributes to keep.
            attrs = {}
            attrs_to_keep = [
                "alt",
                "aria-label",
                "name",
                "title",
                "type",
                "role",
            ]
            for attr in attrs_to_keep:
                if element.get_attribute(attr):
                    attrs[attr] = str(element.get_attribute(attr))

            if element.tag_name == "input":
                # If the element is an input, then add the value and the
                # placeholder.
                input_value = str(element.get_attribute("value"))
                input_placeholder = str(element.get_attribute("placeholder"))
                if input_value:
                    attrs["value"] = input_value
                if input_placeholder:
                    attrs["placeholder"] = input_placeholder

            # Get the text from the element and strip whitespace.
            text = element.get_attribute("innerText").replace("\n", " ")

            # Create the new element.
            bs_tag = Tag(name=element.tag_name, attrs=attrs)
            bs_tag["id"] = str(curr_idx)
            bs_tag.string = text
            new_element = str(bs_tag)

            # If the img has no alt text, then don't include it.
            # In the future, we could try to use computer vision to caption.
            if element.tag_name == "img" and not element.get_attribute("alt"):
                continue

            # If div, button, or anchor has no text, then don't include it.
            if element.tag_name in ["div", "a", "button"] and not text:
                continue

            mapping[str(curr_idx)] = {
                "original": old_element,
                "transformed": new_element,
                "text": text,
            }
            curr_idx += 1

        return mapping

    def _get_first_instruction(self) -> str:
        """Get the first instruction."""
        prompt = PROMPT_FOR_FIRST_INSTRUCTION.format(command=self.objective)
        first_instruction = self._get_completion(prompt=prompt, model=self.model)
        self.commands_so_far_human_readable.append(first_instruction)
        return first_instruction

    def _get_current_url(self) -> str:
        """Get the current URL."""
        url = self.browsing_agent.driver.current_url
        if len(url) >= 100:
            url = url[:100] + "..."
        return url

    def _get_current_browser_view_from_mapping(self):
        """Get what the AI sees."""
        mapping = self.browser_element_mapping
        elements = "\n".join([mapping[key]["transformed"] for key in mapping.keys()])
        return elements

    def _get_natbot_response(self, multiline=False) -> str:
        """Get the next instruction for our current GoalAgent prompt.

        The @multiline argument is used to determine whether or not to
        get a single line response or a multi-line response."""
        stop = ["\n"]
        if multiline:
            stop = None

        mapping: Dict = self.__preprocess_html_for_prompt()
        self.browser_element_mapping = mapping

        elements = self._get_current_browser_view_from_mapping()
        curr_url = self._get_current_url()

        prompt = PROMPT_FOR_REST_OF_INSTRUCTIONS.format(
            curr_url=curr_url,
            html=elements,
            objective=self.objective,
            commands="\n- ".join(self.commands_so_far_human_readable),
        )
        logger.info("\n\nPrompt for AI: " + prompt)
        next_instruction = self._get_completion(
            prompt=prompt, model=self.model, stop=stop, temperature=0.5
        )
        next_instruction = next_instruction.strip()

        # More human readable command logging.
        if next_instruction.startswith("CLICK "):
            parsed = self._parse_natbot_response(next_instruction, multiline=multiline)
            args = parsed["args"]
            element_id = args[1]
            text = mapping[element_id]["text"]
            self.commands_so_far_human_readable.append(
                f"Clicked on element with text '{text}'"
            )
        else:
            self.commands_so_far_human_readable.append(next_instruction)

        return next_instruction

    def _parse_natbot_response(self, natbot_instruction, multiline=False):
        """Get the arguments for each type of command."""
        if multiline:
            natbot_instruction = natbot_instruction.split("\n")[0]

        def get_code_for_selecting_element(element):
            beginning_python = 'element = env.find_element(by="xpath", value="'
            prompt_select_ele = """Write a Selenium xpath selector to uniquely select the following element.
Please default to using single quotes in your xpath selector. If you use double quotes, then you will need to escape them.
Ideally, you should be able to select the element with the text that it contains.
In that case, do NOT use `text()`. Use `normalize-space()` instead. The xpath for an element whose text is "text" is "//*[normalize-space() = 'text']". The xpath for an element that contains text is "//*[contains(normalize-space(), 'text')]".
Use as few characters and HTML attributes as possible to select the element.
If you decide to include a tag name in the xpath, please use the tag name I give you below.

            {element}
            ```python
            {snippet}"""
            prompt = prompt_select_ele.format(element=element, snippet=beginning_python)
            resp = self._get_completion(prompt, model="gpt-3.5-turbo", stop=["```"])
            return_snippet = beginning_python + resp
            return return_snippet

        if natbot_instruction.startswith("SCROLL"):
            direction = natbot_instruction.split("SCROLL")[1].strip()
            args = ["SCROLL", direction]
            code = f"env.scroll('{direction}')"
        elif natbot_instruction.startswith(DONE_TOKEN):
            args = [DONE_TOKEN]
            code = DONE_TOKEN
        elif natbot_instruction.startswith("WAIT"):
            num_secs = int(natbot_instruction.split("WAIT")[1].strip())
            args = ["WAIT", num_secs]
            code = f"env.wait({num_secs})"
        elif natbot_instruction.startswith("ASK_LLM"):
            question = natbot_instruction.split("ASK_LLM")[1].strip()
            args = ["ASK_LLM", question]
            text = self.get_text_from_page()
            prompt = ASK_LLM_PROMPT_TEMPLATE.format(question=question, text=text)
            prompt = prompt.replace("'", "\\'")
            code = f"response = env.get_llm_response('{prompt}')\nprint(response)"
        elif natbot_instruction.startswith("SCREENSHOT"):
            fname = natbot_instruction.split("SCREENSHOT")[1].strip()
            code_response = """element = env.find_element("xpath", "//html")"""
            code_response += """\nenv.screenshot(element, {})""".format(fname)
            args = ["SCREENSHOT", fname]
            code = code_response
        elif natbot_instruction.startswith("CLICK"):
            ele_id = natbot_instruction.split("CLICK")[1].strip()
            element = self.browser_element_mapping[ele_id]["original"]
            select_code = get_code_for_selecting_element(element)
            code = f"{select_code}\nenv.click(element)"
            args = ["CLICK", ele_id]
        elif natbot_instruction.startswith("CLEAR"):
            ele_id = natbot_instruction.split("CLEAR")[1].strip()
            element = self.browser_element_mapping[ele_id]["original"]
            select_code = get_code_for_selecting_element(element)
            code = f"{select_code}\nelement.clear()"
            args = ["CLEAR", ele_id]
        elif natbot_instruction.startswith("TYPE "):
            args = natbot_instruction.split("TYPE")[1].strip()
            args = args.split(" ")
            ele_id = args[0]
            text = " ".join(args[1:]).replace("'", "\\'")

            element = self.browser_element_mapping[ele_id]["original"]
            select_code = get_code_for_selecting_element(element)
            code = (
                f"{select_code}\nenv.click(element)\nenv.send_keys(element, '{text}')"
            )
            args = ["TYPE", ele_id, text]
        elif natbot_instruction.startswith("TYPESUBMIT "):
            args = natbot_instruction.split("TYPESUBMIT")[1].strip()
            ele_id, text = args.split(" ")
            text = " ".join(args[1:]).replace("'", "\\'")
            element = self.browser_element_mapping[ele_id]["original"]
            select_code = get_code_for_selecting_element(element)
            code_response = (
                f"{select_code}\nenv.click(element)\nenv.send_keys(element, '{text}')"
            )
            code += "\nenv.send_keys(element, Keys.ENTER)"
            args = ["TYPESUBMIT", ele_id, text]
        else:
            raise ValueError(f"Invalid command: {natbot_instruction}")

        return {
            "args": args,
            "code": code,
        }

    def _get_compiled_instruction(self, natbot_instruction) -> str:
        """Given a response to the Natbot-inspired prompt, get the next
        instruction to feed to the GPTSeleniumAgent."""
        parsed = self._parse_natbot_response(natbot_instruction)
        code_response = parsed["code"]
        logger.info("\nCode response: {}".format(code_response))
        self.commands_code.append(code_response)
        return code_response

    def __print_instructions(self):
        """Print instructions for how to use the chatbot."""
        print("You can run the following commands:")
        for command, description in CHATBOT_COMMANDS.items():
            print(
                "  '{command}': {description}".format(
                    command=command, description=description
                )
            )
        print("\nOtherwise, just type your objective and press enter.")
        print(
            "NOTE: This chatbot works best if you give it the smallest possible objective at a time."
        )

    """Public functions."""

    def chat(self):
        """If the agent is in chat mode, run the chat loop."""
        logger.setLevel(logging.WARNING)

        print("\nWelcome to the chatbot mode!")
        self.__print_instructions()

        is_first_instruction = True
        while True:
            user_input = input("\n> Next objective: ")
            self.objective = user_input

            if user_input.lower() == "quit" or user_input.lower() == "exit":
                print("Exiting.")
                break
            elif user_input.lower() == "help":
                self.__print_instructions()
                continue
            elif user_input.lower() == "save":
                self.save_chatbot_history()

            if is_first_instruction:
                # Get the first instruction: either to go to a webpage or to search
                # Google. Then perform it.
                first_instruction = self._get_first_instruction()
                print(first_instruction)
                self._feed_instruction_to_agent(first_instruction)
                is_first_instruction = False
            else:
                print("\nChatbot: I'm thinking ...")
                # Get the next instruction.
                natbot_instruction = self._get_natbot_response(multiline=True)
                natbot_instruction = natbot_instruction.split("\n")

                for i, curr_instruction in enumerate(natbot_instruction):
                    browser_view = self._get_current_browser_view_from_mapping()
                    print(browser_view)
                    print(
                        "\nChatbot: Given the browser content above, I want to perform the following action(s)."
                    )
                    print(f"{curr_instruction}")
                    print("\nChatbot: Does this seem right to you?")
                    print("  (1) Yes, this is correct.")
                    print("  (2) No, I want to change the objective.")
                    print("  (3) No, you should try again.")
                    print("  (4) No, I want to quit.")
                    user_input = input("> Your choice: ")

                    if user_input == "1":
                        next_instruction = self._get_compiled_instruction(
                            curr_instruction
                        )
                        if DONE_TOKEN in next_instruction:
                            break
                        print("\nGreat! I will now run the following code:")
                        print(next_instruction + "\n")
                        self._feed_instruction_to_agent(next_instruction)
                        self.objectives_in_chatbot_mode.append(self.objective)
                        self.commands_code_in_chatbot_mode.append(next_instruction)
                    elif user_input == "2":
                        print("Okay, let's try again.")
                        continue
                    elif user_input == "3":
                        print(
                            "Okay, I will try again. Please give me your objective again."
                        )
                    elif user_input == "4":
                        print("Exiting.")
                        break

    def save_chatbot_history(self):
        """Save the agent's state to a yaml."""
        logger.info("Saving the chatbot history to a yaml file.")
        objectives = self.objectives_in_chatbot_mode
        commands = self.commands_code_in_chatbot_mode

        # Save the objectives and commands to a yaml file.
        description = input(
            "> Give a natural language description of the task that was completed: "
        )
        data = {
            "description": description,
            "objectives": objectives,
            "commands": commands,
        }
        with open(self.chatbot_history_file, "w") as f:
            yaml.dump(data, f)

    def run(self):
        """Run the agent with the given objective."""
        if self.objective is None:
            logger.info("No objective given. Running the agent in chat mode.")
            self.chat()
        else:
            # Get the first instruction: either to go to a webpage or to search
            # Google. Then perform it.
            first_instruction = self._get_first_instruction()
            logger.info(first_instruction)
            self._feed_instruction_to_agent(first_instruction)

            # Iteratively get the next instruction and perform it.
            step = 0
            while step < self.max_steps:
                time.sleep(3)
                # Get the next instruction.
                natbot_instruction = self._get_natbot_response()
                logger.info(f"Natbot instruction: {natbot_instruction}")
                next_instruction = self._get_compiled_instruction(natbot_instruction)
                logger.info(f"Next instruction: {next_instruction}")
                if DONE_TOKEN in next_instruction:
                    logger.info("Done!")
                    break

                # Perform the next instruction.
                self._feed_instruction_to_agent(next_instruction, is_code=True)

                step += 1
