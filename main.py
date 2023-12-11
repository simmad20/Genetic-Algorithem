import pygame
import math
import random
import time

pygame.init()
screen_width = 1200
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Genetic Algorithem")

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
balls = []
foods = []
poisons = []
obstacles = []
aliveBalls = []


class Circle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def remove(self):
        pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), self.radius)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


class Rectangle:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def remove(self):
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.x, self.y, self.width, self.height))

    def draw(self):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, self.width, self.height))


class CircleObstacle(Circle):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius, color)

    def remove_items_within_obstacle(self):
        global foods, poisons
        items_to_remove = []

        for food in foods:
            dx = self.x - food.x
            dy = self.y - food.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance < self.radius + food.radius:
                items_to_remove.append(food)

        for poison in poisons:
            dx = self.x - poison.x
            dy = self.y - poison.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance < self.radius + poison.radius:
                items_to_remove.append(poison)

        for item in items_to_remove:
            item.remove()

    def draw(self):
        super().draw()


class RectangleObstacle(Rectangle):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)
        
    def remove_items_within_obstacle(self):
        global foods, poisons  # Füge dies hinzu, um auf die globalen Variablen zuzugreifen
        items_to_remove = []

        for food in foods:
            if self.is_point_inside_rectangle((food.x, food.y), (self.x, self.y), self.width, self.height):
                items_to_remove.append(food)

        for poison in poisons:
            if self.is_point_inside_rectangle((poison.x, poison.y), (self.x, self.y), self.width, self.height):
                items_to_remove.append(poison)

        for item in items_to_remove:
            item.remove()

    def is_point_inside_rectangle(self, point, rectangle_top_left, rectangle_width, rectangle_height):
        return (
            rectangle_top_left[0] <= point[0] <= rectangle_top_left[0] + rectangle_width and
            rectangle_top_left[1] <= point[1] <= rectangle_top_left[1] + rectangle_height
        )

    def draw(self):
        super().draw()


class Food(Circle):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius, color)

    def remove(self):
        super().remove()
        foods.remove(self)

    def draw(self):
        super().draw()


class Poison(Circle):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius, color)

    def remove(self):
        super().remove()
        poisons.remove(self)

    def draw(self):
        super().draw()


class Genome:
    def __init__(self):
        self.genes = [random.random() for _ in range(10)]

    def __len__(self):
        return len(self.genes)

    def __getitem__(self, index):
        return self.genes[index]

    def mutate(self):
        for i in range(len(self.genes)):
            if random.random() < 0.05:
                self.genes[i] += random.random()

    def __str__(self):
        return str(self.genes)


class Brain:
    def __init__(self, genome):
        self.genome = genome
        self.memory = {}
        self.weighted_gene_sum = 0
        self.short_term_memory = 0

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index >= len(self.genome):
            raise StopIteration
        else:
            self.index += 1
            return self.genome[self.index - 1]

    def learn(self, item):
        if item in self.memory:
            self.memory[item] += 1
        else:
            self.memory[item] = 1

    def remember(self, item, value):
        self.memory[item] = value

    def forget(self, item):
        if item in self.memory:
            del self.memory[item]

    def think(self, position, radius):
        direction = self.calculate_direction(self.genome)

        if "food" in self.memory:
            direction = self.seek_food(direction, self.memory["food"], position)
        if "poison" in self.memory:
            direction = self.avoid_poison(direction, self.memory["poison"], position, radius)

        return direction
    
    def seek_food(self, direction, food_memory, position):
        if len(foods) > 0:
            memory = [False]
            for food in foods:
                if food in self.memory:
                    memory = [True, food]
            
            if memory[0]:
                chosen_food = self.memory[memory[1]]
            else:
                probability = food_memory * 0.05 * self.weighted_gene_sum
                if probability > random.random():
                    chosen_food = min(foods, key=lambda food: math.dist((position['x'], position['y']), (food.x, food.y)))
                    self.remember(chosen_food, chosen_food)
                else:
                    chosen_food = random.choice(foods)
                    self.remember(chosen_food, chosen_food)
            dx = chosen_food.x - position['x']
            dy = chosen_food.y - position['y']
            direction_food = math.atan2(dy, dx)
            direction = direction_food if food_memory * self.weighted_gene_sum > random.random() else direction
        return direction
    
    # todo
    def avoid_poison(self, direction, poison_memory, position, radius):
        has_to_avoid_poison = False
        for poison in poisons:
            if self.is_surrounded_by_poison(poison, position, radius):
                has_to_avoid_poison = True
                break
        if has_to_avoid_poison and poison_memory > 0:
            direction_around_poison = self.calculate_direction_around_poison(poisons, position)
            direction = direction_around_poison if direction_around_poison is not None else direction

        return direction

    # todo
    def calculate_direction_around_poison(self, poisons, position):
        escape_direction = None
        for poison in poisons:
            dx = position['x'] - poison.x
            dy = position['y'] - poison.y
            distance_to_poison = math.sqrt(dx ** 2 + dy ** 2)

            if distance_to_poison <= poison.radius:
                angle_around_poison = math.atan2(dy, dx)
                escape_direction = angle_around_poison + math.pi / 2
                break

        return escape_direction

    def calculate_direction(self, genome):
        if "direction" in self.memory:
            direction = self.memory["direction"]
        else:
            for gene in genome.genes:
                self.weighted_gene_sum += gene / sum(genome.genes) * random.uniform(0, 2 * math.pi)

            dx = math.cos(self.weighted_gene_sum)
            dy = math.sin(self.weighted_gene_sum)
            direction = math.atan2(dy, dx)
            self.remember("direction", direction)
        return direction

    # todo
    def is_surrounded_by_poison(self, poison, position, radius):
        dx = position['x'] - poison.x
        dy = position['y'] - poison.y
        distance_to_poison = math.sqrt(dx ** 2 + dy ** 2)

        if distance_to_poison <= radius + poison.radius:
            future_x = position['x'] + self.speed[0]
            future_y = position['y'] + self.speed[1]
            distance_to_future = math.sqrt((future_x - poison.x) ** 2 + (future_y - poison.y) ** 2)

            if distance_to_future <= radius + poison.radius:
                return True

        return False


    def __str__(self):
        return f"Genome: {self.genome}\nMemory: {self.memory}\nWeighted Gene Sum: {self.weighted_gene_sum}\nShort-Term Memory: {self.short_term_memory}"


class Ball:
    def __init__(self, x, y, id, radius, color, speed):
        self.x = x
        self.y = y
        self.id = id
        self.radius = radius
        self.color = color
        self.speed = speed
        self.fitness = 100
        self.foodSaturation = 100
        self.age = 1
        self.last_print_time = 0
        self.last_reproduction_time = 0
        self.last_mutate_time = 0
        self.brain = Brain(Genome())

    def learn(self, item):
        self.brain.learn(item)

    def remember(self, item, value):
        self.brain.remember(item, value)

    def forget(self, item):
        self.brain.forget(item)

    def aging(self):
        if self.foodSaturation > 0:
            self.foodSaturation -= 0.01
        else:
            self.fitness -= 0.01
        self.age += 1

    def move(self):
        direction = self.brain.think({'x': self.x, 'y': self.y}, self.radius)
        self.x += self.speed[0] * math.cos(direction)
        self.y += self.speed[1] * math.sin(direction)

    def bounce(self, screen_width, screen_height):
        if self.x + self.radius > screen_width or self.x - self.radius < 0:
            self.speed[0] *= -1
        if self.y + self.radius > screen_height or self.y - self.radius < 0:
            self.speed[1] *= -1

    def collide(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < self.radius + other.radius:
            if isinstance(other, Food):
                self.learn("food")
                if other in self.brain.memory: self.brain.forget(other)
                self.fitness = (self.fitness + 5) if ((self.fitness + 5) < 100) else 100
                self.foodSaturation = (self.foodSaturation + 20) if ((self.foodSaturation + 20) < 100) else 100
                other.remove()

            if isinstance(other, Poison):
                self.learn("poison")
                self.fitness = (self.fitness - 20) if ((self.fitness - 20) > 0) else 0
                other.remove()
                
            if isinstance(other, CircleObstacle):
                self.learn("obstacle")
                self.speed[0] *= -1
                
            if isinstance(other, RectangleObstacle):
                self.learn("obstacle")
                self.speed[0] *= -1

    def update_color(self):
        if self.fitness < 25:
            self.color = (255, 0, 0)
        elif self.fitness < 50:
            self.color = (255, 165, 0)
        elif self.fitness < 75:
            self.color = (255, 210, 0)
        else:
            self.color = (0, 255, 0)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        
    def draw_health_bar(self):
        pygame.draw.rect(screen, (255, 0, 0), (self.x - self.radius, self.y - self.radius - 10, 2 * self.radius, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - self.radius, self.y - self.radius - 10, (self.fitness / 100) * 2 * self.radius, 5))

    def draw_hunger_bar(self):
        pygame.draw.rect(screen, (255, 255, 0), (self.x - self.radius, self.y + self.radius + 5, 2 * self.radius, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - self.radius, self.y + self.radius + 5, (self.foodSaturation / 100) * 2 * self.radius, 5))

    def check_mutation(self):
        if time.time() - self.last_mutate_time >= 10:
            self.brain.genome.mutate()
            self.last_mutate_time = time.time()

    def check_reproduction(self):
        if time.time() - self.last_reproduction_time >= 10:
            self.reproduce(random.random())
            self.last_reproduction_time = time.time()

    def reproduce(self, probability):
        if probability < 0.06:
            new_id = len(balls)
            new_radius = self.radius * 1.2
            new_color = self.mix_colors(self.color, random.choice(colors))
            new_speed = [self.speed[0] * 1.2, self.speed[1] * 1.2]
            new_ball = Ball(self.x, self.y, new_id, new_radius, new_color, new_speed)
            balls.append(new_ball)
            new_ball.brain.genome.genes = self.brain.genome.genes
            new_ball.brain.memory = self.brain.memory.copy()
            new_ball.brain.genome.mutate()
            if "food" in new_ball.brain.memory: new_ball.brain.memory["food"] /= 2
            if "poison" in new_ball.brain.memory: new_ball.brain.memory["poison"] /= 2

    def mix_colors(self, color1, color2):
        r = (color1[0] + color2[0]) / 2
        g = (color1[1] + color2[1]) / 2
        b = (color1[2] + color2[2]) / 2
        return (r, g, b)

    def mix_speeds(self, speed1, speed2):
        dx = speed1[0] + speed2[0]
        dy = speed1[1] + speed2[1]
        return [dx, dy]

    def checkIfAlive(self):
        if self.fitness <= 0:
            self.reproduce(random.random())
            return False
        return True

    def checkIfPrint(self, mouse_x, mouse_y):
        dx = self.x - mouse_x
        dy = self.y - mouse_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < self.radius:
            if math.sqrt((self.x - mouse_x) ** 2 + (
                    self.y - mouse_y) ** 2) < 100 and time.time() - self.last_print_time > 10:
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
        deprecated_memorys = []
        for key in self.brain.memory.keys():
            if isinstance(key, Food):
                if not (key in foods): deprecated_memorys.append(key)
        if len(deprecated_memorys) > 0:
            for deprecated_memory in deprecated_memorys:
                self.brain.forget(deprecated_memory)

    def update(self, mouse_x, mouse_y):
        for food in foods:
            self.collide(food)
        for poison in poisons:
            self.collide(poison)
        for obstacle in obstacles:
            self.collide(obstacle)
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


def main():
    last_print_time = 0
    ticks = 0

    def initializeSimulation():
        for i in range(random.randint(1, 1)):
            pos = {"x": 100, "y": 100}
            balls.append(Ball(random.randint(pos["x"], screen_width - 10), pos["y"], i, 15, colors[1], [0.1, 0.1]))
            pos["x"] += 40
        for i in range(random.randint(1, 4)):
            pos = {"x": random.randint(100, screen_width - 100), "y": random.randint(100, screen_height - 100)}
            obstacles.append(CircleObstacle(pos["x"], pos["y"], random.randint(20, 30), colors[2]))
        for i in range(random.randint(10, 60)):
            pos = {"x": random.randint(5, screen_width - 10), "y": random.randint(5, screen_height - 10)}
            foods.append(Food(pos["x"], pos["y"], 5, colors[1]))

    running = True
    while running:
        if len(balls) == 0: initializeSimulation()
        aliveBalls = [True for ball in balls]
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.fill((0, 0, 0))
        ballsKilled = 0
        ticks += 1

        if time.time() - last_print_time > 10:
            print(f"Number of alive balls: {len(aliveBalls)}")
            last_print_time = time.time()

        if ticks % 1000 == 0:
            pos = {"x": random.randint(5, screen_width - 10), "y": random.randint(5, screen_height - 10)}
            foods.append(Food(pos["x"], pos["y"], 5, colors[1]))

        if random.random() < 0.0001:
            pos = {"x": random.randint(5, screen_width - 10), "y": random.randint(5, screen_height - 10)}
            poisons.append(Poison(pos["x"], pos["y"], 5, colors[0]))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for i in range(len(balls)):
            balls[i].update(mouse_x, mouse_y)
            aliveBalls[i] = balls[i].checkIfAlive()

        for food in foods:
            food.draw()

        for poison in poisons:
            poison.draw()
            
        for obstacle in obstacles:
            obstacle.remove_items_within_obstacle()
            obstacle.draw()
           

        for i in range(len(aliveBalls)):
            if not aliveBalls[i]:
                del balls[i - ballsKilled]
                ballsKilled += 1

        for ball in balls:
            ball.check_reproduction()

        pygame.display.update()

    pygame.quit()


main()