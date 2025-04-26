from typing import Literal
import arcade
import random
import enum
import math

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


class Face(enum.Enum):
    TOP = 1
    BOTTOM = 2
    RIGHT = 3
    LEFT = 4



class Block:
    def __init__(self, dim: int, start_left: int, tiles: list[bool]) -> None:
        self.dim = dim
        self.start_left = start_left
        self.tiles = tiles
        self.create_new()


    @staticmethod
    def pos_to_index(row: int, col: int) -> int:
        if row < 0:
            row = BLOCK_COUNT - 1
        elif row > BLOCK_COUNT - 1:
            row = 0
        if col < 0:
            col = (BLOCK_COUNT // 2) - 1
        elif col > (BLOCK_COUNT // 2) - 1:
            col = 0

        return row + (BLOCK_COUNT // 2) * col

    @staticmethod
    def index_to_pos(i: int) -> tuple[int, int]:
        return divmod(i, BLOCK_COUNT // 2)

    def generate_indexes(self, start_row: int, start_col: int) -> list[tuple[int, int]]:
        if self.kind == 1:
            indexes = [
                (start_row, start_col),
                (start_row + 1, start_col),
                (start_row, start_col + 1),
                (start_row + 1, start_col + 1),
            ]
            self.color = arcade.color.YELLOW
        elif self.kind == 2:
            indexes = [
                (start_row, start_col),
                (start_row, start_col+1),
                (start_row, start_col+2),
                (start_row, start_col+3),
            ]
            self.color = arcade.color.CYAN
        else:
            raise Exception("Unknown kind")
        return indexes



    def get_indexes(self, kind: int, must_be_valid: bool) -> list[int]:
        assert kind > 0 and kind < 7
        self.kind = kind

        indexes = []
        if kind == 1:
            start_row = random.randint(0, BLOCK_COUNT - 2)
            start_col = random.randint(0, (BLOCK_COUNT // 2) - 2)
            self.color = arcade.color.YELLOW
        elif kind == 2:
            start_row = random.randint(0, BLOCK_COUNT - 1)
            start_col = random.randint(0, (BLOCK_COUNT // 2) - 4)
            self.color = arcade.color.CYAN
        else:
            raise Exception("Unknown kind")
        indexes = list(map(lambda xy: Block.pos_to_index(*xy), self.generate_indexes(start_row, start_col)))
        if not must_be_valid or all(map(self.index_is_valid, indexes)):
            return indexes
        else:
            return self.get_indexes(kind, must_be_valid)


    def create_new(self):
        # kind = random.randint(1, 2)
        kind = 2
        self.indexes = self.get_indexes(kind, True)
        self.goal_indexes = self.get_indexes(kind, False)

    def place_shape(self):
        for index in self.indexes:
            self.tiles[index] = True

    def update_if_win(self):
        if set(self.goal_indexes) != set(self.indexes):
            return
        global score
        score += 1
        self.create_new()


    def index_is_valid(self, i) -> bool:
        # tile already exists
        if self.tiles[i]:
            return False
        if i < 0 or i >= len(self.tiles):
            return False
        return True

    def get_rects(self, indexes) -> list[arcade.Rect]:
        rects = []
        for index in indexes:
            row, col = divmod(index, BLOCK_COUNT // 2)
            left = self.start_left + (col * self.dim)
            bottom = row * self.dim
            rects.append(
                arcade.rect.LRBT(left, left + self.dim, bottom, bottom + self.dim)
            )
        return rects

    def draw(self):
        for rect in self.get_rects(self.indexes):
            arcade.draw_rect_filled(rect, self.color)

    def draw_win(self):
        for rect in self.get_rects(self.goal_indexes):
            arcade.draw_rect_outline(rect, arcade.color.GREEN, 3)


    def hit(self, face: Face, index_of_hit_block, speed_x):
        print(face)
        # move right
        if is_rotate_mode:
            if speed_x > 0:
                self.rotate(index_of_hit_block, False)
            else:
                self.rotate(index_of_hit_block, True)
            self.update_if_win()
            return

        if face == Face.TOP:
            self.move_y(-1)
        elif face == Face.BOTTOM:
            self.move_y(1)
        elif face == Face.RIGHT:
            self.move_x(-1)
        elif face == Face.LEFT:
            self.move_x(1)
        self.update_if_win()


    def move_y(self, up_or_down: Literal[-1] | Literal[1]):
        new_indexes = []
        for old_index in self.indexes:
            new_index = old_index + ((BLOCK_COUNT // 2) * up_or_down)
            if new_index >= len(self.tiles):
                new_index = old_index % (BLOCK_COUNT // 2)
            elif new_index < 0:
                new_index = old_index + ((BLOCK_COUNT // 2) * (BLOCK_COUNT - 1))

            new_indexes.append(new_index)
        self.indexes = new_indexes

    # need to ensure staying on the same row
    def move_x(self, right_or_left: Literal[-1] | Literal[1]):
        new_indexes = []
        for old_index in self.indexes:
            old_row, old_col = divmod(old_index, (BLOCK_COUNT // 2))
            new_col = old_col + right_or_left
            if new_col <= -1:
                new_col = (BLOCK_COUNT // 2) - 1
            elif new_col >= BLOCK_COUNT // 2:
                new_col = 0
            new_indexes.append(old_row * (BLOCK_COUNT // 2) + new_col)
        self.indexes = new_indexes


    def rotate_template(self, index_of_rotation: int, number_of_rotations: Literal[1] | Literal[2] | Literal[3]):
        # regenerate the the shape because the shape columns are not preserved when normalizing
        #    to shaping around board
        og_shape = self.generate_indexes(0,0)
        hit_row, hit_col = og_shape[index_of_rotation]
        if number_of_rotations == 1:



    def rotate(self, index_of_hit_tile: int, is_left_rotation: bool):
        # always rotate around the block that was hit
        og_shape = self.generate_indexes(0, 0)
        hit_row_og, hit_col_og = og_shape[index_of_hit_tile]
        hit_row, hit_col = Block.index_to_pos(self.indexes[index_of_hit_tile])
        new_points = []
        for index in self.indexes:
            row, col = Block.index_to_pos(index)
            # translate to origin then 90* rotation
            new_col = -(row - hit_row) + hit_col
            new_row = (col - hit_col) + hit_row

            new_index = Block.pos_to_index(new_col, new_row)
            new_points.append(new_index)
        self.indexes = new_points
            


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


class Ball:
    def __init__(self, position, speed, width=20, height=20):
        self.frames_to_wait_to_move = 120
        self.center_x, self.center_y = position
        self.speed_x, self.speed_y = speed
        self.width = width
        self.height = height

    # want to preserve the total velocity so
    # speed_x^2 + speed_y^2 = sum_velocity^2 
    # when a paddle hits it with the edge we'll
    # make the angle a pecentage of the velocity

    def change_velocity(self, paddle: arcade.Rect, player: Literal[1] | Literal[2]):
        relative_intersect_y = (paddle.center_y - self.center_y) / (paddle.height / 2)
        bounce_angle = relative_intersect_y * (5 * math.pi / 12)
        speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
        if player == 1:
            self.speed_x = speed * math.cos(bounce_angle)
            self.speed_y = -(speed * math.sin(bounce_angle))
        else:
            self.speed_x = -speed * math.cos(bounce_angle)
            self.speed_y = -( speed * math.sin(bounce_angle) )

        pass

    def reset(self):
        self.speed_x = 0
        self.speed_y = 0
        self.update()
        if self.speed_x < 0:
            self.center_x, self.center_y = (((SCREEN_WIDTH // 2) + (5 * (SCREEN_HEIGHT // BLOCK_COUNT))), SCREEN_HEIGHT  // 2)
            self.speed_x = INITIAL_SPEED
        else:
            self.center_x, self.center_y = (((SCREEN_WIDTH // 2) - (5 * (SCREEN_HEIGHT // BLOCK_COUNT))), SCREEN_HEIGHT  // 2)
            self.speed_x = -INITIAL_SPEED
        self.frames_to_wait_to_move = FRAMES_TO_WAIT
        self.speed_y = 0

    def update(self):
# we'll always have to ensure a base amount 
# of velocity to keep the game going
# the ball will be moving faster then max velocity but that is ok
        # always move a good amount x just to jeep the game going
        if self.frames_to_wait_to_move > 0:
            self.frames_to_wait_to_move -= 1
            return
        if self.speed_x > 0:
            self.center_x += max(self.speed_x, MIN_SPEED)
        else:
            self.center_x += min(self.speed_x, -MIN_SPEED)
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
        self.height = 180
        self.center_x, self.center_y = position
        self.speed = PADDLE_SPEED
        self.key_up = key_up
        self.key_down = key_down

    def get_rect(self):
        return arcade.rect.XYWH(self.center_x, self.center_y, self.width, self.height)

    def update(self):
        if self.center_y < 50:
            self.center_y = 50
        if self.center_y > SCREEN_HEIGHT - 50:
            self.center_y = SCREEN_HEIGHT - 50


class Pong(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

        self.ball = Ball((((SCREEN_WIDTH // 2) + (5 * (SCREEN_HEIGHT // BLOCK_COUNT))), SCREEN_HEIGHT  // 2), (INITIAL_SPEED, 0))
        self.player_1 = Paddle((50, SCREEN_HEIGHT // 2), arcade.key.W, arcade.key.S)
        self.player_2 = Paddle(
            (SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2), arcade.key.UP, arcade.key.DOWN
        )
        self.lives = 5
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
                f"Score: {score}", 20, SCREEN_HEIGHT - 20, arcade.color.WHITE, 20
        )
        arcade.draw_text(
                f"Mode: {'Rotation' if is_rotate_mode else 'Move'}", 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 20
        )
        arcade.draw_text(
            f"Lives: {self.lives}",
            SCREEN_WIDTH - 100,
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
            self.ball.change_velocity(self.player_1.get_rect(), 1)
            # offset = self.ball.center_y - self.player_1.center_y

        if (
            self.ball.get_rect().overlaps(self.player_2.get_rect())
            and self.ball.speed_x > 0
        ):
            self.ball.speed_x *= -1
            self.ball.change_velocity(self.player_2.get_rect(), 2)
            # offset = self.ball.center_y - self.player_1.center_y
            # self.ball.speed_y = offset / 10

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
            self.lives -= 1
            self.ball.reset()
        elif (self.ball.center_x) + (self.ball.width // 2) > SCREEN_WIDTH:
            self.lives -= 1
            self.ball.reset()

        # ball hitting bottom and ceiling
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
            all_distance_faces = []
            for i, rect in enumerate(block.get_rects(block.indexes)):
                if ball_rect.overlaps(rect):
                    # need to figure out which face the ball hit
                    distance_faces = [
                            (i, Face.RIGHT, abs( ball_rect.left - rect.right )),
                            (i, Face.LEFT, abs( ball_rect.right - rect.left )),
                            (i, Face.TOP, abs( ball_rect.bottom - rect.top )),
                            (i, Face.BOTTOM, abs( ball_rect.top - rect.bottom ))
                            ]
                    all_distance_faces.extend(distance_faces)
            if all_distance_faces:
                i, face, _ = min(all_distance_faces, key=lambda x: x[2])
                # right
                if face == Face.RIGHT:
                    block.hit(Face.RIGHT, i, self.ball.speed_x)
                    self.ball.speed_x *= -1
                # left
                elif face == Face.LEFT:
                    block.hit(Face.LEFT, i, self.ball.speed_x)
                    self.ball.speed_x *= -1
                # top
                elif face == Face.TOP:
                    block.hit(Face.TOP, i, self.ball.speed_x)
                    self.ball.speed_y *= -1
                # bottom
                elif face == Face.BOTTOM:
                    block.hit(Face.BOTTOM, i, self.ball.speed_x)
                    self.ball.speed_y *= -1
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
