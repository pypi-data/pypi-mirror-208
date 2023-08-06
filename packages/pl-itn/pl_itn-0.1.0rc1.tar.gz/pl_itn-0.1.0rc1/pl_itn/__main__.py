import argparse
import yaml
from pathlib import Path
from signal import signal, SIGINT, SIGTERM

from pl_itn import Normalizer, package_root
from pl_itn.exceptions import InterruptException, gentle_interrupt_handler
from pl_itn.logging import ITN_logger

def main():
    args = parser()

    itn_logger = ITN_logger("pl_itn")
    itn_logger.set_level(args.log_level)

    if args.config:
        with args.config.open() as config_file:
            config = yaml.safe_load(config_file)
        args.tagger = Path(config.get("out_dir")) / config.get("tagger_fname")
        args.verbalizer = Path(config.get("out_dir")) / config.get("verbalizer_fname")

    normalizer = Normalizer(
        tagger_fst_path=args.tagger,
        verbalizer_fst_path=args.verbalizer,
    )

    if args.interactive:
        run_interactive(normalizer)
    else:
        run_single(normalizer, args.text)


def parser():
    parser = argparse.ArgumentParser(
        description="Inverse Text Normalization based on Finite State Transducers"
    )

    input_args = parser.add_mutually_exclusive_group(required=True)
    input_args.add_argument("-t", "--text", type=str, help="Input text")
    input_args.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="If used, demo will process phrases from stdin interactively.",
    )

    parser.add_argument(
        "--tagger", type=Path, default=(package_root / "grammars/tagger.fst")
    )
    parser.add_argument(
        "--verbalizer", type=Path, default=(package_root / "grammars/verbalizer.fst")
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Optionally provide yaml config with tagger and verbalizer paths.",
    )
    parser.add_argument("--log-level", choices=["debug", "info"], default="info")

    return parser.parse_args()


def run_interactive(normalizer: Normalizer):
    signal(SIGINT, gentle_interrupt_handler)  # keyboard interrupt
    signal(SIGTERM, gentle_interrupt_handler)  # terminal interrupt

    print("Enter your phrase:")

    while True:
        try:
            phrase = input()
            print(normalizer.normalize(phrase))
            print()
        except InterruptException:
            break


def run_single(normalizer: Normalizer, text: str) -> None:
    print(normalizer.normalize(text))


if __name__ == "__main__":
    main()
