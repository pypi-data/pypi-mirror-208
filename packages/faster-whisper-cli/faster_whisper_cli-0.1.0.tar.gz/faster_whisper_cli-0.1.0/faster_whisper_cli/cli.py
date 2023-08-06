import argparse
import os
from faster_whisper import WhisperModel


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Generate .srt file from an input MP3 file")
    parser.add_argument("input_file", help="Input MP3 file")
    parser.add_argument("-o", "--output", default="output.srt",
                        help="Output .srt file (default: output.srt)")

    # Parse arguments
    args = parser.parse_args()

    # Check if input file exists
    if not os.path.isfile(args.input_file):
        print("Input file %s does not exist." % args.input_file)
        exit()

    # Create WhisperModel instance
    model_size = "large-v2"
    model = WhisperModel(model_size, device="cuda", compute_type="float16")

    # Generate subtitle
    segments, info = model.transcribe(args.input_file, beam_size=5)

    # Write subtitle to output file
    with open(args.output, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments):
            f.write(str(i+1) + "\n")
            f.write("{:.2f}".format(segment.start) + " --> " +
                    "{:.2f}".format(segment.end) + "\n")
            f.write(segment.text + "\n")
            f.write("\n")

    print("Subtitle file saved to %s" % args.output)


if __name__ == "__main__":
    main()
