import os
import json
from script.parse_srt import parse_srt
from script.emotion_analysis import (
    analyze_individual_sentences,
    group_and_average,
    group_by_individual_scores
)
from script.utils import extract_highest_groups
from script.plot import EmotionTrendPlotter
from speech.emotion_analysis import EmotionSRTProcessor


class EmotionAnalyzer:
    """Handles emotion analysis tasks like processing SRT files and saving results."""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def analyze_emotions(self, srt_file, work_dir):
        """Perform emotion analysis on the SRT file."""
        self.logger.info(f"Starting emotion analysis for: {srt_file}")

        # Parse subtitles
        subtitles = parse_srt(srt_file)
        self.logger.info(f"Loaded {len(subtitles)} subtitles from SRT file.")

        # Perform individual and group emotion analyses
        individual_results = analyze_individual_sentences(
            subtitles=subtitles,
            model_name=self.config["emotion_model"]
        )
        grouped_ind = group_by_individual_scores(individual_results, group_size=64, step=4)
        grouped_comb = group_and_average(
            subtitles=subtitles, group_size=64, step=4,
            model_name=self.config["emotion_model"], max_length=512
        )

        # Extract highest emotion groups
        highest_results = {
            "individual": extract_highest_groups(*grouped_ind[:3]),
            "combined": extract_highest_groups(*grouped_comb[:3])
        }

        # Save results and generate plots
        self._save_results(highest_results, work_dir)
        self._plot_emotion_trends(grouped_comb, work_dir)

    def _save_results(self, highest_results, work_dir):
        """Save the highest emotion groups to a JSON file."""
        output_json = os.path.join(work_dir, "emotion_highest.json")
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(highest_results, f, ensure_ascii=False, indent=4)
        self.logger.info(f"Emotion analysis results saved to: {output_json}")

    def _plot_emotion_trends(self, grouped_comb, work_dir):
        """Plot and save emotion trends."""
        plot_file = os.path.join(work_dir, "emotion_trends.png")

        # Extract components from grouped_comb
        times, scores, labels = grouped_comb[:3]
        positive_group, negative_group = None, None  # Replace with actual data if available

        EmotionTrendPlotter.plot_emotion_trends(
            times=times,
            scores=scores,
            labels=None,
            positive_group=positive_group,
            negative_group=negative_group,
            output_file=plot_file,
        )
        self.logger.info(f"Emotion trend plot saved to: {plot_file}")

    def process_speech_emotions(self, work_dir):
        """Perform speech emotion analysis and save SRT with emotion scores."""
        speech_analyzer = EmotionSRTProcessor(work_dir=work_dir)
        speech_analyzer.process_and_save()
