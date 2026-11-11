import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("media", Path(__file__).parents[1] / "scripts/media.py")
media = importlib.util.module_from_spec(spec)
spec.loader.exec_module(media)


class MediaTests(unittest.TestCase):
    def setUp(self):
        self.transcript = {"source_sha256": "hash", "segments": [
            {"id": 0, "start": 0, "end": 5, "text": "Veja o botão."}
        ]}
        self.selection = [{"timestamp": 2, "segment_id": 0, "reason": "Botão citado na fala."}]

    def test_selection_references_transcript(self):
        self.assertIn(0, media.validate_selection(self.selection, self.transcript, 10, "hash"))

    def test_wrong_media_rejected(self):
        with self.assertRaises(ValueError):
            media.validate_selection(self.selection, self.transcript, 10, "other")

    def test_bad_timestamps_rejected(self):
        for timestamp in (-1, 10, float("nan"), float("inf")):
            with self.subTest(timestamp=timestamp), self.assertRaises(ValueError):
                media.validate_selection([{**self.selection[0], "timestamp": timestamp}], self.transcript, 10, "hash")

    def test_missing_segment_rejected(self):
        with self.assertRaises(ValueError):
            media.validate_selection([{**self.selection[0], "segment_id": 99}], self.transcript, 10, "hash")

    def test_reason_required(self):
        with self.assertRaises(ValueError):
            media.validate_selection([{**self.selection[0], "reason": ""}], self.transcript, 10, "hash")

    def test_no_sampling_without_analysis(self):
        for selection in ([], self.selection * 9):
            with self.assertRaises(ValueError):
                media.validate_selection(selection, self.transcript, 10, "hash")

    def test_output_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileExistsError):
                media.new_directory(temp)

    def test_timestamp_carry(self):
        self.assertEqual(media.stamp(59.9999), "00:01:00.000")
        self.assertEqual(media.stamp(3661.2), "01:01:01.200")


if __name__ == "__main__":
    unittest.main()
