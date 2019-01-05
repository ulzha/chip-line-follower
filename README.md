# chip-line-follower

An overengineered line follower robot, based on [C.H.I.P. SoC](https://en.wikipedia.org/wiki/CHIP_(computer)).

The code captures images of the road ahead and performs edge detection on them, so that (ideally) the color of the line would not affect the performance, nor would a textured background like a wooden table.

Hardware used:
- C.H.I.P.
- 3.7 V LiPo battery
- el cheapo USB webcam
- A4990 motor driver board ([Pololu 2137](https://www.pololu.com/product/2137))
- 2 gear motors ([Pololu 1512](https://www.pololu.com/product/1512))
- 5 AA batteries
- Lego wheels
- battery holder, wires, cardboard, duct tape
