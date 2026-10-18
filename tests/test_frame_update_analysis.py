import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "decomp" / "frame_update.c"
REPORT = ROOT / "analysis" / "frame-update.md"


class FrameUpdateAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_slice_records_input_identity_and_non_matching_status(self):
        for token in (
            "SLPS_025.55",
            "Ghidra 12.1.4",
            "65979175ccab07f729c591882c28e07037140812e96de30252a7c43eba90cbf0",
            "c444b58144f117bdcd16534e71148f8fa8821210844e918c5f3a6b271fb8e7f4",
            "not a matching reconstruction",
            "buildable game source",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.source)

    def test_helper_and_frame_state_transitions_are_documented(self):
        for token in (
            "void FUN_000134fc(undefined4 param_1)",
            "DAT_00031e20 = param_1;",
            "DAT_00031da0 = param_1;",
            "void FUN_00013514(void)",
            "FUN_000134fc(0xff9f6601);",
            "FUN_000134fc(DAT_0000152c);",
            "DAT_000013d2 = DAT_000013d2 | 1;",
            "DAT_000013d2 = DAT_000013d2 & 0xfffe;",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.source)
                self.assertIn(token, self.report)

    def test_report_separates_static_facts_from_hypotheses(self):
        for token in (
            "Verified from static evidence",
            "Inferred",
            "Unknown",
            "Not established",
            "hypotheses",
            "runtime",
        ):
            with self.subTest(token=token):
                self.assertIn(token.lower(), self.report.lower())
        self.assertIn("not interpreted", self.source.lower())

    def test_transcribed_functions_match_local_ghidra_output_when_available(self):
        log_path = ROOT / "build" / "ghidra-frame-slice-final.log"
        if not log_path.exists():
            self.skipTest("Local Ghidra transcript is not available in this checkout")
        log = log_path.read_text(encoding="utf-8", errors="replace")
        for address, required in (
            ("000134fc", ("void FUN_000134fc(undefined4 param_1)", "DAT_00031e20 = param_1;", "DAT_00031da0 = param_1;")),
            ("00013514", ("void FUN_00013514(void)", "FUN_000134fc(0xff9f6601);", "FUN_000134fc(DAT_0000152c);")),
        ):
            with self.subTest(address=address):
                start = log.find(f"SLICE_C_CODE_BEGIN address={address}")
                end = log.find("SLICE_C_CODE_END", start)
                self.assertGreaterEqual(start, 0)
                self.assertGreater(end, start)
                decompiler_text = log[start:end]
                for token in required:
                    self.assertIn(token, decompiler_text)
                    self.assertIn(token, self.source)
                    self.assertIn(token, self.report)

    def test_report_preserves_delay_slot_and_unknown_semantics_caveats(self):
        for token in (
            "delay slots",
            "meaning of `DAT_00001533`",
            "semantics",
            "runtime observation",
        ):
            with self.subTest(token=token):
                self.assertIn(token.lower(), self.report.lower())


if __name__ == "__main__":
    unittest.main()
