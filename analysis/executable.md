# Rescue Shot executable analysis - first slice

## Scope and inputs

- Title/revision: *Rescue Shot Bubibo* (Japan), boot executable `SLPS_025.55`.
- Local source image pair is user-supplied and remains outside Git. The BIN SHA-256 is `65979175ccab07f729c591882c28e07037140812e96de30252a7c43eba90cbf0`; the CUE SHA-256 is `c444b58144f117bdcd16534e71148f8fa8821210844e918c5f3a6b271fb8e7f4`.
- Disc inventory: `SLPS_025.55` begins at LBA `154741` (raw byte offset `363950832`), occupies 217 Mode 2 Form 1 sectors, and has 444,416 logical bytes. Its extracted logical-data SHA-256 is `a1004943a0653adfbd0fd72acb9b49d21253d434d31f4c4a41d46987e8cad2a7`.
- Boot configuration: `SYSTEM.CNF` names `cdrom:\SLPS_025.55;1`.
- Ghidra 12.1.4 with the installed PSX Executables Loader imported the extracted executable as language `PSX:LE:32:default`. The local project is `build/ghidra-projects/RescueShot`; local executable extraction and diagnostic scripts/logs are ignored under `build/`.

## Verified PS-X EXE facts

The executable header and loader agree on:

| Property | Value |
|---|---:|
| Load address / text start | `0x00010000` |
| Loaded text length | `0x0006C000` bytes (`0x10000`-`0x7BFFF`) |
| Entry point | `0x000165DC` |
| Ghidra entry function | `start`, `0x000165DC`-`0x00016613` |
| Stack pointer initialized by entry stub | value loaded from `0x00031E88` |
| `$gp` initialized by entry stub | `0x00031D88` |
| Main-loop function reached by entry jump | `FUN_000121c4` |

Ghidra's program contains initialized executable block `CODE` at `0x10000`-`0x7BFFF`, plus modeled but uninitialized RAM/device blocks. The loaded text agrees with the PS-X EXE header; this does not establish that every code/data reference or overlay is mapped correctly.

## Entry stub: `start` at `0x000165DC`

Observed instructions (MIPS R3000A, little-endian):

```asm
000165dc  lui    v0,0x3
000165e0  addiu  v0,v0,0x2cc4       # 0x00032CC4
000165e4  lui    v1,0x3
000165e8  addiu  v1,v1,0x6cec       # 0x00036CEC
000165ec  addiu  v0,v0,0x4
000165f0  bne    v0,v1,0x000165ec
000165f4  sw     zero,0x0(v0)       # branch delay slot
000165f8  lui    sp,0x3
000165fc  lw     sp,0x1e88(sp)      # load initial SP from 0x00031E88
00016600  lui    gp,0x3
00016604  addiu  gp,gp,0x1d88       # GP = 0x00031D88
00016608  addiu  sp,sp,-0x10
0001660c  j      0x000121c4
00016610  move   s8,sp              # jump delay slot
```

The loop clears 32-bit words beginning at `0x00032CC8` and ending at `0x00036CEC` inclusive (the branch delay-slot store executes on the final, not-taken branch), installs stack/global pointer state, then transfers control to `FUN_000121c4`. The loop interpretation follows the MIPS branch and delay-slot behavior; runtime memory effects have not yet been checked in an emulator.

## Main function: `FUN_000121c4`

Ghidra decompilation and direct call references show this startup sequence:

```c
void FUN_000121c4(void)
{
  FUN_00016614();
  FUN_0001a68c(0);
  ResetCallback();
  SetDispMask(0);
  ResetGraph(0);
  ClearImage((RECT *)0x108, '\0', '\0', '\0');
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
    ClearOTagR(DAT_00001394, 0x89);
    FUN_00013514();
    FUN_0001661c();
    FUN_00015f2c();
    DrawSync(0);
    VSync((uint)DAT_000332ba);
    PutDispEnv((DISPENV *)(DAT_00001398 + 1));
    DrawOTagEnv(DAT_00001394 + 0x88,DAT_00001398);
    DAT_00001390 = DAT_00001390 + '\x01';
    FUN_00016828();
  } while( true );
}
```

The call names for PsyQ API routines are based on imported Ghidra signatures and symbol recognition. The currently unresolved names, data types, and runtime effects are explicitly unknown; this slice is not byte-accurate and the matching compiler/linker configuration has not been established. The unnamed `FUN_*` functions and global variables remain unresolved. `ClearImage` receives address `0x108`, which may be a structure/reference artifact or a decompiler type interpretation; verify the address and object layout before assigning semantics. The `0x180 x 0xF0` call and alternating environment/order-table state suggest a double-buffered 384x240 rendering loop, but the display interpretation remains a hypothesis pending structure and runtime checks.

## Ghidra evidence and caveats

- The analysis uses the local Ghidra project and extracted input described above. The successful headless analysis log is `build/ghidra-entry-analysis-final.log` (ignored/local).
- Entry-point disassembly and the selected main function were obtained from Ghidra's listing and decompiler. The focused decompilation completed successfully.
- Earlier Ghidra startup produced warnings around uninitialized hardware/GTE address space (`0x20000000`); these are not evidence of malformed initialized game text, but they do mean peripheral/GTE semantics need separate validation.
- This is analysis of a boot executable only. XA-stream overlays `RS0.X`/`RS1.X` are not flat Form 1 files and remain undecoded. No compiler/matching build has been established, no executable bytes have been reconstructed, and the original-runtime behavior and matching compiler/linker configuration remain unknown; no runtime observation has been independently completed.

## Next evidence-backed work

1. Resolve the entry function's called functions and PsyQ APIs, starting with early initialization and the display/draw-environment structures.
2. Confirm the PS-X EXE header fields and relevant addresses against an independent parser/raw bytes.
3. Load the authorized local image in a debugger/emulator and verify the entry, RAM clear, stack/global pointer, and first rendered frame without modifying the source image.
4. Keep further source reconstruction in small address-scoped units, recording unresolved symbols and exact byte ranges; do not call the project byte-accurate until an actual candidate build is compared.
