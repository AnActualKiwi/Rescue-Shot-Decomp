# Frame-update slice: trigger/state handling

## Scope and evidence

This pass follows the frame loop in `FUN_000121c4` at `0x000121c4`, which calls `FUN_00013514` before the later pad polling at `FUN_00016828`. The slice focuses on `FUN_00013514` (`0x00013514`-`0x00013577`) and its helper `FUN_000134fc` (`0x000134fc`-`0x00013513`). It is narrow on purpose: the state variables and helper effects are still unnamed.

Input: local, user-supplied Japanese *Rescue Shot Bubibo* BIN/CUE. Boot file `SLPS_025.55` is at LBA `154741`, raw offset `363950832`; extracted logical-data SHA-256 `a1004943a0653adfbd0fd72acb9b49d21253d434d31f4c4a41d46987e8cad2a7`. Original image hashes were unchanged after the analysis: BIN `65979175ccab07f729c591882c28e07037140812e96de30252a7c43eba90cbf0`, CUE `c444b58144f117bdcd16534e71148f8fa8821210844e918c5f3a6b271fb8e7f4`.

Ghidra 12.1.4, PSX Executables Loader, language `PSX:LE:32:default`. The isolated project and full inspection transcript are local-only under ignored `build/`; the transcript is `build/ghidra-frame-slice-final.log`. No extracted executable or log is included in this repository.

## Helper at `0x000134FC`

Ghidra reports:

```c
void FUN_000134fc(undefined4 param_1)
{
  DAT_00031e20 = param_1;
  DAT_00031da0 = param_1;
  return;
}
```

The instructions write the argument to two global addresses. This suggests mirrored/shared state, but the values' use sites and semantics have not yet been traced.

## Frame update at `0x00013514`

Ghidra reports:

```c
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
```

Relevant disassembly (MIPS R3000A; delay slots shown explicitly):

```asm
00013514  lb    v0,0x1533(gp)
00013518  addiu sp,sp,-0x18
0001351c  blez  v0,0x00013540
00013520  sw    ra,0x10(sp)          # branch delay slot
00013524  lui   a0,0xff9f
00013528  sb    zero,0x1533(gp)
0001352c  jal   0x000134fc
00013530  ori   a0,a0,0x6601          # delay slot: a0 = 0xff9f6601
00013534  lhu   v0,0x13d2(gp)
00013538  j     0x00013564
0001353c  ori   v0,v0,1               # delay slot
00013540  bne   v0,zero,0x00013568
00013544  li    v0,-1                 # delay slot
00013548  lw    a0,0x152c(gp)
0001354c  sb    v0,0x1533(gp)
00013550  jal   0x000134fc
00013554  nop
00013558  lhu   v0,0x13d2(gp)
0001355c  nop
00013560  andi  v0,v0,0xfffe
00013564  sh    v0,0x13d2(gp)
00013568  lw    ra,0x10(sp)
0001356c  nop
00013570  jr    ra
00013574  addiu sp,sp,0x18            # delay slot
```

When the signed byte state at `0x1533` is positive, this routine clears it, calls the helper with constant `0xff9f6601`, and sets bit 0 in the halfword at `0x13d2`. When that signed state is exactly zero, it writes `-1`, calls the helper with the current word at `0x152c`, and clears bit 0 at `0x13d2`. Negative state falls through without either update. These are instruction-level effects only; the meaning of the state, flag, and helper-managed words is unknown.

A word in MIPS `lui`/`ori` order `0xFF9F6601` can resemble a hardware command, but that resemblance alone is insufficient to name this as a GPU command or prove it starts/stops any feature. No code/data references or runtime observation yet establish those semantics. Treat it only as the observed constant passed into the state helper.

## Place in the frame loop

`FUN_000121c4` calls `FUN_00013514` once per iteration, then calls `FUN_0001661c` and `FUN_00015f2c`, synchronizes drawing, waits for vertical sync, submits the draw environment/order table, increments a counter, and calls `FUN_00016828`. The loop is not fully reconstructed. `FUN_00016828` is identified by Ghidra as interacting with PsyQ pad APIs, but its decompilation contains overlapping-instruction and unresolved-jump-table warnings; it is deliberately not used here to claim a complete input/gameplay model.

## Confidence and next work

- **Verified from static evidence:** function extents, instruction addresses/opcodes as rendered by the installed Ghidra MIPS decoder, writes and calls described above, and call position in the main-loop decompilation.
- **Inferred:** `FUN_00013514` is per-frame state/flag handling, based on the known caller loop; `0xff9f6601` may encode a hardware-facing operation. Both are hypotheses.
- **Unknown:** meaning of `DAT_00001533`, `DAT_0000152c`, `DAT_000013d2`, the helper's two target words, ordering/runtimes effects, and whether Ghidra's data typing around these globals is correct.
- **Not established:** compiler/linker, source correspondence, exact matching, or behavior observed on a PlayStation/emulator.

Next: trace references to the state/flag fields, inspect `0xff9f6601`'s source and use sites, and validate branch/delay-slot behavior in a read-only runtime session before assigning game-facing names.