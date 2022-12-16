## The Ball class represents a ball in the simulation. It has a number of instance variables:

x and y: The x and y positions of the ball on the screen. <br>
dx and dy: The x and y velocities of the ball. <br>
radius: The radius of the ball. <br>
color: The color of the ball. br>
life: The remaining life of the ball. <br>
food_eaten: The amount of food the ball has eaten. <br>
poison_eaten: The amount of poison the ball has eaten. <br>
brain: An instance of the Brain class, which represents the ball's brain. <br>
genome: An instance of the Genome class, which represents the ball's genetic information. <br>
The Ball class has a number of methods: <br>
<br>
__init__(self, x, y, dx, dy, radius, color, life): This is the constructor for the Ball class. It initializes the instance variables and eates a new instance of the Brain and Genome classes. <br>
move(self): This method updates the position of the ball based on its velocity. <br>
draw(self, screen): This method draws the ball on the screen using Pygame. <br>
is_collision(self, other_ball): This method checks if the ball is colliding with another ball. <br>
is_collision_food(self, food): This method checks if the ball is colliding with a piece of food. <br>
is_collision_poison(self, poison): This method checks if the ball is colliding with a piece of poison. <br>
is_dead(self): This method checks if the ball is dead (i.e., if its life is 0). <br>
copy(self): This method returns a copy of the ball. <br>
calculate_fitness(self): This method calculates the fitness of the ball based on its food and poison intake. <br>
