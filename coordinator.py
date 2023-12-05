from typing import List
from schema import AssistantRoleSetting, UserRoleSetting, Message, BaseRoleSetting,ScheduleItem, ScheduleItem
import os
import json
import copy
# from openai import OpenAI
from dotenv import load_dotenv
import openai


load_dotenv()
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")



# client = OpenAI(base_url=os.getenv("OPENAI_API_BASE"),
#                 api_key=os.getenv("OPENAI_API_KEY"))

assign_prompt_tpl = """
请根据仔细分析以下对话记录，针对最后一条记录从以下提供的对话角色中，选择需要回复的角色:

对话角色:
{role_description}

请使用 json 格式回复，格式如下，必须包含以上所有提供的角色且不能出现以上没有提供的角色:
{{
    \"角色名称1\": true,  // 表示角色1需要回复
    \"角色名称2\": false, // 表示角色2不需要回复
    ...
}}

历史对话记录:
{history_conversation}

最后一条记录:
{last_conversation}
"""


class CoordinatorV2:
    DEFAULT_COORDINATOR_SYS_MSG = '你是一个优秀的对话场景分析师，你可以根据对话内容，找出下一个需要回复的角色'

    def __init__(self,
                 schedule_role_ls: List[ScheduleItem],
                 default_schedule_role: ScheduleItem,
                 system_msg: str | None = None):

        self.schedule_role_ls = schedule_role_ls
        self.default_schedule_role = default_schedule_role
        self.system_msg = system_msg or self.DEFAULT_COORDINATOR_SYS_MSG
        self.ctx_msg: List[Message] | None = None

    # def run(self,
    #         history: List[Message],
    #         max_round: int = 5
    #         ) -> List[Message]:
    #     self.reset()
    #     self.ctx_msg = copy.deepcopy(history)
    #     result = self.assign_job(history=copy.deepcopy(history))
    #     return result

    # def step(self):
    #     pass
    #
    # def assistant_reply(self):
    #     pass

    def assign_job(self, history: List[Message]) -> List[ScheduleItem]:

        prompt = assign_prompt_tpl.format(role_description=self.prompt_role_description(),
                                          history_conversation=self.prompt_history_conversation(history),
                                          last_conversation=self.prompt_last_conversation(history))
        # print(prompt)
        # completion = client.chat.completions.create(
        #     model='gpt-4',
        #     seed=1,
        #     response_format={"type": "json_object"},
        #     temperature=0.0,
        #     messages=[
        #         {"role": "system", "content": self.system_msg},
        #         {"role": "user", "content": prompt},
        #     ]
        # )
        print(prompt)
        completion = openai.ChatCompletion.create(
                model='gpt-4',
                seed=1,
                response_format={"type": "json_object"},
                temperature=0.0,
                messages=[
                    {"role": "system", "content": self.system_msg},
                    {"role": "user", "content": prompt},
                ]
        )

        # 解析返回 json 数据
        result = json.loads(completion.choices[0].message.content)

        # 提取返回的角色
        reply_roles = [role for role in self.schedule_role_ls if result.get(f'角色{role.id}', False) is True]
        print('openai 返回: ', [(x.role.name, x.role.role_id) for x in reply_roles])

        # 如果没有角色回复，则选择默认角色进行回复
        if len(reply_roles) == 0:
            reply_roles = [self.default_schedule_role]

        return reply_roles

    def prompt_default_role(self) -> str:
        return f'角色{self.default_schedule_role.id}'

    def prompt_role_description(self) -> str:
        prompt_ls = []
        for schedule_role in self.schedule_role_ls:
            prompt = f'- `角色{schedule_role.id}`: {schedule_role.role.description}; {schedule_role.skill.skill_desc if schedule_role.skill else ""}'
            prompt_ls.append(prompt)

        return '\n'.join(prompt_ls)

    @staticmethod
    def prompt_history_conversation(history: List[Message]) -> str:
        return '\n'.join([f'{msg.name}: {msg.content}' for msg in history])

    @staticmethod
    def prompt_last_conversation(history: List[Message]) -> str:
        last_ctx_msg = history[-1]
        return f'{last_ctx_msg.name}: {last_ctx_msg.content}'

    def reset(self):
        self.ctx_msg = []
