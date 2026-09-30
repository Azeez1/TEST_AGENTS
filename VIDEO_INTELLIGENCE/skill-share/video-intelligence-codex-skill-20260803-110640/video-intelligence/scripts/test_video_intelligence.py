#!/usr/bin/env python
"""Offline regression tests for the video-intelligence skill."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from generate_test_fixtures import generate
from video_intelligence import SCHEMA_VERSION
from video_intelligence.captions import parse_json3_captions
from video_intelligence.cache import load_cache, make_cache_key, save_cache
from video_intelligence.costs import estimate_cost, resolve_model
from video_intelligence.media import detect_rapid_change_segments, extract_clip, resolve_source
from video_intelligence.profiles import available_profiles, build_prompt
from video_intelligence.render import render_markdown, timestamp
from video_intelligence.schema import validate_analysis
from video_intelligence.security import redact
from video_intelligence.timeline import repair_timestamps


def valid_analysis() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "profile": "general",
        "source": {"label": "fixture.mp4", "kind": "local_file"},
        "summary": "A deterministic color and tone fixture.",
        "chapters": [{"id": "chapter-1", "start_seconds": 0, "end_seconds": 6, "title": "Fixture", "summary": "Three phases."}],
        "events": [{"id": "event-1", "start_seconds": 0, "end_seconds": 2, "event_type": "visual", "description": "Red phase.", "evidence_type": "visual", "confidence": 1.0}],
        "transcript_segments": [],
        "on_screen_text": [{"id": "text-1", "start_seconds": 0, "end_seconds": 2, "text": "RED PHASE", "location": "center", "confidence": 1.0}],
        "entities": [],
        "claims": [],
        "profile_analysis": [{"title": "Sequence", "finding": "Three phases.", "evidence_ids": ["event-1"], "score": -1, "confidence": 1.0}],
        "quality": {"overall_confidence": 1.0, "limitations": [], "requires_high_detail_pass": False, "high_detail_segments": []},
        "high_detail_findings": [],
        "open_questions": [],
    }


class ContractTests(unittest.TestCase):
    def test_valid_contract(self):
        self.assertEqual(validate_analysis(valid_analysis()), [])

    def test_rejects_invalid_time_and_confidence(self):
        data = valid_analysis()
        data["events"][0]["end_seconds"] = -1
        data["events"][0]["confidence"] = 1.2
        errors = validate_analysis(data)
        self.assertTrue(any("end_seconds" in item for item in errors))
        self.assertTrue(any("confidence" in item for item in errors))

    def test_rejects_too_many_escalations(self):
        data = valid_analysis()
        data["quality"]["high_detail_segments"] = [
            {"start_seconds": index, "end_seconds": index + 1, "reason": "test"}
            for index in range(6)
        ]
        self.assertTrue(any("at most 5" in item for item in validate_analysis(data)))

    def test_rejects_timestamps_beyond_source_duration(self):
        data = valid_analysis()
        data["chapters"][0]["end_seconds"] = 12
        self.assertTrue(any("exceeds source duration" in item for item in validate_analysis(data, 6.0)))


class UtilityTests(unittest.TestCase):
    def test_json3_caption_timeline(self):
        payload = {
            "events": [
                {"tStartMs": 1000, "dDurationMs": 2000, "segs": [{"utf8": "hello "}, {"utf8": "world"}]},
                {"tStartMs": 4000, "dDurationMs": 1000, "segs": [{"utf8": "next point"}]},
            ]
        }
        timeline = parse_json3_captions(payload)
        self.assertIn("[00:01-00:05]", timeline)
        self.assertIn("hello world", timeline)

    def test_caption_timeline_repairs_stretched_clock(self):
        data = valid_analysis()
        data["chapters"] = [
            {"id": "c1", "start_seconds": 0, "end_seconds": 50, "title": "Introduction", "summary": "Intro"},
            {"id": "c2", "start_seconds": 50, "end_seconds": 233, "title": "Chunking", "summary": "Break tasks down"},
            {"id": "c3", "start_seconds": 233, "end_seconds": 751, "title": "Confidence", "summary": "Small wins"},
        ]
        timeline = "[00:00-00:08] introduction\n[00:48-00:59] chunking break tasks down\n[02:25-02:34] confidence small wins"
        stats = repair_timestamps(data, timeline, 180.0)
        self.assertEqual(data["chapters"][1]["start_seconds"], 48.0)
        self.assertEqual(data["chapters"][2]["start_seconds"], 145.0)
        self.assertEqual(data["chapters"][-1]["end_seconds"], 180.0)
        self.assertGreater(stats["aligned"], 0)
        self.assertEqual(validate_analysis(data, 180.0), [])

    def test_model_and_cost_routing(self):
        self.assertEqual(resolve_model("auto"), "gemini-3.5-flash")
        estimate = estimate_cost("gemini-3.5-flash", 60, 1000)
        self.assertGreater(estimate.estimated_total_usd or 0, 0)
        self.assertLess(estimate.estimated_total_usd or 1, 0.05)

    def test_prompt_is_content_agnostic_and_evidence_aware(self):
        self.assertIn("software-qa", available_profiles())
        prompt = build_prompt(
            profile="tutorial-sop",
            question="Extract steps",
            source_label="x.mp4",
            duration_seconds=6.0,
            caption_timeline="[00:02-00:03] grounded words",
        )
        self.assertIn("visual frames and audio", prompt)
        self.assertIn("Extract steps", prompt)
        self.assertIn("hard boundary", prompt)
        self.assertIn("AUTHORITATIVE CAPTION TIMELINE", prompt)

    def test_redaction(self):
        secret = "AIza" + "A" * 32
        self.assertNotIn(secret, redact(f"api_key={secret}"))
        self.assertIn("[REDACTED]", redact(f"api_key={secret}"))

    def test_cache_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            key = make_cache_key({"source": "abc", "profile": "general"})
            save_cache(key, {"analysis": valid_analysis()}, root)
            self.assertEqual(load_cache(key, root)["analysis"]["summary"], valid_analysis()["summary"])

    def test_render(self):
        report = render_markdown(valid_analysis(), {"model": "gemini-3.5-flash", "cost_usd": 0.01})
        self.assertIn("00:00–00:02", report)
        self.assertIn("Timestamped evidence", report)
        self.assertEqual(timestamp(3661), "01:01:01")


class MediaTests(unittest.TestCase):
    def test_fixture_probe_and_clip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = generate(root)
            source = resolve_source(str(fixture["video"]))
            self.assertAlmostEqual(source.duration_seconds, 6.0, delta=0.2)
            self.assertEqual((source.width, source.height), (640, 360))
            rapid = detect_rapid_change_segments(source)
            self.assertTrue(any(item["start_seconds"] <= 3.0 <= item["end_seconds"] for item in rapid))
            clip = extract_clip(source, 2.8, 3.5, root / "clip.mp4")
            clipped = resolve_source(str(clip))
            self.assertAlmostEqual(clipped.duration_seconds, 0.7, delta=0.2)
            slowed = extract_clip(source, 2.8, 3.5, root / "slow.mp4", slow_factor=8)
            slowed_source = resolve_source(str(slowed))
            self.assertAlmostEqual(slowed_source.duration_seconds, 5.6, delta=0.4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
