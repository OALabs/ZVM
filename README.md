# ZVM
Disassembler for Zeus VM custom instruction set with a [Binary Ninja](https://binary.ninja/) plugin.

## What
This is just a demo to learn more about reverse engineering virtual machines and Binary Ninja architecture plugin development. Our goal is to build a disassembler for the custom Zeus VM instruction set and disassemble the VM code then lift it in Binary Ninja to reveal the custom algorithm used to protect their configuration file.

The Zeus VM uses a custom set of XOR keys in the instruction set that is updated with each build. Because of this our disassembler will only work with a single version of the malware `f792997cb36a477fa55102ad6b680c97e3517b2e63c83c802bf8d57ae9ed525e` [[Download](https://www.unpac.me/results/bb557f46-a12a-4737-a638-787f982963fd?hash=f792997cb36a477fa55102ad6b680c97e3517b2e63c83c802bf8d57ae9ed525e#/)].

## Development Notes
The full analysis and development process is being streamed on [Twitch](https://www.twitch.tv/oalabslive) and the VODs are available on the [OALABS Patreon](https://www.patreon.com/collection/320968?view=expanded). 

Notes from our streams are also available here.

- [Introduction To VM Protection - VMZeus](https://research.openanalysis.net/vmzues/zeus/vm/obfuscation/tutorial/2024/01/07/into-to-vms.html)
- [VM Reverse Engineering Part 2 - Disassembly](https://research.openanalysis.net/vmzues/zeus/vm/obfuscation/tutorial/2024/01/21/vmzeus-disassembler.html)

## Documentation
For the Binary Ninja Plugin we loosely followed the binja Architecture Plugin guides and had a lot of help from @xusheng6.

- [A Guide to Architecture Plugins (Part 1)](https://binary.ninja/2020/01/08/guide-to-architecture-plugins-part1.html)
- [A Guide To Architecture Plugins (Part 2)](https://binary.ninja/2021/12/09/guide-to-architecture-plugins-part2.html)

### Reference 
The following references were also helpful.

- [LEVERAGING BINARY NINJA IL TO REVERSE A CUSTOM ISA: CRACKING THE “POT OF GOLD” 37C3](https://www.synacktiv.com/en/publications/leveraging-binary-ninja-il-to-reverse-a-custom-isa-cracking-the-pot-of-gold-37c3)
- [Untangling Exotic Architectures with Binary Ninja Supplementing Flare-On 2017 with some sanity](https://blog.ret2.io/2017/10/17/untangling-exotic-architectures-with-binary-ninja/)
- [Lifting VM based obfuscators in Binary Ninja](https://www.lodsb.com/lifting-vm-based-obfuscators-in-binary-ninja)
- [Breaking Down Binary Ninja’s Low Level IL](https://blog.trailofbits.com/2017/01/31/breaking-down-binary-ninjas-low-level-il/)

### Intrinsics
For our architecture we had two unique instructions, `rc4` and `shuffle` both of which don't have a good representation in the binja IL. To represent these we used [intrinsics](https://api.binary.ninja/binaryninja.architecture-module.html#binaryninja.architecture.IntrinsicInfo)

```python
from binaryninja.architecture import IntrinsicInfo
from binaryninja.types import Type

intrinsics = {'rc4': IntrinsicInfo(inputs=[], outputs=[], index=1),
              'shuffle': IntrinsicInfo(inputs=[Type.int(4, False), Type.int(1, False)], outputs=[], index=2)
```

### Loops
Loops are also interesting as they require an expression that branches. The code is straight forward but one thing to keep in mind is that each expression in the IL has a label an labels are used for branching (instead of addresses).

```python
il.append(il.set_reg(4,
                     'loop_counter',
                     il.sub(4, il.reg(4, 'loop_counter'), il.const(4, 1))))
condition = il.compare_not_equal(4, il.reg(4, 'loop_counter'), il.const(4, 0))
t = il.get_label_for_address(Architecture['ZVM'], addr + instr.size - op2.value)
f = il.get_label_for_address(Architecture['ZVM'], addr + instr.size)
# here we just think t and f are both valid, and take the easy route
il.append(il.if_expr(condition, t, f))
```


## No PRs
Because this project is meant to be a community effort on stream we won’t be accepting PRs. Aside from some maintenance/cleanup **all coding will be done on-stream**. If you have feature requests or suggestions leave your feedback as an Issue or come chat with us on [**Discord**](https://discord.gg/oalabs).

## Join Us!
 💖 Check out our [**schedule**](https://www.twitch.tv/oalabslive/schedule) we stream Sundays at 1300 EST

[![Chat](https://img.shields.io/badge/Chat-Discord-blueviolet)](https://discord.gg/oalabs) [![Support](https://img.shields.io/badge/Support-Patreon-FF424D)](https://www.patreon.com/oalabs)
