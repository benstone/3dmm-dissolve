import pygame
import pygame.image
import pygame.surfarray
import random
from typing import Callable

FRAMERATE = 12.5

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480


class Transition:

    def __init__(self, width: int, height: int, swap_pixel: Callable):
        self.width = width
        self.height = height
        self.swap_pixel = swap_pixel

    def reset(self):
        raise NotImplementedError

    def update(self, time_delta_ms: int) -> bool:
        raise NotImplementedError


class DissolveTransition(Transition):

    def __init__(self, duration_ms: int, width: int, height: int, swap_pixel: Callable):
        super().__init__(width, height, swap_pixel)

        self.duration_ms = duration_ms
        self.elapsed_ms = 0

        self.pixels_total = width * height
        self.pixels_swapped = 0

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
            self.k = (self.k * self.m) % self.p

        # TODO: Update the colour palette, as described in the patent:
        # The current palette is gradually changed to the source palette by linearly interpolating each palette entry
        # between the color value in the current palette and the color value in the source palette.

        return True


def main():
    pygame.init()

    # Load images
    source_image = pygame.image.load("source.png")
    source_pixels = pygame.surfarray.array3d(source_image)

    dest_image = pygame.image.load("dest.png")
    dest_pixels = pygame.surfarray.array3d(dest_image)

    # Make a copy of the source image as our starting point
    current_state = source_pixels.copy()

    # Callback for swapping a pixel
    def swap_pixel(x, y):
        current_state[x, y] = dest_pixels[x, y]

    # Dissolves in 3DMM are four seconds long
    duration_ms = 4000
    transition = DissolveTransition(duration_ms, WINDOW_WIDTH, WINDOW_HEIGHT, swap_pixel)

    # Create display window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
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
