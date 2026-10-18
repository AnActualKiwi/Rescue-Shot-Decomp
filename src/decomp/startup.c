/*
 * First decompilation slice for Rescue Shot Bubibo (Japan), SLPS_025.55.
 *
 * SOURCE: User-supplied local BIN/CUE, boot file at LBA 154741, extracted
 * as 444416 bytes of Mode 2 Form 1 user data. Input image SHA-256:
 *   BIN 65979175ccab07f729c591882c28e07037140812e96de30252a7c43eba90cbf0
 *   CUE c444b58144f117bdcd16534e71148f8fa8821210844e918c5f3a6b271fb8e7f4
 * EXTRACT SHA-256: a1004943a0653adfbd0fd72acb9b49d21253d434d31f4c4a41d46987e8cad2a7
 * TOOL: Ghidra 12.1.4 + PSX Executables Loader, PSX:LE:32:default.
 * EVIDENCE: build/ghidra-entry-analysis-final.log (local, ignored).
 *
 * This file is transcription of Ghidra evidence, not a matching or buildable
 * reconstruction. FUN_* names/types and DATA_* globals are not yet resolved.
 * PsyQ symbols recognized by Ghidra are retained as-is. Validate all control
 * flow, delay slots, ABI details, and structures against instruction bytes.
 */

/* Entry point 0x000165dc; 0x00010000..0x0007bfff is the initialized code block. */
/*
 * Observed MIPS listing:
 *
 * 000165dc  lui    v0,0x3
 * 000165e0  addiu  v0,v0,0x2cc4
 * 000165e4  lui    v1,0x3
 * 000165e8  addiu  v1,v1,0x6cec
 * 000165ec  addiu  v0,v0,0x4
 * 000165f0  bne    v0,v1,0x000165ec
 * 000165f4  sw     zero,0x0(v0)      // branch delay slot
 * 000165f8  lui    sp,0x3
 * 000165fc  lw     sp,0x1e88(sp)     // load from 0x00031e88
 * 00016600  lui    gp,0x3
 * 00016604  addiu  gp,gp,0x1d88      // GP becomes 0x00031d88
 * 00016608  addiu  sp,sp,-0x10
 * 0001660c  j      0x000121c4
 * 00016610  move   s8,sp             // jump delay slot
 */

/* Ghidra decompilation at 0x000121c4; retain unresolved names and globals. */
/*
void FUN_000121c4(void)
{
  FUN_00016614();
  FUN_0001a68c(0);
  ResetCallback();
  SetDispMask(0);
  ResetGraph(0);
  ClearImage((RECT *)0x108,'\0','\0','\0');
  FUN_000138f0();
  FUN_00016808();
  InitGeom();
  FUN_000157d4();
  FUN_0001e9cc();
  FUN_000122ec();
  SetDispMask(1);
  FUN_0001672c();
  FUN_00016ba4(0x180,0xf0);
  do {
    DAT_00000f40 = DAT_00000f40 ^ 1;
    DAT_00001398 = (DRAWENV *)(DAT_00000f40 * 0x80);
    DAT_00001394 = *(u_long **)&DAT_00001398[1].tpage;
    ClearOTagR(DAT_00001394,0x89);
    FUN_00013514();
    FUN_0001661c();
    FUN_00015f2c();
    DrawSync(0);
    VSync((uint)DAT_000332ba);
    PutDispEnv((DISPENV *)(DAT_00001398 + 1));
    DrawOTagEnv(DAT_00001394 + 0x88,DAT_00001398);
    DAT_00001390 = DAT_00001390 + '\x01';
    FUN_00016828();
  } while(true);
}
*/

/*
 * The branch delay-slot store runs on each branch iteration, including the
 * final not-taken branch; the observed cleared word range is 0x32cc8..0x36cec
 * inclusive. This interpretation follows the listing, not an emulator trace.
 *
 * Questions intentionally left open:
 * - Is 0x108 a true RECT pointer or a bad inferred type? Inspect memory/data refs.
 * - What source routines do FUN_00016614 and the other startup callees represent?
 * - Confirm display/environment sizes and the inferred double-buffer semantics.
 * - Validate exception/syscall and hardware behavior in a suitable PS1 runtime.
 */
