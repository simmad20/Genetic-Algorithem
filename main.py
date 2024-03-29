
import pygame
import math
import random
import time

pygame.init()
screen_width = 1200
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Genetic Algorithem")

MUTATION_PROBABILITY = 0.05
REPRODUCTION_PROBABILITY = 0.06
REPRODUCTION_AND_MUTATION_INTERVAL = 10
PRINT_INTERVAL = 10
NUMBER_OF_GENES = 10
FOOD_PROBABILITY = 0.0001
OUTLINE_ENABLED = True

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
all_items = []
balls = []
foods = []
poisons = []


class Button:
    """
    Represents a clickable button with methods for drawing and interaction.
    """
    def __init__(self, x, y, width, height, color, text, font_size=30):
        """
        Initializes the Button object with specified parameters.

        Parameters:
        - x: x-coordinate of the button's top-left corner.
        - y: y-coordinate of the button's top-left corner.
        - width: Width of the button.
        - height: Height of the button.
        - color: Color of the button.
        - text: Text to be displayed on the button.
        - font_size: Font size of the text (default is 30).
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.font_size = font_size
        self.font = pygame.font.Font(None, self.font_size)
        self.clicked = False

    def draw(self):
        """
        Draws the button on the screen.

        Parameters:
        - screen: Pygame screen surface.
        """
        global screen
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_x, mouse_y):
        """
        Checks if the button is clicked.

        Parameters:
        - mouse_x: The x-coordinate of the mouse.
        - mouse_y: The y-coordinate of the mouse.

        Sets the 'clicked' attribute to True if the button is clicked.
        """
        if self.x < mouse_x < self.x + self.width and self.y < mouse_y < self.y + self.height:
            self.clicked = True
        else:
            self.clicked = False
        return self.clicked


class Circle:
    """
    Represents a circle object with methods for drawing and removal.
    """
    def __init__(self, x, y, radius, color):
        """
        Initializes the Circle object with specified parameters.

        Parameters:
        - x: x-coordinate of the circle's center.
        - y: y-coordinate of the circle's center.
        - radius: radius of the circle.
        - color: color of the circle.
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def remove(self):
        """
        Removes the circle from the screen.
        """
        global screen
        pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), self.radius)

    def draw(self):
        """
        Draws the circle on the screen.
        """
        global screen
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


class Food(Circle):
    """
    Represents a food item, inheriting from the Circle class.
    """
    def __init__(self, x, y, radius, color):
        """
        Initializes the Food object with specified parameters.

        Parameters:
        - x: x-coordinate of the food's center.
        - y: y-coordinate of the food's center.
        - radius: radius of the food.
        - color: color of the food.
        """
        super().__init__(x, y, radius, color)

    def remove(self):
        """
        Removes the food item from the screen and the global foods list.
        """
        global foods
        super().remove()
        foods.remove(self)

    def draw(self):
        """
        Draws the food item on the screen.
        """
        super().draw()


class Poison(Circle):
    """
    Represents a poison item, inheriting from the Circle class.
    """
    def __init__(self, x, y, radius, color):
        """
        Initializes the Poison object with specified parameters.

        Parameters:
        - x: x-coordinate of the poison's center.
        - y: y-coordinate of the poison's center.
        - radius: radius of the poison.
        - color: color of the poison.
        """
        super().__init__(x, y, radius, color)

    def remove(self):
        """
        Removes the poison item from the screen and the global poisons list.
        """
        global poisons
        super().remove()
        poisons.remove(self)

    def draw(self):
        """
        Draws the poison item on the screen.
        """
        super().draw()


class Genome:
    """
    Represents a genome with genetic information for the AI.
    """
    def __init__(self):
        """
        Initializes the Genome object with a list of random genes.
        """
        self.genes = [random.random() for _ in range(NUMBER_OF_GENES)]

    def __len__(self):
        """
        Returns the length of the genome.

        Returns:
        The length of the genome.
        """
        return len(self.genes)

    def __getitem__(self, index):
        """
        Gets the gene at the specified index.

        Parameters:
        - index: Index of the gene.

        Returns:
        The gene at the specified index.
        """
        return self.genes[index]

    def mutate(self):
        """
        Mutates the genome by randomly adjusting some genes.
        """
        for i in range(len(self.genes)):
            if random.random() < MUTATION_PROBABILITY:
                self.genes[i] += random.random()

    def __str__(self):
        """
        Returns a string representation of the genome.

        Returns:
        A string representation of the genome.
        """
        return str(self.genes)


class Brain:
    """
    Represents the brain of an AI with methods for learning and decision-making.
    """
    def __init__(self, genome):
        """
        Initializes the Brain object with a given genome and memory.

        Parameters:
        - genome: The genome object containing genetic information.
        """
        self.genome = genome
        self.memory = {}
        self.weighted_gene_sum = sum(self.genome.genes)
        self.short_term_memory = 0

    def __iter__(self):
        """
        Initializes an iterator for the genes in the genome.

        Returns:
        The iterator object.
        """
        self.index = 0
        return self

    def __next__(self):
        """
        Retrieves the next gene in the genome.

        Returns:
        The next gene in the genome.

        Raises:
        StopIteration: If there are no more genes to retrieve.
        """
        if self.index >= len(self.genome):
            raise StopIteration
        else:
            self.index += 1
            return self.genome[self.index - 1]

    def learn(self, item):
        """
        Learns from a given item by updating the memory.

        Parameters:
        - item: The item to learn from.
        """
        if item in self.memory:
            self.memory[item] += 1
        else:
            self.memory[item] = 1

    def remember(self, item, value):
        """
        Remembers a specific value associated with an item in the memory.

        Parameters:
        - item: The item to remember.
        - value: The value associated with the item.
        """
        self.memory[item] = value

    def forget(self, item):
        """
        Forgets a specific item from the memory.

        Parameters:
        - item: The item to forget.
        """
        if item in self.memory:
            del self.memory[item]

    def think(self, position, radius, visibility):
        """
        Makes a decision based on the current position, radius, and all available food and poison.

        Parameters:
        - position: Dictionary with 'x' and 'y' representing the current position.
        - radius: The radius of the AI.
        - visibility: The visibility range of the AI.

        Returns:
        The direction to move in.
        """
        global foods, poisons
        visible_food = self.get_visible_items(position, visibility, foods)
        visible_poison = self.get_visible_items(position, visibility, poisons)
        direction = self.calculate_direction(self.genome)

        if "food" in self.memory:
            direction = self.seek_food(direction, self.memory["food"], position, visible_food)
        if "poison" in self.memory:
            direction = self.avoid_poison(direction, self.memory["poison"], position, radius, visible_poison)
        if "position" in self.memory and "food" in self.memory: 
            direction = self.overthink_position(direction, position, self.memory["position"])
        else: self.remember("position", position)

        return direction
    
    def get_visible_items(self, position, visibility, all_items):
        """
        Returns a list of items within the visibility range of the AI.

        Parameters:
        - position: Dictionary with 'x' and 'y' representing the current position.
        - visibility: The visibility range of the AI.
        - all_items: List of all items.

        Returns:
        List of items within the visibility range.
        """
        visible_items = [item for item in all_items if self.calculate_distance(position, item) <= visibility]
        return visible_items
    
    def calculate_distance(self, position1, position2):
        """
        Calculates the distance between two positions.

        Parameters:
        - position1: Dictionary with 'x' and 'y' representing the first position.
        - position2: Dictionary with 'x' and 'y' representing the second position.

        Returns:
        The distance between the two positions.
        """
        if isinstance(position1, dict): x1, y1 = position1['x'], position1['y']
        else: x1, y1 = position1.x, position1.y

        if isinstance(position2, dict): x2, y2 = position2['x'], position2['y']
        else: x2, y2 = position2.x, position2.y

        dx = x1 - x2
        dy = y1 - y2
        return math.sqrt(dx ** 2 + dy ** 2)
    
    def calculate_direction(self, genome):
        """
        Calculates the overall direction based on the weighted sum of genes.

        Parameters:
        - genome: The genome object.

        Returns:
        The calculated direction.
        """
        if "direction" in self.memory:
            direction = self.memory["direction"]
        else:
            weighted_gene_sum = sum(genome.genes)
            for gene in genome.genes:
                self.weighted_gene_sum += gene / weighted_gene_sum * random.uniform(0, 2 * math.pi)

            dx = math.cos(self.weighted_gene_sum)
            dy = math.sin(self.weighted_gene_sum)
            direction = math.atan2(dy, dx)
            self.remember("direction", direction)
        return direction
    
    def seek_food(self, direction, food_memory, position, visible_food):
        """
        Adjusts the direction based on the memory of food.

        Parameters:
        - direction: The current direction.
        - food_memory: The memory value for food.
        - position: Dictionary with 'x' and 'y' representing the current position.
        - visible_food: List of food items within the visibility range.

        Returns:
        The adjusted direction.
        """
        global foods
        if len(foods) > 0:
            
            memory = [False]
            for food in foods:
                if food in self.memory:
                    memory = [True, food]
            
            if memory[0]:
                chosen_food = self.memory[memory[1]]
            else:
                if not visible_food:
                    return direction
                
                valid_foods = [food for food in visible_food if not self.is_food_near_poison(food, poisons)]

                if not valid_foods:
                    return direction
                
                if food_memory * 0.05 * self.weighted_gene_sum > random.random():
                    chosen_food = min(valid_foods, key=lambda food: math.dist((position['x'], position['y']), (food.x, food.y)))
                    self.remember(chosen_food, chosen_food)
                else:
                    chosen_food = random.choice(valid_foods)
                    self.remember(chosen_food, chosen_food)

            dx = chosen_food.x - position['x']
            dy = chosen_food.y - position['y']
            direction_food = math.atan2(dy, dx)
            direction = direction_food if food_memory * self.weighted_gene_sum > random.random() else direction
        return direction
    
    def is_food_near_poison(self, food, poisons):
        """
        Checks if a food is near any poison.

        Parameters:
        - food: The Food object.
        - poisons: List of Poison objects.

        Returns:
        True if the food is near any poison, False otherwise.
        """
        for poison in poisons:
            distance_to_poison = math.sqrt((food.x - poison.x) ** 2 + (food.y - poison.y) ** 2)
            if distance_to_poison < food.radius + poison.radius + 20:
                return True
        return False
    
    def avoid_poison(self, direction, poison_memory, position, radius, visible_poison):
        """
        Adjusts the direction to avoid poison based on memory.

        Parameters:
        - direction: The current direction.
        - poison_memory: The memory value for poison.
        - position: Dictionary with 'x' and 'y' representing the current position.
        - radius: The radius of the AI.
        - visible_poison: List of poison items within the visibility range.

        Returns:
        The adjusted direction.
        """
        global poisons
        has_to_avoid_poison = [False]
        for poison in poisons:
            if self.is_surrounded_by_poison(poison, position, radius):
                has_to_avoid_poison = [True, poison]
                break
        probability = poison_memory * 0.05 * self.weighted_gene_sum
        if has_to_avoid_poison[0] and probability > random.random():
            direction_around_poison = self.calculate_direction_around_poison(has_to_avoid_poison[1], position)
            direction = direction_around_poison if direction_around_poison is not None else direction

        return direction
    
    def is_surrounded_by_poison(self, poison, position, radius):
        """
        Checks if the AI is surrounded by poison.

        Parameters:
        - poison: The Poison object.
        - position: Dictionary with 'x' and 'y' representing the current position.
        - radius: The radius of the AI.

        Returns:
        True if the AI is surrounded by poison, False otherwise.
        """
        distance_to_poison = math.sqrt((position['x'] - poison.x) ** 2 + (position['y'] - poison.y) ** 2)
        return distance_to_poison < radius + poison.radius + 20
    
    def calculate_direction_around_poison(self, poison, position):
        """
        Calculates a direction to move around the given poison.

        Parameters:
        - poison: The Poison object.
        - position: Dictionary with 'x' and 'y' representing the current position.

        Returns:
        A new direction to move around the poison, or None if calculation fails.
        """
        try:
            angle_to_poison = math.atan2(poison.y - position['y'], poison.x - position['x'])
            new_direction = angle_to_poison + math.pi / 2
            return new_direction
        except Exception as e:
            print("Error calculating direction around poison:", e)
            return None
        
    def overthink_position(self, direction, position, last_position):
        global foods
        if len(foods) > 0:
            
            food_in_memory = None
            for food in foods:
                if food in self.memory:
                    food_in_memory = food
                    
            if food_in_memory:
                distance_to_last_position = self.calculate_distance(last_position, food_in_memory)
                distance_to_current_position = self.calculate_distance(position, food_in_memory)
                
                if distance_to_last_position < distance_to_current_position:
                    dx = food_in_memory.x - position['x']
                    dy = food_in_memory.y - position['y']
                    direction = math.atan2(dy, dx)
                    
                if distance_to_last_position == distance_to_current_position:
                    self.forget(food_in_memory)
                    direction = self.calculate_direction(self.genome)
            
        self.forget("position")
        return direction

    def __str__(self):
        """
        Returns a string representation of the Brain.

        Returns:
        A string representation of the Brain.
        """
        return f"Genome: {self.genome}\nMemory: {self.memory}\nWeighted Gene Sum: {self.weighted_gene_sum}\nShort-Term Memory: {self.short_term_memory}"


class Ball:
    """
    Represents a ball object with methods for movement, collision, and AI interactions.
    """
    def __init__(self, x, y, id, radius, color, speed):
        """
        Initializes the Ball object with specified parameters.

        Parameters:
        - x: x-coordinate of the ball's center.
        - y: y-coordinate of the ball's center.
        - id: Unique identifier for the ball.
        - radius: Radius of the ball.
        - color: Color of the ball.
        - speed: List containing the speed of the ball in the x and y directions.
        """
        self.x = x
        self.y = y
        self.id = id
        self.radius = radius
        self.color = color
        self.speed = speed
        self.fitness = 100
        self.foodSaturation = 100
        self.age = 1
        self.direction = 0
        self.last_print_time = 0
        self.last_reproduction_time = 0
        self.last_mutate_time = 0
        self.visibility = 100
        self.brain = Brain(Genome())

    def learn(self, item):
        """
        Learns from a given item by updating the AI's brain memory.

        Parameters:
        - item: The item to learn from.
        """
        self.brain.learn(item)

    def remember(self, item, value):
        """
        Remembers a specific value associated with an item in the AI's brain memory.

        Parameters:
        - item: The item to remember.
        - value: The value associated with the item.
        """
        self.brain.remember(item, value)

    def forget(self, item):
        """
        Forgets a specific item from the AI's brain memory.

        Parameters:
        - item: The item to forget.
        """
        self.brain.forget(item)

    def aging(self):
        """
        Simulates the aging process of the AI, affecting fitness and food saturation.
        """
        if self.foodSaturation > 0:
            self.foodSaturation -= 0.005
        else:
            self.fitness -= 0.005
        self.age += 1

    def move(self):
        """
        Moves the ball based on the AI's brain decision.
        """
        self.direction = self.brain.think({'x': self.x, 'y': self.y}, self.radius, self.visibility)
        self.x += self.speed[0] * math.cos(self.direction)
        self.y += self.speed[1] * math.sin(self.direction)

    def bounce(self, screen_width, screen_height):
        """
        Bounces the ball off the screen borders.

        Parameters:
        - screen_width: Width of the screen.
        - screen_height: Height of the screen.
        """
        if self.x + self.radius > screen_width or self.x - self.radius < 0:
            self.speed[0] *= -1
        if self.y + self.radius > screen_height or self.y - self.radius < 0:
            self.speed[1] *= -1

    def handle_collisions(self, other):
        """
        Handles collision with other objects and updates AI state accordingly.

        Parameters:
        - ball: The Ball object.
        - other: The object with which collision occurs.
        """
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < self.radius + other.radius:
            if isinstance(other, Food):
                self.handle_food_collision(other)
            elif isinstance(other, Poison):
                self.handle_poison_collision(other)

    def handle_food_collision(self, food):
        """
        Handles collision with a food object and updates AI state accordingly.

        Parameters:
        - ball: The Ball object.
        - food: The Food object.
        """
        self.learn("food")
        if food in self.brain.memory: self.brain.forget(food)
        self.fitness = min(self.fitness + 5, 100)
        self.foodSaturation = min(self.foodSaturation + 20, 100)
        food.remove()

    def handle_poison_collision(self, poison):
        """
        Handles collision with a poison object and updates AI state accordingly.

        Parameters:
        - ball: The Ball object.
        - poison: The Poison object.
        """
        self.learn("poison")
        self.fitness = max(self.fitness - 20, 0)
        poison.remove()
        
    def update_color(self):
        """
        Updates the color of the ball based on its fitness.
        """
        if self.fitness < 25:
            self.color = (255, 0, 0)
        elif self.fitness < 50:
            self.color = (255, 165, 0)
        elif self.fitness < 75:
            self.color = (255, 210, 0)
        else:
            self.color = (0, 255, 0)

    def draw(self):
        """
        Draws the ball on the screen.
        """
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        
    def draw_health_bar(self):
        """
        Draws the health bar of the ball on the screen.
        """
        pygame.draw.rect(screen, (255, 0, 0), (self.x - self.radius, self.y - self.radius - 10, 2 * self.radius, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - self.radius, self.y - self.radius - 10, (self.fitness / 100) * 2 * self.radius, 5))

    def draw_hunger_bar(self):
        """
        Draws the hunger bar of the ball on the screen.
        """
        pygame.draw.rect(screen, (255, 255, 0), (self.x - self.radius, self.y + self.radius + 5, 2 * self.radius, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - self.radius, self.y + self.radius + 5, (self.foodSaturation / 100) * 2 * self.radius, 5))
        
    def draw_visibility_outline(self):
        """
        Draws a Outline Circle to show how great the visibility of a ball is.
        """
        pygame.draw.circle(screen, (0, 255, 0), (self.x, self.y), self.radius + self.visibility, width=2)

    def check_mutation(self):
        """
        Checks if it's time for the AI to undergo mutation and mutates its genome accordingly.
        """
        if time.time() - self.last_mutate_time >= REPRODUCTION_AND_MUTATION_INTERVAL:
            self.brain.genome.mutate()
            self.last_mutate_time = time.time()

    def check_reproduction(self):
        """
        Checks if it's time for the AI to reproduce and initiates reproduction if conditions are met.
        """
        if time.time() - self.last_reproduction_time >= REPRODUCTION_AND_MUTATION_INTERVAL:
            self.reproduce(random.random())
            self.last_reproduction_time = time.time()

    def reproduce(self, probability):
        """
        Reproduces a new AI ball with certain probability.

        Parameters:
        - probability: The probability of reproduction.
        """
        if probability < REPRODUCTION_PROBABILITY:
            new_id = len(balls)
            new_radius = self.radius * 1.2
            new_color = self.mix_colors(self.color, random.choice(colors))
            new_speed = [self.speed[0] * 1.2, self.speed[1] * 1.2]
            new_ball = Ball(self.x, self.y, new_id, new_radius, new_color, new_speed)
            balls.append(new_ball)
            new_ball.brain.genome.genes = self.brain.genome.genes.copy()
            new_ball.brain.memory = self.brain.memory.copy()
            new_ball.brain.genome.mutate()
            if "food" in new_ball.brain.memory: new_ball.brain.memory["food"] /= 2
            if "poison" in new_ball.brain.memory: new_ball.brain.memory["poison"] /= 2

    def mix_colors(self, color1, color2):
        """
        Mixes two colors and returns the result.

        Parameters:
        - color1: The first color.
        - color2: The second color.

        Returns:
        The mixed color.
        """
        r = (color1[0] + color2[0]) / 2
        g = (color1[1] + color2[1]) / 2
        b = (color1[2] + color2[2]) / 2
        return (r, g, b)

    def mix_speeds(self, speed1, speed2):
        """
        Mixes two speed vectors and returns the result.

        Parameters:
        - speed1: The first speed vector.
        - speed2: The second speed vector.

        Returns:
        The mixed speed vector.
        """
        dx = speed1[0] + speed2[0]
        dy = speed1[1] + speed2[1]
        return [dx, dy]

    def checkIfAlive(self):
        """
        Checks if the AI is alive based on its fitness.

        Returns:
        True if alive, False otherwise.
        """
        if self.fitness <= 0:
            self.reproduce(random.random())
            return False
        return True

    def checkIfPrint(self, mouse_x, mouse_y):
        """
        Checks if information about the AI should be printed based on mouse proximity.

        Parameters:
        - mouse_x: The x-coordinate of the mouse.
        - mouse_y: The y-coordinate of the mouse.
        """
        dx = self.x - mouse_x
        dy = self.y - mouse_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < self.radius:
            if math.sqrt((self.x - mouse_x) ** 2 + (self.y - mouse_y) ** 2) < 100 and time.time() - self.last_print_time > PRINT_INTERVAL:
                print(f"id: {self.id}")
                print(f"x: {self.x}")
                print(f"y: {self.y}")
                print(f"radius: {self.radius}")
                print(f"color: {self.color}")
                print(f"speed: {self.speed}")
                print(f"fitness: {self.fitness}")
                print(f"age: {self.age / 1000}")
                print(self.brain)
                self.last_print_time = time.time()

    def checkMemory(self):
        """
        Checks and removes deprecated memories from the AI's brain memory.
        """
        deprecated_memorys = []
        for key in self.brain.memory.keys():
            if isinstance(key, Food):
                if not (key in foods): deprecated_memorys.append(key)
        if len(deprecated_memorys) > 0:
            for deprecated_memory in deprecated_memorys:
                self.brain.forget(deprecated_memory)

    def update(self, mouse_x, mouse_y):
        """
        Updates the AI state, handles interactions, and draws on the screen.

        Parameters:
        - mouse_x: The x-coordinate of the mouse.
        - mouse_y: The y-coordinate of the mouse.
        """
        for food in foods:
            self.handle_collisions(food)
        for poison in poisons:
            self.handle_collisions(poison)
        self.move()
        self.bounce(screen_width, screen_height)
        self.aging()
        self.update_color()
        self.checkIfPrint(mouse_x, mouse_y)
        self.check_mutation()
        self.draw()
        self.draw_health_bar()
        self.draw_hunger_bar()
        self.checkMemory()
        
        if OUTLINE_ENABLED:
            self.draw_visibility_outline()

def initializeSimulation():
    """
    Initializes the simulation by adding balls and food.
    """
    for i in range(random.randint(1, 5)):
        pos = {"x": 100, "y": 100}
        balls.append(Ball(random.randint(pos["x"], screen_width - 10), pos["y"], i, 15, colors[1], [0.1, 0.1]))
        pos["x"] += 40
        
    for i in range(random.randint(10, 60)):
        pos = {"x": random.randint(5, screen_width - 10), "y": random.randint(5, screen_height - 10)}
        foods.append(Food(pos["x"], pos["y"], 5, colors[1]))

def main():
    """
    The main function that controls the Pygame simulation.
    """
    global balls, foods, poisons, OUTLINE_ENABLED
    last_print_time = 0
    button = Button(0, 0, 200, 50, (0, 255, 0), "Toggle Outline")
    ticks = 0

    running = True
    while running:
        if len(balls) == 0: initializeSimulation()
        aliveBalls = [True for _ in balls]
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.fill((0, 0, 0))
        ballsKilled = 0
        button.draw()
        ticks += 1

        if time.time() - last_print_time > 10:
            print(f"Number of alive balls: {len(aliveBalls)}")
            last_print_time = time.time()

        if ticks % 1000 == 0:
            pos = {"x": random.randint(5, screen_width - 10), "y": random.randint(5, screen_height - 10)}
            foods.append(Food(pos["x"], pos["y"], 5, colors[1]))

        if random.random() < FOOD_PROBABILITY:
            pos = {"x": random.randint(5, screen_width - 10), "y": random.randint(5, screen_height - 10)}
            poisons.append(Poison(pos["x"], pos["y"], 5, colors[0]))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button.is_clicked(mouse_x, mouse_y):
                    OUTLINE_ENABLED = not OUTLINE_ENABLED

        for i in range(len(balls)):
            balls[i].update(mouse_x, mouse_y)
            aliveBalls[i] = balls[i].checkIfAlive()

        for food in foods:
            food.draw()

        for poison in poisons:
            poison.draw()
           

        for i in range(len(aliveBalls)):
            if not aliveBalls[i]:
                del balls[i - ballsKilled]
                ballsKilled += 1

        for ball in balls:
            ball.check_reproduction()

        pygame.display.update()

    pygame.quit()


main()