ROUTING_KEY_FROM_IDX = 0
ROUTING_KEY_SASSY_MESSAGE_IDX = 1
ROUTING_KEY_TO_IDX = 2


def from_actor(routing_key_base):
    return routing_key_base.split(".")[ROUTING_KEY_FROM_IDX]


def to_actor(routing_key_base):
    return routing_key_base.split(".")[ROUTING_KEY_TO_IDX]


def sassy_message(routing_key_base):
    return routing_key_base.split(".")[ROUTING_KEY_SASSY_MESSAGE_IDX]


class HackTypeBase:
    def __init__(self, routing_key_base, agent=None):
        self.from_smq_actor_alias = from_actor(routing_key_base)
        self.sassy_message = sassy_message(routing_key_base)
        self.to_smq_actor_alias = to_actor(routing_key_base)
        self.agent = agent
        self.is_debug_mode = False
        self.routing_key_base = routing_key_base
        self.payload = {}
