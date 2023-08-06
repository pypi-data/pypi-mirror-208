import whisper
from .video_utils import convert_video_to_audio, create_video_with_subtitles
from .translator import Translator
import os


class Transcriber(object):
    model = None
    model_type = None
    target_language = None
    language_model_type = None
    device = None
    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]

    @staticmethod
    def create_model():
        if Transcriber.model is None:
            try:
                Transcriber.model = whisper.load_model(
                    Transcriber.model_type, device=Transcriber.device
                )
            except Exception as e:
                print("Couldn't load model.")
                print(e)

    @staticmethod
    def transcribe(
        video_file,
        output_video_file=None,
        output_subtitle_file="output.srt",
        target_language=None,
        model_type="base",
        language_model_type="base",
        device="cpu",
    ):
        """Transcribe video file and generate SRT file.
        
        Args:
            video_file (str): Path to video file.

            output_video_file (str, optional): Path to output video file. Defaults to None.

            output_subtitle_file (str, optional): Path to output SRT file. Defaults to "output.srt".

            target_language (str, optional): Target language for translation. Defaults to None.

            model_type (str, optional): Model type. Defaults to "base".

            language_model_type (str, optional): Language model type. Defaults to "base".

            device (str, optional): Device to use. Defaults to "cpu".
        """
        if model_type not in Transcriber.AVAILABLE_MODELS:
            print(
                f"Invalid 'model_type'. Using base model. Available models: {Transcriber.AVAILABLE_MODELS}"
            )
            model_type = "base"

        # Set device
        Transcriber.device = device

        # Set target language
        Transcriber.target_language = target_language

        # Set language model type
        Transcriber.language_model_type = language_model_type

        # Set model type
        Transcriber.model_type = model_type

        # Create model
        Transcriber.create_model()

        if output_video_file is None:
            output_video_file = video_file.replace(".mp4", "_subtitled.mp4")

        # Try to transcribe audio
        transcript = None
        try:
            convert_video_to_audio(video_file, "temporary_audio.wav")

            print("Transcribing audio.")
            transcript = Transcriber.model.transcribe("temporary_audio.wav")
            print("Finished transcription.")

            os.remove("temporary_audio.wav")
        except Exception as e:
            print("Couldn't transcribe audio.")
            print(e)

        # Try to generate SRT file
        srt_content = None
        try:
            srt_content = Transcriber.generate_srt_file(transcript)
        except Exception as e:
            print("Couldn't generate SRT file.")
            print(e)

        print(srt_content)
        # Add .srt extension if not present
        if not output_subtitle_file.endswith(".srt"):
            output_subtitle_file += ".srt"

        # Write SRT file
        with open(output_subtitle_file, "w", encoding="utf-8") as f:
            f.write(srt_content)

        create_video_with_subtitles(video_file, output_subtitle_file, output_video_file)

    @staticmethod
    def generate_srt_file(transcript):
        srt_content = ""

        print("Starting generation of srt file.")
        print(f"Total lines: {len(transcript['segments'])}")
        for line in transcript["segments"]:
            # Add line number
            srt_content += str(line["id"]) + "\n"

            # Add timestamps
            srt_content += (
                Transcriber.format_seconds_to_srt_timestamp(line["start"])
                + " --> "
                + Transcriber.format_seconds_to_srt_timestamp(line["end"])
                + "\n"
            )

            # Add text
            text = line["text"].strip()
            if Transcriber.target_language is not None:
                # Translate text only if user wanted to translate text
                text = Translator.translate(
                    text,
                    source_language=transcript["language"],
                    target_language=Transcriber.target_language,
                    model_type=Transcriber.language_model_type,
                    device=Transcriber.device,
                ).strip()

                print(
                    f"- Line {line['id'] + 1} of {len(transcript['segments'])}: {line['text']}\n --> {text}"
                )
            else:
                print(
                    f"- Line {line['id'] + 1} of {len(transcript['segments'])}: {line['text']}"
                )
            srt_content += text + "\n"

            srt_content += "\n"

        return srt_content

    @staticmethod
    def format_seconds_to_srt_timestamp(seconds):
        milliseconds = round(seconds * 1000.0)

        hours = milliseconds // 3_600_000
        milliseconds -= hours * 3_600_000

        minutes = milliseconds // 60_000
        milliseconds -= minutes * 60_000

        seconds = milliseconds // 1_000
        milliseconds -= seconds * 1_000

        return f"{hours}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
