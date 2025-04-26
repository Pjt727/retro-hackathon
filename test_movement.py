from typing import Literal
import arcade
import random
import enum
import time
import math
from main import Block, Face

SCREEN_WIDTH = 870
SCREEN_HEIGHT = 680
BLOCK_COUNT = 10
SCREEN_TITLE = "Pong"
INITIAL_SPEED = 10
REL_TOL = 2
FRAMES_TO_WAIT = 60
PADDLE_SPEED = 12
MIN_SPEED = 8

is_rotate_mode = False
score = 0



class Tetris:
    def __init__(self) -> None:
        self.outlines: list[arcade.Rect] = []
        self.tiles: list[bool] = [False] * (BLOCK_COUNT * (BLOCK_COUNT // 2))
        # each square of a block is dim x dim
        dim = SCREEN_HEIGHT // BLOCK_COUNT
        start_left = (SCREEN_WIDTH - ((BLOCK_COUNT * dim) // 2)) // 2
        self.blocks: list[Block] = [Block(dim, start_left, self.tiles)]
        for i in range(BLOCK_COUNT):
            for j in range(BLOCK_COUNT // 2):
                left = start_left + (j * dim)
                bottom = i * dim
                self.outlines.append(
                    arcade.rect.LRBT(left, left + dim, bottom, bottom + dim)
                )

    def draw(self) -> None:
        for block in self.blocks:
            block.draw()
        for outline in self.outlines:
            arcade.draw_rect_outline(outline, arcade.color.RED_DEVIL, 2)
        for block in self.blocks:
            block.draw_win()




class Pong(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

        self.lives = 5
        self.up_pressed = False
        self.down_pressed = False
        self.w_pressed = False
        self.s_pressed = False
        self.tetris = Tetris()

    def on_draw(self):
        self.clear()
        self.tetris.draw()
        # arcade.draw_text(
        #         f"Score: {score}", 20, SCREEN_HEIGHT - 20, arcade.color.WHITE, 20
        # )
        # arcade.draw_text(
        #     f"Lives: {self.lives}",
        #     SCREEN_WIDTH - 100,
        #     SCREEN_HEIGHT - 30,
        #     arcade.color.WHITE,
        #     20,
        # )

    def update(self, delta_time):

        # block hits
        for block in self.tetris.blocks:
            for _ in block.get_rects(block.indexes):
                block.hit(Face.RIGHT, 1)
                time.sleep(.2)
                break

    def on_key_press(self, key, modifiers):  # pyright: ignore
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        if key == arcade.key.W:
            self.w_pressed = True
        elif key == arcade.key.S:
            self.s_pressed = True

    def on_key_release(self, key, modifiers):  # pyright: ignore
        # togle rotate or move
        if key == arcade.key.SPACE:
            global is_rotate_mode
            is_rotate_mode = not is_rotate_mode

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        if key == arcade.key.W:
            self.w_pressed = False
        elif key == arcade.key.S:
            self.s_pressed = False


if __name__ == "__main__":
    app = Pong(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.schedule(app.update, 1 / 60)
    arcade.run()
