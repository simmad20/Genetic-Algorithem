## The Ball class represents a ball in the simulation. It has a number of instance variables:

### x and y: The x and y positions of the ball on the screen.
### dx and dy: The x and y velocities of the ball.
### radius: The radius of the ball.
### color: The color of the ball.
### life: The remaining life of the ball.
### food_eaten: The amount of food the ball has eaten.
### poison_eaten: The amount of poison the ball has eaten.
### brain: An instance of the Brain class, which represents the ball's brain.
### genome: An instance of the Genome class, which represents the ball's genetic information.
### The Ball class has a number of methods:

### __init__(self, x, y, dx, dy, radius, color, life): This is the constructor for the Ball class. It initializes the instance variables and ###reates a new instance of the Brain and Genome classes.
### move(self): This method updates the position of the ball based on its velocity.
### draw(self, screen): This method draws the ball on the screen using Pygame.
### is_collision(self, other_ball): This method checks if the ball is colliding with another ball.
### is_collision_food(self, food): This method checks if the ball is colliding with a piece of food.
### is_collision_poison(self, poison): This method checks if the ball is colliding with a piece of poison.
### is_dead(self): This method checks if the ball is dead (i.e., if its life is 0).
### copy(self): This method returns a copy of the ball.
### calculate_fitness(self): This method calculates the fitness of the ball based on its food and poison intake.