import argparse
import pygame
import pygame.image
import pygame.surfarray
import random
from typing import Callable

FRAMERATE = 12.5
DEFAULT_TRANSITION_DURATION = 4.0


class Transition:

    def __init__(self, width: int, height: int, swap_pixel: Callable):
        self.width = width
        self.height = height
        self.swap_pixel = swap_pixel

    def reset(self):
        raise NotImplementedError

    def update(self, delta_ms: int) -> bool:
        raise NotImplementedError


class DissolveTransition(Transition):

    def __init__(self, duration_ms: int, width: int, height: int, swap_pixel: Callable):
        super().__init__(width, height, swap_pixel)

        self.duration_ms = duration_ms
        self.elapsed_ms = 0

        self.pixels_total = width * height
        self.pixels_swapped = 0

        # Source: https://patents.google.com/patent/US5771033A/en
        # Step A: selecting a prime number p;
        # 3. The method of claim 1 wherein p=2^e+1 with e being
        #    a positive integer and m=2^c–1 with c being a positive
        #    integer.
        # 4. The method of claim 3 wherein e=16 and c=15.
        self.p = (2 ** 16) + 1
        self.m = (2 ** 15) - 1

        # Step B: selecting a number k=k0, where k0 is a number between 1 and p-1;
        k0 = random.randint(1, self.p - 1)
        self.k = k0

    def reset(self):
        self.elapsed_ms = 0
        self.pixels_swapped = 0

    def update(self, delta_ms: int) -> bool:
        # Check if already finished
        if self.pixels_swapped >= self.pixels_total:
            return False

        # Calculate elapsed time
        self.elapsed_ms += delta_ms
        if self.elapsed_ms >= self.duration_ms:
            self.elapsed_ms = self.duration_ms

        # Calculate number of pixels to swap in this frame
        pixels_to_swap = int((self.pixels_total * self.elapsed_ms) / self.duration_ms) - self.pixels_swapped

        self.pixels_swapped += pixels_to_swap

        while pixels_to_swap > 0:

            # Step C: calculating a pixel number j in the current image according to the formula j=(w*h)+k-p;
            j = self.pixels_total + self.k - self.p

            # Step D: determining if J is non-negative
            while j > 0:
                # Step E: replacing the pixel corresponding to pixel number j in the first image with the corresponding
                # pixel in the second image
                self.swap_pixel(j % self.width, j // self.width)

                pixels_to_swap -= 1

                # Step F: Calculating a number jnew, according to the formula jnew = j-(p-1), and setting j=jnew
                j = j - (self.p - 1)

            # Step H: calculating a number knew according to the formula knew = (k*m) mod p, wherein m is a primitive
            # root of unity modulo p, and setting k=knew
            knew = (self.k * self.m) % self.p
            self.k = knew

        # TODO: Update the colour palette, as described in the patent:
        # The current palette is gradually changed to the source palette by linearly interpolating each palette entry
        # between the color value in the current palette and the color value in the source palette.

        return True


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="3D Movie Maker dissolve demo")
    parser.add_argument("source", nargs="?", default="source.png", help="Image to transition from")
    parser.add_argument("destination", nargs="?", default="dest.png", help="Image to transition to")
    parser.add_argument("--duration", type=float, default=DEFAULT_TRANSITION_DURATION, help="Transition duration")

    args = parser.parse_args()

    pygame.init()

    # Load images
    source_image = pygame.image.load(args.source)
    dest_image = pygame.image.load(args.destination)

    source_image_size = source_image.get_size()
    window_width, window_height = source_image_size

    if source_image_size != dest_image.get_size():
        raise Exception("Images must be the same size")

    source_pixels = pygame.surfarray.array3d(source_image)
    dest_pixels = pygame.surfarray.array3d(dest_image)

    # Make a copy of the source image as our starting point
    current_state = source_pixels.copy()

    # Callback for swapping a pixel
    def swap_pixel(x, y):
        current_state[x, y] = dest_pixels[x, y]

    duration_ms = int(args.duration * 1000)
    transition = DissolveTransition(duration_ms, window_width, window_height, swap_pixel)

    # Create display window
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("3D Movie Maker dissolve - press SPACE to start/stop, ESC to restart")

    clock = pygame.time.Clock()

    exit_requested = False
    running = False
    while not exit_requested:

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_requested = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    running = not running
                elif event.key == pygame.K_ESCAPE:
                    # Reset
                    current_state = source_pixels.copy()
                    transition.reset()

        frame_delta = clock.tick(FRAMERATE)

        # Update transition
        if running:
            running = transition.update(frame_delta)

        # Render
        pygame.surfarray.blit_array(screen, current_state)
        pygame.display.flip()


if __name__ == '__main__':
    main()
