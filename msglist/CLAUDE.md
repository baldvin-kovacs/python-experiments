# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python experiment for generating deterministic pseudo-random messages using a seeded random number generator. The project consists of two main files:

- `msgs.py`: Contains the `Msgs` class that implements a message generator
- `msgs_try.py`: Test script demonstrating the message generator functionality

## Architecture

The `Msgs` class implements a custom sequence-like interface:
- `__getitem__(key)`: Generates a pseudo-random message for index `key` using a seeded random generator
- `__len__()`: Returns fixed length of 70 messages
- Each message consists of 1-8 random words (Gaussian distribution, mean=5, std=3)
- Word lengths range from 3-10 characters using lowercase ASCII letters
- Messages are deterministic - same index always produces same message due to seeding

## Running the Code

Execute the test script:
```bash
python3 msgs_try.py
```

This will print the total number of messages (70) followed by all generated messages.

## Development Notes

- No external dependencies beyond Python standard library
- Uses `random.Random()` with index-based seeding for reproducible output
- Implements iterator protocol allowing `for` loops over the `Msgs` instance