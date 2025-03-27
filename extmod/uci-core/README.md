# SR150 UWB Host Interface Design

## Overview

This project implements a two-stage protocol interface to the NXP SR150 UWB transceiver:

- **HBCI (Host Bootloader Command Interface)**: Used for uploading RAM-resident firmware.
- **UCI (UWB Command Interface)**: Used after firmware upload to configure and operate the UWB subsystem.

## Design Summary

### SPIqueue (Base Layer)

- Abstracts SPI communication and protocol state transitions.
- Provides semaphores, ring buffer, and threading support for TX/RX packet flow.
- Designed as a **State Pattern Context**, with protocol-specific subclasses as states.

### HBCIqueue

- Implements the firmware upload state.
- Handles firmware chunk queuing, acknowledgment, retries.
- Intended as a transient state which hands off control to UCIqueue upon completion.

### UCIqueue

- Implements UCI protocol communication (e.g., commands, notifications).
- Can act as the main application entry point.
- In future versions, will internally manage HBCIqueue if firmware upload is needed.

### State Pattern Logic

```python
# Conceptually:
class SPIqueue: pass
class HBCIqueue(SPIqueue): pass
class UCIqueue(SPIqueue): pass

# On firmware upload completion:
self.__class__ = UCIqueue
self.__dict__ = UCIqueue(...).__dict__
```

## Key Design Decisions

- ✅ **State pattern** used to allow runtime protocol switching.
- ✅ `HBCIcommand` and `UCIcommand` are parametric; subclasses only override semantics.
- ✅ `accept_response()` is implemented per packet for fine-grained parsing.
- ✅ Retries and blocking semaphores are managed at the SPIqueue layer.
- ✅ No current need for separate response packet classes.
- ❌ Reverse transition UCI → HBCI is not supported (requires hardware reset).
- ❗Firmware flags (e.g. type/init bytes) are **not currently embedded in `.bin` files** and must be manually assigned.

## TODO / Future Enhancements

- [ ] Query chunk size from chip (if possible), else determine from HBCI spec.
- [ ] Add CRC-16 response validation on all received packets.
- [ ] Auto-handshake and firmware detection from UCIqueue entry point.
- [ ] Add support for async UCI notifications.
- [ ] Optional `UCIqueue.reset_to_hbci()` if firmware erase is implemented.

## Notes

- `CHUNKSIZE` is currently hardcoded.
- Firmware chunk responses must be treated specially: they do not mirror CLA/INS.
- UCIqueue and HBCIqueue may need references to each other only to support state transition.
