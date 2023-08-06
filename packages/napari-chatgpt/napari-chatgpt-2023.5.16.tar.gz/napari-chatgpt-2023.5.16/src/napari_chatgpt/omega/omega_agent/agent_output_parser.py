import re
import traceback
from typing import Union

from langchain.agents import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish

from napari_chatgpt.omega.omega_agent.prompts import \
    OMEGA_FORMAT_INSTRUCTIONS


class OmegaAgentOutputParser(AgentOutputParser):
    def get_format_instructions(self) -> str:
        return OMEGA_FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:

        try:
            cleaned_output = text.strip()

            # lines = cleaned_output.splitlines(keepends=True)
            words = re.split(r'(\s+)', cleaned_output)

            # Simple state machine to robustly parse output:
            action = ''
            input = ''
            state = 'start'
            for word in words:
                normalised_word = word.strip().lower()
                if 'action:' == normalised_word or '**action:**' == normalised_word:
                    state = 'action'
                    continue
                elif 'input:' == normalised_word or '**input:**' == normalised_word:
                    state = 'input'
                    continue

                if state == 'action':
                    action += word
                elif state == 'input':
                    input += word

            action = action.strip()
            input = input.strip()

            # Clean up the input, necessary for Bard:
            input = input.split("FinalAnswer:")[0].strip()

            if action.lower() == "finalanswer":
                return AgentFinish({"output": input}, text)
            else:
                return AgentAction(action, input, text)

        except Exception as e:
            traceback.print_exc()
            raise e
