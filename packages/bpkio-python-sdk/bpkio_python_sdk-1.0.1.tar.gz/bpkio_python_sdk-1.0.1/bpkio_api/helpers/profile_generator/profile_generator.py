from typing import Dict


class TranscodingProfileGenerator:
    config = dict(
        preset="veryfast",
    )

    def __init__(self, config: Dict = {}) -> None:
        self.config.update(config)

    def generate(self, renditions):
        common = {
            "codecv": "h264",
            "preset": self.config["preset"],
        }

        jobs = []
        for r in renditions:
            if r["type"] == "video":
                jobs.append(
                    {
                        "level": r["level"],
                        "scale": f"-1:{r['resolution'][1]}",
                        "bitratev": r["bitrate"],
                        "profilev": r["profile"],
                        "frameratev": r["framerate"],
                    }
                )

            if r["type"] == "audio":
                audio_spec = {
                    "codeca": "aac",
                    "bitratea": r["bitrate"],
                    "loudnorm": "I=-23:TP=-1",
                }

                if r.get("muxed") is True:
                    common.update(audio_spec)

                else:
                    jobs.append(audio_spec)

        profile = {
            "packaging": {
                "--hls.client_manifest_version=": "4",
                "--hls.minimum_fragment_length=": "4",
            },
            "servicetype": "offline_transcoding",
            "transcoding": {
                "jobs": jobs,
                "common": common,
            },
        }

        return profile
