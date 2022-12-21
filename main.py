import pygame
import math
import random
import time

pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Genetic Algorithem")

colors = [(255,0,0),(0,255,0),(0,0,255)]
balls = []
foods = []
poisons = []
aliveBalls = []

class Genome:
    def __init__(self):
        self.genes = [random.random() for _ in range(10)]
        
    def __len__(self):
        return len(self.genes)

    def __getitem__(self, index):
        return self.genes[index]

    def mutate(self):
        for i in range(len(self.genes)):
            if random.random() < 0.01:
                self.genes[i] += random.random()

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
                dx = chosen_food.x - position['x']
                dy = chosen_food.y - position['y']
                direction_food = math.atan2(dy, dx)
            else:
                chosen_food = random.choice(foods)
                dx = chosen_food.x - position['x']
                dy = chosen_food.y - position['y']
                direction_food = math.atan2(dy, dx)
                self.remember(chosen_food, chosen_food)
            direction = direction_food if food_memory * self.weighted_gene_sum > random.random() else direction
        return direction

    def avoid_poison(self, direction, poison_memory, position, radius):
        has_to_avoid_poison = False
        for poison in poisons:
            if self.is_surrounded_by_poison(poison, position, radius):
                has_to_avoid_poison = True
                break
        if has_to_avoid_poison and (poison_memory * self.weighted_gene_sum) > random.random():
            for food in foods:
                if food in self.memory: self.forget(self.memory[food])
            direction = self.seek_food(self.calculate_direction(self.genome), self.memory["food"], position) if "food" in self.memory else self.calculate_direction(self.genome)
        return direction

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
    
    def is_surrounded_by_poison(self, poison, position, radius):
        dx = position['x'] - poison.x
        dy = position['y'] - poison.y
        distance_to_poison = math.sqrt(dx ** 2 + dy ** 2)

        if distance_to_poison <= radius + poison.radius:
            return True
        return False

class Poison:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
            
    def remove(self):
        pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), self.radius)
        poisons.remove(self)
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

class Food:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
            
    def remove(self):
        pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), self.radius)
        foods.remove(self)
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

class Ball:
    def __init__(self, x, y, id, radius, color, speed):
        self.x = x
        self.y = y
        self.id = id
        self.radius = radius
        self.color = color
        self.speed = speed
        self.fitness = 100
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
        if self.age >= 100: self.fitness -= 0.01
        self.age += 1
            
    def move(self):
        direction = self.brain.think({'x':self.x,'y':self.y}, self.radius)
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
                self.fitness = (self.fitness + 20) if ((self.fitness + 20) < 100) else 100
                other.remove()
                
            if isinstance(other, Poison):
                self.learn("poison")
                self.fitness = (self.fitness - 40) if ((self.fitness - 40) > 0) else 0
                other.remove()
                
    def update_color(self):
        if self.fitness < 25:
            self.color = (255, 0, 0)
        elif self.fitness < 50:
            self.color = (255, 165, 0)
        elif self.fitness < 75:
            self.color = (255, 210, 0)
        else:
            self.color = (0, 255, 0)
            
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
    
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
            new_ball.brain.memory = self.brain.memory
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
            if math.sqrt((self.x - mouse_x) ** 2 + (self.y - mouse_y) ** 2) < 100 and time.time() - self.last_print_time > 10:
                print("id:", self.id)
                print("x:", self.x)
                print("y:", self.y)
                print("radius:", self.radius)
                print("color:", self.color)
                print("speed:", self.speed)
                print("fitness:", self.fitness)
                print("age:", self.age/1000)
                print("Gehirn:", self.brain.memory.items())
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
        self.move()
        self.bounce(screen_width, screen_height)
        self.aging()
        self.update_color()
        self.checkIfPrint(mouse_x, mouse_y)
        self.check_mutation()
        self.draw(screen)
        self.checkMemory()

def main():
    last_print_time = 0
    ticks = 0
        
    def initializeSimulation():
        pos = {"x": 100, "y": 100}
        for i in range(random.randint(10, 20)):
            balls.append(Ball(pos["x"], pos["y"], i, 15, colors[1], [0.1, 0.1]))
            pos["x"] += 40
        for i in range(random.randint(10, 40)):
            pos = {"x": random.randint(5, screen_width-10), "y": random.randint(5, screen_height-10)}
            foods.append(Food(pos["x"], pos["y"],5,colors[1]))

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
            pos = {"x": random.randint(5, screen_width-10), "y": random.randint(5, screen_height-10)}
            foods.append(Food(pos["x"], pos["y"],5,colors[1]))
            
        if random.random() < 0.0001:
            pos = {"x": random.randint(5, screen_width-10), "y": random.randint(5, screen_height-10)}
            poisons.append(Poison(pos["x"], pos["y"], 5, colors[0]))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        for i in range(len(balls)):
            balls[i].update(mouse_x, mouse_y)
            aliveBalls[i] = balls[i].checkIfAlive()
            
        for food in foods:
            food.draw(screen)
        
        for poison in poisons:
            poison.draw(screen)
            
        for i in range(len(aliveBalls)):
            if not aliveBalls[i]:
                del balls[i-ballsKilled]
                ballsKilled += 1
        
        for ball in balls:
            ball.check_reproduction()
                  
        pygame.display.update()

    pygame.quit()
    
main()