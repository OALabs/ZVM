# ZVM
Disassembler for Zeus VM custom instruction set.

## What
This is just a demo to learn more about reverse engineering virtual machines. Our goal is to build a disassembler for the custom Zeus VM instruction set and disassemble the VM code to reveal the custom algorithm used to protect their configuration file.

The Zeus VM uses a custom set of XOR keys in the instruction set that is updated with each build. Because of this our disassembler will only work with a single version of the malware `f792997cb36a477fa55102ad6b680c97e3517b2e63c83c802bf8d57ae9ed525e` [[Download](https://www.unpac.me/results/bb557f46-a12a-4737-a638-787f982963fd?hash=f792997cb36a477fa55102ad6b680c97e3517b2e63c83c802bf8d57ae9ed525e#/)].

## Documentation
The full analysis and development process is being streamed on [Twitch](https://www.twitch.tv/oalabslive) and the VODs are available on the [OALABS Patreon](https://www.patreon.com/collection/320968?view=expanded). 

### Notes
Notes are also available here.

- [Introduction To VM Protection - VMZeus](https://research.openanalysis.net/vmzues/zeus/vm/obfuscation/tutorial/2024/01/07/into-to-vms.html)
- [VM Reverse Engineering Part 2 - Disassembly](https://research.openanalysis.net/vmzues/zeus/vm/obfuscation/tutorial/2024/01/21/vmzeus-disassembler.html)

