import pygame
import os
import math
import sys
import neat

# --- EKRAN AYARLARI ---
EKRAN_GENISLIK = 1200
EKRAN_YUKSEKLIK = 800
GENERATION = 0

# --- RENKLER ---
RENK_CIM = (34, 139, 34)
RENK_ASFALT = (50, 50, 50)
RENK_CIZGI = (255, 255, 255)
RENK_ARABA = (230, 0, 0)
RENK_SAMPJYON = (0, 255, 0)
RENK_BITIS = (0, 255, 255)
RENK_ENGEL = (200, 200, 0)

pygame.init()
screen = pygame.display.set_mode((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
pygame.display.set_caption("Yapay Zeka - AKILLI BİTİŞ SİSTEMİ")
clock = pygame.time.Clock()

# --- HARİTA ---
track_surface = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
track_surface.fill(RENK_CIM)
collision_map = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
collision_map.fill((0, 0, 0))

# Pist
outer_rect = pygame.Rect(150, 150, 900, 500)
inner_rect = outer_rect.inflate(-240, -240)

pygame.draw.ellipse(track_surface, RENK_ASFALT, outer_rect)
pygame.draw.ellipse(track_surface, RENK_CIM, inner_rect)
pygame.draw.ellipse(track_surface, RENK_CIZGI, outer_rect, 5)
pygame.draw.ellipse(track_surface, RENK_CIZGI, inner_rect, 5)
pygame.draw.ellipse(collision_map, (255, 255, 255), outer_rect, 15)
pygame.draw.ellipse(collision_map, (255, 255, 255), inner_rect, 15)

# --- ENGELLER ---
engeller = [
    pygame.Rect(750, 140, 50, 50),
    pygame.Rect(450, 600, 50, 50)
]

for engel in engeller:
    pygame.draw.rect(track_surface, RENK_ENGEL, engel)
    pygame.draw.rect(collision_map, (255, 255, 255), engel)

# --- GÖRÜNMEZ ORTA SAHA VE BİTİŞ ---
# Ekrana çizdirmiyoruz, sadece mantıkta varlar
mid_checkpoint = pygame.Rect(550, 150, 100, 150)
finish_line = pygame.Rect(550, 500, 100, 150)

# Bitiş çizgisini görelim sadece (Mavi çizgi)
pygame.draw.rect(track_surface, RENK_BITIS, (595, 500, 10, 150))


class Araba:
    def __init__(self):
        self.surface = pygame.Surface((60, 35), pygame.SRCALPHA)
        pygame.draw.rect(self.surface, RENK_ARABA, (0, 0, 60, 35), border_radius=8)
        pygame.draw.rect(self.surface, (50, 50, 200), (45, 5, 10, 25), border_radius=3)

        self.sprite = self.surface
        start_pos = [600, 590]
        self.rect = self.surface.get_rect(center=start_pos)

        self.angle = 0
        self.speed = 0
        self.position = list(start_pos)
        self.radars = []
        self.center = [self.position[0] + 30, self.position[1] + 17.5]

        self.alive = True
        self.distance = 0
        self.time_spent = 0

        self.passed_mid = False
        self.is_finished = False

    def make_champion(self):
        self.surface = pygame.Surface((60, 35), pygame.SRCALPHA)
        pygame.draw.rect(self.surface, RENK_SAMPJYON, (0, 0, 60, 35), border_radius=8)
        self.sprite = self.surface
        self.is_finished = True
        self.speed = 0

    def check_radar(self, degree, map_image):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        while length < 600:
            length += 10
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

            if x >= EKRAN_GENISLIK or x < 0 or y >= EKRAN_YUKSEKLIK or y < 0:
                break

            try:
                if map_image.get_at((x, y)) == (255, 255, 255, 255):
                    break
            except:
                break

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def check_collision(self, map_image, track_surface):
        if self.time_spent < 10: return
        if self.is_finished: return

        self.alive = True

        for engel in engeller:
            if self.rect.colliderect(engel):
                self.alive = False
                return

        points = [
            (int(self.center[0] + math.cos(math.radians(360 - (self.angle + 45))) * 30),
             int(self.center[1] + math.sin(math.radians(360 - (self.angle + 45))) * 30)),
            (int(self.center[0] + math.cos(math.radians(360 - (self.angle + 135))) * 30),
             int(self.center[1] + math.sin(math.radians(360 - (self.angle + 135))) * 30)),
            (int(self.center[0] + math.cos(math.radians(360 - (self.angle + 225))) * 30),
             int(self.center[1] + math.sin(math.radians(360 - (self.angle + 225))) * 30)),
            (int(self.center[0] + math.cos(math.radians(360 - (self.angle + 315))) * 30),
             int(self.center[1] + math.sin(math.radians(360 - (self.angle + 315))) * 30))
        ]

        for p in points:
            if p[0] >= EKRAN_GENISLIK or p[0] < 0 or p[1] >= EKRAN_YUKSEKLIK or p[1] < 0:
                self.alive = False
                break
            try:
                if map_image.get_at(p) == (255, 255, 255, 255):
                    self.alive = False
                    break
                if track_surface.get_at(p) == RENK_CIM:
                    self.alive = False
                    break
            except:
                self.alive = False
                break

    def update(self, collision_map, track_surface):
        if self.is_finished:
            self.sprite = pygame.transform.rotate(self.surface, self.angle)
            self.rect = self.sprite.get_rect(center=self.position)
            return

        self.speed *= 0.96
        self.speed = max(0, min(self.speed, 15))

        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[1] += math.cos(math.radians(360 - (self.angle + 90))) * self.speed

        self.sprite = pygame.transform.rotate(self.surface, self.angle)
        self.rect = self.sprite.get_rect(center=self.position)
        self.center = [int(self.position[0]), int(self.position[1])]

        self.radars.clear()
        for d in [-120, -90, -45, 0, 45, 90, 120]:
            self.check_radar(d, collision_map)

        self.check_collision(collision_map, track_surface)
        self.distance += self.speed
        self.time_spent += 1

    def draw(self, screen):
        screen.blit(self.sprite, self.rect)

    def get_data(self):
        radars = self.radars
        return_values = [0, 0, 0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1]) / 600.0
        return return_values


def run_simulation(genomes, config):
    global GENERATION, screen, track_surface, collision_map
    GENERATION += 1

    start_time = pygame.time.get_ticks()
    time_limit = 40

    # --- YENİ EKLENTİ: ERKEN BİTİRME ZAMANLAYICISI ---
    finish_timer = 0
    someone_finished = False

    nets = []
    cars = []
    ge = []

    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        cars.append(Araba())
        genome.fitness = 0
        ge.append(genome)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        for i, car in enumerate(cars):
            if car.alive:
                if not car.is_finished:
                    output = nets[i].activate(car.get_data())
                    choice = output.index(max(output))
                    if choice == 0:
                        car.angle += 4
                    elif choice == 1:
                        car.angle -= 4
                    elif choice == 2:
                        car.speed -= 1
                    else:
                        car.speed += 1

                car.update(collision_map, track_surface)

        finish_counter = 0

        for i, car in enumerate(cars):
            if car.alive:
                if not car.is_finished:
                    ge[i].fitness += (car.speed * 0.1)

                    # 1.5 saniye sonra hızı 3'ten azsa ÖL.
                    if car.time_spent > 100 and car.speed < 3:
                        car.alive = False
                        ge[i].fitness -= 10

                        # ORTA SAHA (Görünmez)
                    if mid_checkpoint.colliderect(car.rect):
                        if not car.passed_mid:
                            car.passed_mid = True
                            ge[i].fitness += 2000

                    # BİTİŞ
                    if finish_line.colliderect(car.rect):
                        if car.passed_mid:
                            car.make_champion()
                            ge[i].fitness += 10000

                            # --- BİRİ BİTİRDİĞİNDE ZAMANLAYICIYI BAŞLAT ---
                            if not someone_finished:
                                someone_finished = True
                                finish_timer = pygame.time.get_ticks()  # Şu anki zamanı kaydet
                        else:
                            pass

            if car.is_finished:
                finish_counter += 1

        for i in range(len(cars) - 1, -1, -1):
            if not cars[i].alive:
                cars.pop(i)
                nets.pop(i)
                ge.pop(i)

        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) / 1000

        # --- BİTİŞ KONTROLÜ (DÜZELTİLDİ) ---
        should_end = False

        # 1. Herkes ölürse bitir
        if len(cars) == 0:
            should_end = True

        # 2. Maksimum süre dolarsa bitir
        if elapsed_time > time_limit:
            should_end = True

        # 3. BİRİ BİTİRDİYSE VE 3 SANİYE GEÇTİYSE BİTİR (Bekletme yok)
        if someone_finished:
            time_since_finish = (current_time - finish_timer) / 1000
            if time_since_finish > 3:  # 3 Saniye bekle ve kapat
                should_end = True

        if should_end:
            print(f"Nesil {GENERATION} bitti. Bitiş Çizgisini Geçen: {finish_counter}")
            break

        screen.blit(track_surface, (0, 0))

        for car in cars:
            car.draw(screen)
            if car == cars[0]:
                for radar in car.radars:
                    pygame.draw.line(screen, (0, 255, 0), car.center, radar[0], 1)
                    pygame.draw.circle(screen, (0, 255, 0), radar[0], 3)

        font = pygame.font.SysFont("Arial", 30)

        # Süre göstergesi (Biri bitirince kırmızı olsun)
        color = (255, 255, 255)
        if someone_finished:
            color = (255, 50, 50)  # Kırmızı

        time_text = font.render(f"Süre: {int(time_limit - elapsed_time)}", True, color)
        screen.blit(time_text, (550, 10))

        text = font.render(f"Gen: {GENERATION} Canlı: {len(cars)}", True, (255, 255, 255))
        screen.blit(text, (10, 10))

        finish_text = font.render(f"BİTİREN: {finish_counter}", True, (0, 255, 0))
        screen.blit(finish_text, (10, 50))

        pygame.display.flip()
        clock.tick(60)


def create_config_file(config_path):
    # Diktatör Modu Devam Ediyor
    config_content = """
[NEAT]
fitness_criterion = max
fitness_threshold = 100000
pop_size = 100
reset_on_extinction = False
no_fitness_termination = False

[DefaultGenome]
num_inputs = 7
num_outputs = 4
num_hidden = 4
feed_forward = True
compatibility_disjoint_coefficient = 1.0
compatibility_weight_coefficient = 0.5
conn_add_prob = 0.5
conn_delete_prob = 0.5
node_add_prob = 0.2
node_delete_prob = 0.2
activation_default = tanh
activation_mutate_rate = 0.1
activation_options = tanh
aggregation_default = sum
aggregation_mutate_rate = 0.0
aggregation_options = sum
bias_init_mean = 0.0
bias_init_stdev = 1.0
bias_max_value = 30.0
bias_min_value = -30.0
bias_mutate_power = 0.3
bias_mutate_rate = 0.7
bias_replace_rate = 0.1
bias_init_type = gaussian
enabled_default = True
enabled_mutate_rate = 0.01
enabled_rate_to_true_add = 0.0
enabled_rate_to_false_add = 0.0
initial_connection = full_direct
weight_init_mean = 0.0
weight_init_stdev = 1.0
weight_max_value = 30
weight_min_value = -30
weight_mutate_power = 0.3
weight_mutate_rate = 0.8
weight_replace_rate = 0.1
weight_init_type = gaussian
response_init_mean = 1.0
response_init_stdev = 0.0
response_max_value = 30.0
response_min_value = -30.0
response_mutate_power = 0.0
response_mutate_rate = 0.0
response_replace_rate = 0.0
response_init_type = gaussian
single_structural_mutation = False
structural_mutation_surer = default

[DefaultSpeciesSet]
compatibility_threshold = 3.0

[DefaultStagnation]
species_fitness_func = max
max_stagnation = 20
species_elitism = 2

[DefaultReproduction]
elitism = 10
survival_threshold = 0.1
min_species_size = 2
"""
    with open(config_path, "w") as f:
        f.write(config_content)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    create_config_file(config_path)
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(run_simulation, 1000)