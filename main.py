from random import choice, randint as r, seed
import threading
import arcade, os
from time import sleep as sl

SPRITE_SCALING = 3
SPRITE_NATIVE_SIZE = 16
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING)
WORLD_SIZE = SPRITE_SIZE * 70

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "MARIOCRAFT"

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 40
RIGHT_MARGIN = 150

# Physics
MOVEMENT_SPEED = 5
JUMP_SPEED = SPRITE_SCALING * 3
GRAVITY = 0.5


class MyGame(arcade.Window):
    """ Main application class. """
    def __init__(self):
        """
        Initializer
        """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.falling = 99
        self.debugmode = False  # DEVELOPMENT ONLY
        self.freecam = False  # DEVELOPMENT ONLY
        self.fc = self.freecam
        self.freecam = not self.fc and self.freecam

        # Set the working directory (where we expect to find files)
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Sprite lists
        self.entity_list = None
        self.wall_list = None
        self.pipe_list = None

        # Set up the player
        self.player_sprite = None
        self.physics_engine = None
        self.view_left = 0
        self.view_bottom = 0

    def setup(self):
        """ Set up the game and initialize the variables. """

        # self.set_fullscreen(True)
        self.set_vsync(True)

        # Sprite lists
        self.entity_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.pipe_list = arcade.SpriteList(use_spatial_hash=True)

        # Draw the walls on the bottom
        for x in range(0, WORLD_SIZE, SPRITE_SIZE):
            wall = arcade.Sprite("resources/images/tiles/bedrock.png",
                                 SPRITE_SCALING)

            wall.bottom = -SPRITE_SIZE
            wall.left = x
            self.wall_list.append(wall)

        # World Generation
        # seed(1) # uncomment for set seed
        b = r(12, 15) * SPRITE_SIZE
        for x in range(0, WORLD_SIZE, SPRITE_SIZE):
            b += r(r(-1, 0), r(0, 1)) * SPRITE_SIZE
            wall = arcade.Sprite("resources/images/tiles/grass_block.png",
                                 SPRITE_SCALING)

            wall.bottom = abs(b)
            wall.left = x
            self.wall_list.append(wall)

            if x % r(100, 200) == 0:
                pipe = arcade.Sprite("resources/images/tiles/pipe.png",
                                     SPRITE_SCALING - .5)
                pipe.bottom = abs(b) + SPRITE_SIZE
                pipe.left = x
                self.pipe_list.append(pipe)
            for y in range(1, int(wall.bottom), SPRITE_SIZE):
                wall2 = arcade.Sprite("resources/images/tiles/dirt.png",
                                      SPRITE_SCALING)

                wall2.bottom = y
                wall2.left = x
                self.wall_list.append(wall2)

        # Set up the player
        self.player_sprite = arcade.Sprite(
            "resources/images/entities/steve.png", SPRITE_SCALING)
        self.player_sprite_behavior = 0  # 0 = terrestrial, 1 = flying
        self.player_inpipe = False
        self.entity_list.append(self.player_sprite)

        # Starting position of the player
        self.player_sprite.center_x = WORLD_SIZE // 2
        # Make sure we don't spawn underground
        self.player_sprite.bottom = 1000

        self.physics_engine_entity = []

        self.move_camera_sprite(self.player_sprite)

        # Create entities
        for i in range(5):
            # Create a new Sprite
            entity = arcade.Sprite(
                f"resources/images/entities/{choice(['creeper','spider'])}.png",
                SPRITE_SCALING)

            # Position the entity
            entity.center_x = r(0, WORLD_SIZE)
            entity.bottom = 1000

            # Add the entity to the lists
            self.entity_list.append(entity)

            # Make the entity be a physics object
            self.physics_engine_entity.append(
                arcade.PhysicsEnginePlatformer(entity, self.wall_list,
                                               GRAVITY))

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, [self.wall_list, self.pipe_list], GRAVITY)

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        self.frameCount = 0

    def move_camera_sprite(self, sprite: arcade.Sprite):
        """
        Center the camera on the given sprite.
        """
        self.view_left = sprite.center_x - SCREEN_WIDTH / 2
        self.view_bottom = sprite.center_y - SCREEN_HEIGHT / 2
        # update the viewport to center on the sprite
        arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left,
                            self.view_bottom, SCREEN_HEIGHT + self.view_bottom)

    def move_camera(self, x, y):
        self.view_left += x
        self.view_bottom += y
        arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left,
                            self.view_bottom, SCREEN_HEIGHT + self.view_bottom)

    def on_draw(self):
        """
        Render the screen.
        """
        if self.physics_engine.can_jump():
            self.falling = 0
        # X coordinate relative to the viewport.

        self.frameCount += 1

        self.falling += 1

        # This command has to happen before we start drawing
        self.clear()

        if not self.freecam:
            self.move_camera_sprite(self.player_sprite)

        # Prevent the player from going off the edge of the screen
        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
        elif self.player_sprite.right > WORLD_SIZE:
            self.player_sprite.right = WORLD_SIZE

        # Draw all the sprites.
        self.wall_list.draw()
        self.entity_list.draw()
        self.pipe_list.draw()

    # called when the mouse moves
    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """
        Called when the user presses a mouse button
        """
        pass

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP and self.falling < 3:
            if not self.freecam:
                self.player_sprite.change_y = JUMP_SPEED
            else:
                self.move_camera(0, 100)
        elif key == arcade.key.LEFT:
            if not self.freecam:
                self.player_sprite.change_x = -MOVEMENT_SPEED
            else:
                self.move_camera(-100, 0)
        elif key == arcade.key.RIGHT:
            if not self.freecam:
                self.player_sprite.change_x = MOVEMENT_SPEED
            else:
                self.move_camera(100, 0)
        elif key == arcade.key.DOWN and self.freecam:
            self.move_camera(0, -100)
        elif key == arcade.key.DOWN:
            for pipe in self.pipe_list:
                if pipe.right > self.player_sprite.left and pipe.left < self.player_sprite.right:
                    if pipe.bottom < self.player_sprite.top:
                        self.player_sprite.bottom = pipe.bottom
                        self.player_inpipe = True
        elif key == arcade.key.SPACE and self.fc:
            self.freecam = not self.freecam
        elif key == arcade.key.R:
            if self.debugmode:
                threading.Thread(target=os.system,
                                 args=["python main.py"]).start()
                sl(.3)
                self.close()

    def on_key_release(self, key, modifiers):
        """
        Called when the user presses a mouse button
        """
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Update the player based on the physics engine
        if not self.player_inpipe:
            self.physics_engine.update()
        else:
            a = choice(self.pipe_list)
            self.player_sprite.left = a.left
            self.player_sprite.bottom = a.bottom
            self.player_inpipe = False
        for physics_engine in self.physics_engine_entity:
            physics_engine.update()


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
