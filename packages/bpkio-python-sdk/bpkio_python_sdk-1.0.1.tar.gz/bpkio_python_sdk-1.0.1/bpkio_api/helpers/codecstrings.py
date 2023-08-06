from typing import Dict, List


class CodecStringParser:
    @staticmethod
    def parse_multi_codec_string(string: str) -> List[Dict]:
        codecstrings = [c.strip() for c in string.split(",")]
        return [CodecStringParser.parse_codec_string(c) for c in codecstrings]

    @staticmethod
    def parse_codec_string(codecstring: str) -> Dict:
        (codec, *codec_data) = codecstring.split(".")

        match codec:
            case "avc1" | "avc3":
                return CodecStringParser._parse_avc(codec_data[0])
            case "mp4a":
                return CodecStringParser._parse_aac(codec_data)
            case _:
                raise Exception(f"Codec '{codec}' invalid or not yet implemented")

    @staticmethod
    def _parse_avc(codec_data):
        H264Profile = {"42": "baseline", "4D": "main", "64": "high"}
        H264Level = {
            "0A": "1",
            "0B": "1.1",
            "0C": "1.2",
            "0D": "1.3",
            "14": "2",
            "15": "2.1",
            "16": "2.2",
            "1E": "3",
            "1F": "3.1",
            "20": "3.2",
            "28": "4",
            "29": "4.1",
            "2A": "4.2",
            "32": "5",
            "33": "5.1",
            "34": "5.2",
            "3C": "6",
            "3D": "6.1",
            "3F": "6.2",
        }

        try:
            profile, level = codec_data[:2].upper(), codec_data[4:6].upper()
            return dict(
                cc="H264",
                type="video",
                codec="AVC/H.264",
                profile=H264Profile[profile],
                level=H264Level[level],
            )
        except Exception:
            raise Exception(f"Invalid or unsupported H264 codec data: {codec_data}")

    @staticmethod
    def _parse_aac(codec_data):
        oti, mode = codec_data

        AAC_OTI = {
            "40": "MPEG-4 AAC",
            "66": "MPEG-2 AAC Main Profile",
            "67": "MPEG-2 AAC Low Complexity Profile",
            "68": "MPEG-2 AAC Scalable Sampling Rate Profile",
            "69": "MPEG-2 Audio Part 3",
            "6B": "MPEG-1 Part 3",
        }
        AAC_MODE = {"1": "Main", "2": "Low-Complexity AAC"}

        try:
            return dict(
                cc="AAC", type="audio", codec=AAC_OTI[oti.upper()], mode=AAC_MODE[mode]
            )
        except Exception:
            raise Exception(f"Invalid or unsupported H264 codec data: {codec_data}")
