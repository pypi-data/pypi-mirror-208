import logging

from ..codecstrings import CodecStringParser
from bpkio_api.helpers.handlers.dash import DASHHandler

from mpd_parser.parser import MPD


class DashAnalyser:
    def __init__(self, handler: DASHHandler) -> None:
        self.handler = handler

    def analyze(self):
        dash_obj: MPD = self.handler.document

        if len(dash_obj.periods) > 1:
            logging.warning(
                "More than 1 period found. Only the first period will be taken into account"
            )

        period = dash_obj.periods[0]

        audio_renditions = {}
        video_renditions = {}

        for adaptation_set in period.adaptation_sets:
            if adaptation_set.content_type == "audio":
                for representation in adaptation_set.representations:
                    codec = CodecStringParser.parse_codec_string(
                        representation.codecs or adaptation_set.codecs
                    )

                    codec["bitrate"] = representation.bandwidth
                    audio_renditions[representation.id] = codec

            if adaptation_set.content_type == "video":
                for representation in adaptation_set.representations:
                    codec = CodecStringParser.parse_codec_string(
                        representation.codecs or adaptation_set.codecs
                    )

                    codec["resolution"] = (representation.width, representation.height)
                    codec["bitrate"] = representation.bandwidth
                    codec["framerate"] = representation.frame_rate
                    video_renditions[representation.id] = codec

        return [*video_renditions.values(), *audio_renditions.values()]
