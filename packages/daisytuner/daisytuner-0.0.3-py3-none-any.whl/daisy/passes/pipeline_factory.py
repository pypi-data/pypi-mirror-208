from dace.transformation import pass_pipeline as ppl

from daisy.utils import host
from daisy.architecture import architecture
from daisy.passes.expansion_pass import ExpansionPass
from daisy.passes.transfer_tuner_pass import TransferTunerPass


class PipelineFactory:
    @classmethod
    def static(cls, topK: int = 3) -> ppl.Pipeline:
        pipeline = ppl.Pipeline(
            [ExpansionPass(), TransferTunerPass(hostname=None, arch=None, topK=topK)]
        )
        return pipeline

    @classmethod
    def full(cls, topK: int = 3) -> ppl.Pipeline:
        pipeline = ppl.Pipeline(
            [
                ExpansionPass(),
                TransferTunerPass(
                    hostname=host(), arch=architecture()["cpu"], topK=topK
                ),
            ]
        )
        return pipeline
