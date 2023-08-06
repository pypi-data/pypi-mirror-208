import bpkio_api.helpers.profile_generator as PG
from bpkio_api.helpers.handlers import ContentHandler, DASHHandler, HLSHandler


def make_transcoding_profile(handler: ContentHandler):
    analyser = None
    if isinstance(handler, HLSHandler):
        analyser = PG.HlsAnalyser(handler)
    elif isinstance(handler, DASHHandler):
        analyser = PG.DashAnalyser(handler)
    else:
        raise Exception("Unsupported handler type")

    renditions = analyser.analyze()

    generator = PG.TranscodingProfileGenerator()

    return generator.generate(renditions)
