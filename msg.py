#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 应该做成回调函数。备注一下
def msg_list():
    # 指令列表
    commands = {
        u'紧急制动': emergency,

        u'去充电': charge,

        u'重新定位': remap,

        u'手动模式': manual_mode,

        u'自动模式': auto_mode,

        u'设备自检': check_device
    }
    # 匹配指令
    command_match = False
    for key_word in commands:
        if re.match(key_word, message.content):
            # 指令匹配后，设置默认状态
            set_user_state(openid, 'default')
            response = commands[key_word]()
            command_match = True
            break
    if not command_match:
        # 匹配状态
        state = get_user_state(openid)
        # 关键词、状态都不匹配，缺省回复
        if state == 'default' or not state:
            response = command_not_found()
        else:
            response = state_commands[state]()
    return response
