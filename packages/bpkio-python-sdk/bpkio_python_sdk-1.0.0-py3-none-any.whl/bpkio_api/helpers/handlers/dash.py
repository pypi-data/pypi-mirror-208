from datetime import datetime, timedelta
from typing import Dict, List

from lxml import etree
from mpd_parser.parser import MPD, Parser

from bpkio_api.helpers.times import iso8601_duration_to_float

from .xml import XMLHandler


class DASHHandler(XMLHandler):
    content_types = ["application/dash+xml"]
    file_extensions = [".mpd", ".dash"]

    uri_attributes = ["initialization", "media"]
    uri_elements = ["BaseURL"]

    def __init__(self, url, content: bytes | None = None):
        super().__init__(url, content)
        self._document: MPD = None

    @property
    def document(self) -> MPD:
        # if not self._document:
        #    self._document = Parser.from_string(self.content.decode())
        # return self._document
        return Parser.from_string(self.content.decode())

    @property
    def xml_document(self) -> etree._Element:
        return etree.fromstring(self.content)

    def read(self):
        return "Handling DASH file."

    @staticmethod
    def is_supported_content(content):
        try:
            root = etree.fromstring(content)
            if root.tag == "{urn:mpeg:dash:schema:mpd:2011}MPD":
                return True
        except etree.XMLSyntaxError:
            pass
        return False

    def is_live(self):
        if self.document.type == "dynamic":
            return True
        else:
            return False

    def get_duration(self) -> float:
        """Extract duration from the MPD if it's for a VOD

        Returns:
            float: duration in seconds
        """
        if self.is_live():
            return -1
        else:
            return iso8601_duration_to_float(self.document.media_presentation_duration)

    def extract_info(self) -> Dict:
        info = {
            "format": "DASH",
            "type": "Live (dynamic)" if self.is_live() else "VOD (static)",
            "duration (in sec)": "N/A" if self.is_live() else self.get_duration(),
        }

        return info

    def extract_timeline(self):
        timeline = []

        for i, period in enumerate(self.document.periods):
            duration = period.duration
            if not duration and len(self.document.periods) > i + 1:
                duration = calculate_effective_duration(
                    period.start, self.document.periods[i + 1].start
                )

            info = {
                "period": period.id,
                "start": period_start_time(
                    self.document.availability_start_time, period.start
                ),
                "duration": duration,
                "baseUrl": period.base_urls[0].text if len(period.base_urls) else "",
            }
            timeline.append(info)

        return timeline

    def extract_features(self) -> List[Dict] | None:
        features = []

        for period in self.document.periods:
            for adaptation_set in period.adaptation_sets:
                for representation in adaptation_set.representations:
                    res = (
                        "{} x {}".format(
                            representation.width,
                            representation.height,
                        )
                        if representation.width
                        else ""
                    )

                    features.append(
                        {
                            "period": period.id,
                            "adaptation_set": adaptation_set.id,
                            "type": adaptation_set.content_type,
                            "bandwidth": representation.bandwidth,
                            "codecs": representation.codecs or adaptation_set.codecs,
                            "resolution": res,
                            "language": adaptation_set.lang,
                        }
                    )

        return features


def period_start_time(availability_start_time: str, start: str) -> str:
    if availability_start_time:
        availability_start_time_dt = datetime.fromisoformat(
            availability_start_time.replace("Z", "+00:00")
        )
        start_duration = float(start.replace("PT", "").replace("S", ""))
        start_time_dt = availability_start_time_dt + timedelta(seconds=start_duration)
        return start_time_dt.strftime("%Y-%m-%d %H:%M:%S")


def calculate_effective_duration(start_time, next_start_time):
    current_start = float(start_time.replace("PT", "").replace("S", ""))
    next_start = float(next_start_time.replace("PT", "").replace("S", ""))
    return next_start - current_start
