import arcade
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 680
BLOCK_COUNT = 10
SCREEN_TITLE = "Pong"
MIN_SPEED_FOR_DOWN = 10

is_rotate_mode = False


class Block:
    def __init__(self, dim: int, start_left: int, tiles: list[bool]) -> None:
        self.dim = dim
        self.start_left = start_left
        self.tiles = tiles
        self.create_new()

    @staticmethod
    def pos_to_index(row: int, col: int) -> int:
        return row + (BLOCK_COUNT // 2) * col

    def create_new(self):
        # kind = random.randint(1, 7)
        kind = 1
        if kind == 1:
            start_row = random.randint(0, BLOCK_COUNT - 2)
            start_col = random.randint(0, BLOCK_COUNT // 2)
            self.indexes = [
                Block.pos_to_index(start_row, start_col),
                Block.pos_to_index(start_row + 1, start_col),
                Block.pos_to_index(start_row, start_col + 1),
                Block.pos_to_index(start_row + 1, start_col + 1),
            ]
            self.color = arcade.color.YELLOW
        elif kind == 2:
            pass
        if all(map(self.index_is_valid, self.indexes)):
            self.place_shape()
        else:
            self.create_new()

    def place_shape(self):
        for index in self.indexes:
            self.tiles[index] = True

    def remove_shape(self):
        for index in self.indexes:
            self.tiles[index] = False

    def index_is_valid(self, i) -> bool:
        # tile already exists
        if self.tiles[i]:
            return False
        if i < 0 or i >= len(self.tiles):
            assert False
            return False
        return True

    def get_rects(self) -> list[arcade.Rect]:
        rects = []
        for index in self.indexes:
            row, col = divmod(index, BLOCK_COUNT // 2)
            left = self.start_left + (col * self.dim)
            bottom = row * self.dim
            rects.append(
                arcade.rect.LRBT(left, left + self.dim, bottom, bottom + self.dim)
            )
        return rects

    def draw(self):
        for rect in self.get_rects():
            arcade.draw_rect_filled(rect, self.color)

    def hit(self, speed_y: float, speed_x: float):
        # move right
        if speed_x > 0:
            new_indexes = list(map(lambda x: x + 1, self.indexes))
            if all(map(self.index_is_valid, new_indexes)):
                self.indexes = new_indexes
        # move left
        elif speed_x > 0:
            new_indexes = list(map(lambda x: x - 1, self.indexes))
            if all(map(self.index_is_valid, new_indexes)):
                self.indexes = new_indexes

    def rotate(self):
        pass


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


class Ball:
    def __init__(self, position, speed, width=20, height=20):
        self.center_x, self.center_y = position
        self.speed_x, self.speed_y = speed
        self.width = width
        self.height = height

    def update(self):
        self.center_x += self.speed_x
        self.center_y += self.speed_y

        if (
            self.center_x - self.width / 2 < 0
            or self.center_x + self.width / 2 > SCREEN_WIDTH
        ):
            self.speed_x *= -1
        if (
            self.center_y - self.height / 2 < 0
            or self.center_y + self.height / 2 > SCREEN_HEIGHT
        ):
            self.speed_y *= -1

    def get_rect(self) -> arcade.Rect:
        return arcade.rect.XYRR(
            x=self.center_x,
            y=self.center_y,
            half_height=self.height // 2,
            half_width=self.width // 2,
        )


class Paddle:
    def __init__(self, position, key_up, key_down, *args, **kwargs):
        self.width = 20
        self.height = 100
        self.center_x, self.center_y = position
        self.speed = 20
        self.key_up = key_up
        self.key_down = key_down

    def get_rect(self):
        return arcade.rect.XYWH(self.center_x, self.center_y, self.width, self.height)

    def update(self):
        if self.center_y < self.height / 2:
            self.center_y = self.height / 2
        if self.center_y > SCREEN_HEIGHT - self.height / 2:
            self.center_y = SCREEN_HEIGHT - self.height / 2


class Pong(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

        self.ball = Ball((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (10, 0))
        self.player_1 = Paddle((50, SCREEN_HEIGHT // 2), arcade.key.W, arcade.key.S)
        self.player_2 = Paddle(
            (SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2), arcade.key.UP, arcade.key.DOWN
        )
        self.player_1_score = 0
        self.player_2_score = 0
        self.up_pressed = False
        self.down_pressed = False
        self.w_pressed = False
        self.s_pressed = False
        self.tetris = Tetris()

    def on_draw(self):
        self.clear()
        self.tetris.draw()
        arcade.draw_rect_filled(self.ball.get_rect(), arcade.color.WHITE_SMOKE)
        arcade.draw_rect_outline(
            self.ball.get_rect(), arcade.color.BLACK_LEATHER_JACKET, 3
        )
        arcade.draw_rect_filled(self.player_1.get_rect(), arcade.color.WHITE)
        arcade.draw_rect_filled(self.player_2.get_rect(), arcade.color.WHITE)
        arcade.draw_text(
            str(self.player_1_score), 20, SCREEN_HEIGHT - 30, arcade.color.WHITE, 20
        )
        arcade.draw_text(
            str(self.player_2_score),
            SCREEN_WIDTH - 40,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            20,
        )

    def update(self, delta_time):
        self.ball.update()
        self.player_1.update()
        self.player_2.update()

        # player hit the ball
        if (
            self.ball.get_rect().overlaps(self.player_1.get_rect())
            and self.ball.speed_x < 0
        ):
            self.ball.speed_x *= -1
            offset = self.ball.center_y - self.player_1.center_y
            self.ball.speed_y = offset / 10
        if (
            self.ball.get_rect().overlaps(self.player_2.get_rect())
            and self.ball.speed_x > 0
        ):
            self.ball.speed_x *= -1
            offset = self.ball.center_y - self.player_2.center_y
            self.ball.speed_y = offset / 10

        # player movement
        if self.up_pressed:
            self.player_2.center_y += self.player_2.speed
        if self.down_pressed:
            self.player_2.center_y -= self.player_2.speed
        if self.w_pressed:
            self.player_1.center_y += self.player_1.speed
        if self.s_pressed:
            self.player_1.center_y -= self.player_1.speed

        # player "scores"
        if self.ball.center_x - (self.ball.width // 2) < 0:
            self.player_2_score += 1
            self.ball.center_x = SCREEN_WIDTH // 2
            self.ball.center_y = SCREEN_HEIGHT // 2
        elif (self.ball.center_x) + (self.ball.width // 2) > SCREEN_WIDTH:
            self.player_1_score += 1
            self.ball.center_x = SCREEN_WIDTH // 2
            self.ball.center_y = SCREEN_HEIGHT // 2

        # ball out of bounds
        if self.ball.center_y - (self.ball.height // 2) < 0 and self.ball.speed_y < 0:
            self.ball.speed_y *= -1
        elif (
            self.ball.center_y + (self.ball.height // 2) > SCREEN_HEIGHT
            and self.ball.speed_y > 0
        ):
            self.ball.speed_y *= -1

        # block hits
        ball_rect = self.ball.get_rect()
        for block in self.tetris.blocks:
            if any(map(ball_rect.overlaps, block.get_rects())):
                block.hit(self.ball.speed_y, self.ball.speed_x)

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
    arcade.schedule(app.update, 1 / 30)
    arcade.run()
