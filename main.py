import arcade

SCREEN_WIDTH = 1040
SCREEN_HEIGHT = 680
SCREEN_TITLE = "Pong"


class Ball:
    def __init__(self, position, speed):
        self.center_x, self.center_y = position
        self.speed_x, self.speed_y = speed
        self.width = 50
        self.height = 50
        self.color = arcade.color.WHITE

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

    def get_rect(self):
        # def XYRR(x: AsFloat, y: AsFloat, half_width: AsFloat, half_height: AsFloat) -> Rect:
        return arcade.rect

    def draw(self):
        arcade.rect.XYRR(
            x=self.center_x,
            y=self.center_y,
            half_height=self.height // 2,
            half_width=self.width // 2,
        )
        arcade.draw_rect_filled(
            self.center_x, self.center_y, self.width, self.height, self.color
        )


class Paddle(arcade.Sprite):
    def __init__(self, position, key_up, key_down, *args, **kwargs):
        super().__init__("white_box.png", scale=2.5, *args, **kwargs)
        self.center_x, self.center_y = position
        self.speed = 5
        self.key_up = key_up
        self.key_down = key_down
        self.width = 20
        self.height = 100

    def update(self):
        if self.center_y < self.height / 2:
            self.center_y = self.height / 2
        if self.center_y > SCREEN_HEIGHT - self.height / 2:
            self.center_y = SCREEN_HEIGHT - self.height / 2


class Pong(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

        self.ball = Ball((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (5, 5))
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

    def on_draw(self):
        arcade.start_render()
        self.ball.draw_hit_box()
        self.player_1.draw_hit_box(arcade.color.WHITE)
        self.player_2.draw_hit_box(arcade.color.WHITE)
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

        if arcade.check_for_collision(self.ball, self.player_1):
            self.ball.speed_x *= -1
            offset = self.ball.center_y - self.player_1.center_y
            self.ball.speed_y = offset / 10
        # if arcade.check_for_collision(self.ball, self.player_2):

        if self.up_pressed:
            self.player_2.center_y += self.player_2.speed
        if self.down_pressed:
            self.player_2.center_y -= self.player_2.speed
        if self.w_pressed:
            self.player_1.center_y += self.player_1.speed
        if self.s_pressed:
            self.player_1.center_y -= self.player_1.speed

        if self.ball.left < 0:
            self.player_2_score += 1
            self.ball.center_x = SCREEN_WIDTH // 2
            self.ball.center_y = SCREEN_HEIGHT // 2
        if self.ball.right > SCREEN_WIDTH:
            self.player_1_score += 1
            self.ball.center_x = SCREEN_WIDTH // 2
            self.ball.center_y = SCREEN_HEIGHT // 2

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.W:
            self.w_pressed = True
        elif key == arcade.key.S:
            self.s_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.W:
            self.w_pressed = False
        elif key == arcade.key.S:
            self.s_pressed = False


if __name__ == "__main__":
    app = Pong(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
