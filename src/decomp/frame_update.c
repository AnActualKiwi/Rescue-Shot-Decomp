/*
 * Rescue Shot Bubibo (Japan), SLPS_025.55 — frame-update slice.
 *
 * Evidence: Ghidra 12.1.4 / PSX Executables Loader / PSX:LE:32:default.
 * Local headless transcript: build/ghidra-frame-slice-final.log (ignored).
 * Source BIN/CUE hashes:
 *   65979175ccab07f729c591882c28e07037140812e96de30252a7c43eba90cbf0
 *   c444b58144f117bdcd16534e71148f8fa8821210844e918c5f3a6b271fb8e7f4
 * Extracted boot-file SHA-256:
 *   a1004943a0653adfbd0fd72acb9b49d21253d434d31f4c4a41d46987e8cad2a7
 *
 * Static Ghidra transcription only. This is not buildable game source,
 * not a matching reconstruction, and not behavior verified in a runtime.
 * Keep machine-generated globals and function identifiers until references,
 * layout, ABI details, delay slots, and runtime effects are corroborated.
 */

/* Ghidra function at 0x000134fc. Two global stores are observed; semantics
 * of either destination are unresolved. */
/*
void FUN_000134fc(undefined4 param_1)
{
  DAT_00031e20 = param_1;
  DAT_00031da0 = param_1;
  return;
}
*/

/* Ghidra function at 0x00013514. Called in the main frame loop before the
 * pad polling function. The value 0xff9f6601 is transcribed, not interpreted. */
/*
void FUN_00013514(void)
{
  if (DAT_00001533 < '\x01') {
    if (DAT_00001533 == '\0') {
      DAT_00001533 = -1;
      FUN_000134fc(DAT_0000152c);
      DAT_000013d2 = DAT_000013d2 & 0xfffe;
    }
  }
  else {
    DAT_00001533 = '\0';
    FUN_000134fc(0xff9f6601);
    DAT_000013d2 = DAT_000013d2 | 1;
  }
  return;
}
*/

/* Evidence-backed behavior at this level:
 * - positive signed DAT_00001533: clear it; helper receives 0xff9f6601; set
 *   bit 0 of DAT_000013d2.
 * - zero DAT_00001533: set it to -1; helper receives DAT_0000152c; clear
 *   bit 0 of DAT_000013d2.
 * - negative DAT_00001533: neither branch updates these values.
 *
 * Unknowns: purpose of the state/flag and the helper's targets. Hardware
 * interpretation of 0xff9f6601 is a hypothesis only. No runtime observation.
 */
