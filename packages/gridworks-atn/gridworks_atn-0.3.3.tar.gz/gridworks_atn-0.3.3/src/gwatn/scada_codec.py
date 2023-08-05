from gwproto import Decoders
from gwproto import MQTTCodec
from gwproto import create_message_payload_discriminator
from gwproto.messages import GtShStatus_Maker
from gwproto.messages import PowerWatts_Maker
from gwproto.messages import SnapshotSpaceheat_Maker


ScadaMessageDecoder = create_message_payload_discriminator(
    model_name="GwprotoMessageDecoder", module_names=["gwproto.messages"]
)


class ScadaCodec(MQTTCodec):
    def __init__(self):
        super().__init__(
            Decoders.from_objects(
                [
                    GtShStatus_Maker,
                    SnapshotSpaceheat_Maker,
                    PowerWatts_Maker,
                ],
                message_payload_discriminator=ScadaMessageDecoder,
            )
        )

    def validate_source_alias(self, source_alias: str):
        pass
