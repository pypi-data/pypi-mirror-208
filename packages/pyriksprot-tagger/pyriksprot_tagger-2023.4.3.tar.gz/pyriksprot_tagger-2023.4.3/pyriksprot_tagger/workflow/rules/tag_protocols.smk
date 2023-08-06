# type: ignore
# pylint: skip-file, disable-all, syntax-error

"""
PoS tags Parla-CLARIN XML files using Stanza.
"""
from os import makedirs
from os.path import join as jj

from pyriksprot import tag_protocol_xml

from pyriksprot.workflows.tag import TaggerProvider, TaggerRegistry
from pyriksprot.configuration import Config
from pyriksprot_tagger import StanzaTaggerFactory, check_cuda

typed_config: Config = typed_config
disable_gpu: bool = config.get("disable_gpu", 0) == 1

check_cuda()

makedirs(typed_config.target.folder, exist_ok=True)

def create_factory():
    typed_config.tagger_opts['use_gpu'] = not disable_gpu
    return TaggerProvider.tagger_factory().create()

def tagger():
    if StanzaTaggerFactory.identifier in TaggerRegistry.instances:
        return TaggerRegistry.instances[StanzaTaggerFactory.identifier]
    return TaggerRegistry.get(create_factory())

rule tag_protocols:
    message:
        "step: tag_protocols"
    input:
        filename=jj(typed_config.source.folder, "{year}", "{basename}.xml"),
    output:
        filename=jj(typed_config.target.folder, "{year}", "{basename}.zip"),
    run:
        try:
            tag_protocol_xml(
                input.filename,
                output.filename,
                tagger(),
                storage_format="json",
            )
        except Exception as ex:
            print(f"failed: tag_protocols {input.filename} --output-filename {output.filename}")
            raise
