from schema import (MutilAssistantChatRoomSetting, ScheduleItem, UserRoleSetting,
                    AssistantType, AssistantRoleSetting, Message, SkillSetting)
from coordinator import CoordinatorV2
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
        content="我老婆最近脸部出现很多痘痘，怎么办？"
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
        AssistantRoleSetting(
            role_id='a',
            name="咨询助理",
            description="负责接待客户",
            type=AssistantType.with_skills,
            skills=[SkillSetting(skill_id='s0',
                                 skill_desc='引导客户提出问题'),
                    SkillSetting(skill_id='s1',
                                 skill_desc='对于接待女性客户或者有关美容方面的问题的客户更加在行'),
                    SkillSetting(skill_id='s2',
                                 skill_desc='对于接待男性客户或者有关健身方面的问题更加专业')]
        ),
        AssistantRoleSetting(
            role_id='b',
            name="销售助理",
            description="回复关于商品价格的相关信息以及优惠方案",
            type=AssistantType.no_skills
        ),
        AssistantRoleSetting(
            role_id='c',
            name="售后助理",
            description="负责处理客户的退货、退款、换货等售后需求",
            type=AssistantType.no_skills
        ),
        AssistantRoleSetting(
            role_id='d',
            name="区域经理",
            description="负责处理产品代理商的问题",
            type=AssistantType.no_skills
        ),
        AssistantRoleSetting(
            role_id='e',
            name="技术客服",
            description="负责处理客户关于产品使用上的技术问题",
            type=AssistantType.no_skills
        ),
    ]
)


schedule_role_ls: List[ScheduleItem] = []
schedule_idx_to_item: Dict[str, ScheduleItem] = {}

idx = 0
for role in room_setting.roles:
    skills = role.skills or [None]

    for skill in skills:
        idx += 1
        sc_item = ScheduleItem(id=str(idx), role=role, skill=skill)
        schedule_role_ls.append(sc_item)
        schedule_idx_to_item[str(idx)] = sc_item


if __name__ == '__main__':
    # df_data = pd.DataFrame([x.model_dump() for x in test_data])[['role', 'name', 'content']]
    # y_test = []

    for i in range(len(test_data)):

        coordinator = CoordinatorV2(schedule_role_ls=schedule_role_ls,
                                    default_schedule_role=schedule_role_ls[1])

        roles = coordinator.assign_job(history=test_data[:i + 1])
        print('调度结果: ', [(x.role.name, x.skill) for x in roles])
        print('下一个实际回复: ', test_data[i+1].name)
        print('-' * 50)

    #     break
    #     y_test.append(','.join([x.name for x in roles]))
    #     break
    #
    # df_data['label'] = df_data['name'].shift(-1)
    # df_data['y_test'] = y_test
    #
    # df_data.to_csv('result.csv')
