from schema import (
    MutilAssistantChatRoomSetting, ScheduleItem, UserRoleSetting,
    SkillType, AgentRoleSetting, Message, SkillSetting,
)
from scheduler import AgentScheduler
from typing import List, Dict

test_data: List[Message] = [
    Message(
        role="user", name="客户",
        content="你好"
    ),
    Message(
        role="assistant", name="咨询助理",
        content="你好，有什么我可以帮你的吗？"
    ),
    Message(
        role="user", name="客户",
        content="我老婆最近使用您家产品后脸部还是出现很多痘痘，怎么办？"
    ),
    Message(
        role="assistant", name="咨询助理",
        content="可能是由于睡眠不足引起的内分泌失调"
    ),
    Message(
        role="assistant", name="咨询助理",
        content="也有可能是由于现在的天气比较干燥造成的，希望我的解答能帮助到您"
    ),
    Message(
        role="user", name="客户",
        content="现在的男士护肤方面产品有什么优惠吗?"
    ),
    Message(
        role="assistant", name="销售助理",
        content="由于现在是店庆期间，现在的产品买一送一的有优惠活动，您可以在下单时使用优惠券"
    ),
    Message(
        role="user", name="客户",
        content="其实我是一个专业的代理公司，看了你们的产品后感觉挺好的，有合作机会吗？"
    ),
    Message(
        role="assistant", name="区域经理",
        content="我们是有区域代理业务的，请问你是哪一个区域的？"
    ),
    Message(
        role="user", name="客户",
        content="我是在中国华南地区一带的"
    ),
]

room_setting = MutilAssistantChatRoomSetting(
    room_description="现在是接待进店的客人，根据客人需求进行服务",
    roles=[
        UserRoleSetting(
            name="客户",
            description="聊天中咨询问题的客户"
        ),
        AgentRoleSetting(
            role_id='a',
            name="咨询助理",
            description="负责接待客户",
            type=SkillType.with_skills,
            skills=[SkillSetting(skill_id='s0',
                                 skill_desc='引导客户提出问题'),
                    SkillSetting(skill_id='s1',
                                 skill_desc='对于接待女性客户或者有关美容方面的问题的客户更加在行'),
                    SkillSetting(skill_id='s2',
                                 skill_desc='对于接待男性客户或者有关健身方面的问题更加专业')]
        ),
        AgentRoleSetting(
            role_id='b',
            name="销售助理",
            description="回复关于商品价格的相关信息以及优惠方案",
            type=SkillType.no_skills
        ),
        AgentRoleSetting(
            role_id='c',
            name="售后助理",
            description="负责处理客户的退货、退款、换货等售后需求",
            type=SkillType.no_skills
        ),
        AgentRoleSetting(
            role_id='d',
            name="区域经理",
            description="负责处理产品代理商的问题",
            type=SkillType.no_skills
        ),
        AgentRoleSetting(
            role_id='e',
            name="技术客服",
            description="负责处理客户关于产品使用上的技术问题",
            type=SkillType.no_skills
        ),
    ]
)

agent_role_ls: List[ScheduleItem] = []
human_role: ScheduleItem | None = None
agent_idx_to_item: Dict[str, ScheduleItem] = {}

idx = 0
for role in room_setting.roles:
    if type(role) is UserRoleSetting:
        idx += 1
        human_role = ScheduleItem(id=str(idx), role=role)
    elif type(role) is AgentRoleSetting:
        skills = role.skills or [None]

        for skill in skills:
            idx += 1
            sc_item = ScheduleItem(id=str(idx), role=role, skill=skill)
            agent_role_ls.append(sc_item)
            agent_idx_to_item[str(idx)] = sc_item
    else:
        raise Exception('未知的角色类型')

if __name__ == '__main__':


    history = test_data[:3]
    while True:
        coordinator = AgentScheduler(human_role=human_role,
                                     agent_role_ls=agent_role_ls,
                                     default_schedule_role=agent_role_ls[1],
                                     history=history)
        reply_msgs = coordinator.run()
        history.extend(reply_msgs)

        user_content = input('输入客户回复内容: ')
        history.append(Message(role='user', name='客户', content=user_content))
        if user_content == 'exit':
            break
