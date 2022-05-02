# 3D Movie Maker Dissolve

This is a reimplementation of the dissolve transition effect from Microsoft 3D Movie Maker, based
on [Shon Katzenberger's patent](https://patents.google.com/patent/US5771033A/en) and reverse engineering of the program.

**NOTE:** This implementation is not complete. The patent also describes how the colour palette is faded during the transition. I haven't implemented that yet.

https://user-images.githubusercontent.com/1490287/166219273-c390e3c6-fae7-48b1-b3f8-729ef9fb233f.mp4

## Requirements

* Python 3.6+
* Pygame
* Numpy

## Usage

Run `dissolve.py` to transition between two test images.

* Press SPACE to start/pause the transition
* Press ESC to reset the transition

## Reverse Engineering

All function addresses below are from the World English (UK) release of 3D Movie Maker.

When you play a movie, a function in the MVIE class (0x4a2310) is called whenever 3DMM needs to transition to a new scene. This calls different functions depending on the type of transition selected in the Scene Organizer.

The APPB class has a function (0x41d100) which is used to render other transitions in the app (eg. moving to a different room of the Theatre). This function supports a few extra transitions that aren't used in 3DMM.

Each transition type is implemented as a method on the GNV class:

* 0x421040 - Dissolve
* 0x421840 - Cut
* 0x4209e0 - Wipe (not used)
* 0x420c90 - Slide (not used)
* 0x421a40 - Slide from corner (not used)

If you want to try out the unused transitions:

* Attach WinDbg to 3DMOVIE.EXE
* Set this breakpoint: `bp 41d0b4 "r eax=2; g"`
  * Change the value for EAX to 1 = wipe, 2 = slide, 5 = slide from corner
* Open the Map and click any room
