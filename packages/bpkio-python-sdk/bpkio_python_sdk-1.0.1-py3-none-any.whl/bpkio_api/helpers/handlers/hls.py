from functools import lru_cache
from typing import Dict, List

import m3u8

from bpkio_api.exceptions import BroadpeakIoHelperError

from .generic import ContentHandler


class HLSHandler(ContentHandler):
    content_types = ["application/x-mpegurl", "application/vnd.apple.mpegurl"]
    file_extensions = [".m3u8", ".hls"]

    def __init__(self, url, content: bytes | None = None):
        super().__init__(url, content)
        self._document: m3u8.M3U8 = None

    @property
    def document(self) -> m3u8.M3U8:
        if not self._document:
            self._document = m3u8.loads(content=self.content.decode(), uri=self.url)
        return self._document

    def read(self):
        return "Handling HLS file."

    @staticmethod
    def is_supported_content(content):
        return content.decode().startswith("#EXTM3U")

    def has_children(self) -> bool:
        if self.document.is_variant:
            return True
        return False

    def get_child(self, index: int):
        try:
            return HLSHandler(url=self.document.playlists[index - 1].absolute_uri)
        except IndexError as e:
            raise BroadpeakIoHelperError(
                status_code=404,
                message=f"The HLS manifest only has {len(self.document.playlists)} renditions.",
                original_message=e.args[0],
            )

    @lru_cache()
    def _fetch_sub(self, uri):
        return m3u8.load(uri)

    def is_live(self):
        """Checks if the HLS is a live stream (ie. without an end)

        Returns:
            bool
        """
        # Check the first sub-playlist
        sub = self._fetch_sub(self.document.playlists[0].absolute_uri)
        if not sub.is_endlist:  # type: ignore
            return True
        else:
            return False

    def get_duration(self):
        """Calculates the duration of the stream (in seconds)

        Returns:
            int
        """
        if self.is_live():
            return -1
        else:
            sub = self._fetch_sub(self.document.playlists[0].absolute_uri)
            return sum([seg.duration for seg in sub.segments])

    def num_segments(self):
        """Calculates the number of segments in the stream

        Returns:
            int
        """
        sub = self._fetch_sub(self.document.playlists[0].absolute_uri)
        return len(sub.segments)
    
    def has_muxed_audio(self) -> bool:
        """Checks is the audio stream is muxed in with video
        
        Returns:
            bool
        """
        for media in self.document.media:
            if media.type == "AUDIO":
                if media.uri is None:
                    return True
        return False

    def extract_info(self) -> Dict:
        info = {
            "format": "HLS",
            "type": "Live" if self.is_live() else "VOD",
            "duration (in sec)": "N/A" if self.is_live() else self.get_duration(),
            "segments": self.num_segments(),
        }

        return info

    def extract_timeline(self):
        pass

    def extract_features(self) -> List[Dict]:
        """Extracts essential information from the HLS manifest"""
        arr = []
        index = 0

        if self.document.is_variant:
            for playlist in self.document.playlists:
                index += 1

                si = playlist.stream_info
                res = (
                    "{} x {}".format(
                        si.resolution[0],
                        si.resolution[1],
                    )
                    if si.resolution
                    else ""
                )

                arr.append(
                    dict(
                        index=index,
                        type="variant",
                        manifest=playlist.uri,
                        bandwidth=playlist.stream_info.bandwidth,
                        codecs=playlist.stream_info.codecs,
                        resolution=res,
                        url=playlist.absolute_uri,
                    )
                )

            for media in self.document.media:
                index += 1
                arr.append(
                    dict(
                        index=index,
                        type="media",
                        manifest=media.uri,
                        language=media.language,
                        url=media.absolute_uri,
                    )
                )

        return arr
