from typing import Any
from pepperbot.extensions.log import logger
from pepperbot.utils.common import await_or_sync


class ActionChainBase:
    sequence = []
    index = 0


class OnebotV11ActionEvent(ActionChainBase):
    def group_message(self, callback: Any):
        self.sequence.append(("group_message", callback))
        return self

    def friend_message(self, callback: Any):
        self.sequence.append(("friend_message", callback))
        return self


class ActionChain(OnebotV11ActionEvent):
    def __init__(self, timeout=30):
        return self

    async def __run(self):
        pass

    def __await__(self):
        # doing job
        return self.__run()


callback = lambda x: x


async def test():
    chain = ActionChain()
    await chain.group_message(callback).friend_message(callback).__await__()


action_chains = {}


def generate_action_event():
    pass


def validate_action_chain_callback():
    """参数和class_handler中的event_handler一致"""
    pass


async def run_action_chains():
    event_name = ""
    source_id = ""
    mode = ""

    # 先确定消息来源——跨平台的来源判断，当前action_chain所定义的bot_route内，提及的消息来源的平台，都应该要判断
    if not source_id and mode:
        return

    # 再traverse所有该消息来源绑定的action_chain
    binding_action_chains = action_chains[mode][source_id]

    for action_chain in binding_action_chains:
        # 如果event符合进度，下一步(执行当前进度绑定的回调函数)
        if action_chain.pointer == event_name:
            target_method = action_chain.methods[action_chain.pointer]

            try:
                result = await await_or_sync(target_method)
                # 推进一步
                if result:
                    action_chain.next()
                    logger.success("")
                else:
                    logger.info("")
            except Exception as e:
                logger.exception("执行出错")


def clear_timeout_action_chains():
    pass
