import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "decomp" / "startup.c"
REPORT = ROOT / "analysis" / "executable.md"


class ExecutableAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_source_slice_records_input_provenance_and_scope(self):
        self.assertIn("SLPS_025.55", self.source)
        self.assertIn("Ghidra 12.1.4", self.source)
        self.assertIn("65979175ccab07f729c591882c28e07037140812e96de30252a7c43eba90cbf0", self.source)
        self.assertIn("not a matching or buildable", self.source)

    def test_entry_addresses_and_global_register_setup_are_documented(self):
        expected = (
            "000165dc", "000165f0", "000165f4", "000165fc", "00016604",
            "0001660c", "0x00031e88", "0x00031d88", "0x000121c4",
        )
        for token in expected:
            with self.subTest(token=token):
                self.assertIn(token, self.source.lower())
                self.assertIn(token, self.report.lower())

    def test_main_decompilation_slice_matches_documented_evidence(self):
        fragments = (
            "void FUN_000121c4(void)",
            "ResetCallback();",
            "ClearImage((RECT *)0x108",
            "FUN_00016ba4(0x180",
            "DrawOTagEnv(DAT_00001394 + 0x88",
            "DAT_00001398);",
            "} while",
        )
        for fragment in fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.source)
                self.assertIn(fragment, self.report)

        self.assertIn("000165f4  sw     zero,0x0(v0)", self.report)
        self.assertIn("final, not-taken branch", self.report)
        self.assertIn("inclusive", self.source)
        self.assertIn("inclusive", self.report)

        # When the local Ghidra project/log are available, independently
        # compare the transcription; clean checkouts don't require private logs.
        ghidra_log = ROOT / "build" / "ghidra-entry-analysis-final.log"
        if ghidra_log.exists():
            self.assertTrue(self._ghidra_entry_instruction_present(ghidra_log))
            self.assertTrue(self._ghidra_main_fragments_present(ghidra_log, fragments))

    def _ghidra_entry_instruction_present(self, path):
        log = path.read_text(encoding="utf-8", errors="replace")
        start = log.find("ENTRY=000165dc")
        end = log.find("MAIN_C_CODE_BEGIN", start)
        self.assertGreaterEqual(start, 0)
        self.assertGreater(end, start)
        return "INSN=000165f4 _sw zero,0x0(v0)" in log[start:end]

    def _ghidra_main_fragments_present(self, path, fragments):
        log = path.read_text(encoding="utf-8", errors="replace")
        start = log.find("MAIN_C_CODE_BEGIN")
        end = log.find("MAIN_C_CODE_END", start)
        self.assertGreaterEqual(start, 0)
        self.assertGreater(end, start)
        evidence = log[start:end]
        return all(fragment in evidence for fragment in fragments)

    def test_committed_transcription_is_not_claimed_as_matching_source(self):
        self.assertIn("not a matching or buildable", self.source)
        self.assertIn("not byte-accurate", self.report)
        self.assertIn("matching compiler/linker configuration has not been established", self.report)

    def test_report_identifies_unresolved_hypotheses_and_no_match_claim(self):
        for token in (
            "hypothesis", "unknown", "not been established", "remain undecoded",
            "no executable bytes have been reconstructed", "runtime", "compiler/matching build",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.report.lower())


if __name__ == "__main__":
    unittest.main()
