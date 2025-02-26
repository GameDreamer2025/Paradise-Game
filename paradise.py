from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from panda3d.core import TextNode, loadPrcFileData, NodePath, ParticleEffect, TextureStage
import random

# UTF-8 encoding setup
loadPrcFileData("", "text-encoding utf8")

class ParadiseGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setBackgroundColor(245/255, 245/255, 220/255)  # Default beige
        
        # Load font with fallback
        self.font = self.loader.loadFont("cmss12")
        if not self.font.isValid():
            self.font = self.loader.loadFont("Arial")
            if not self.font.isValid():
                self.font = None
        
        self.worlds = {  # Структура миров остаётся без изменений для краткости
            "1": {"name": "Sea", "monster": "Flaming Phoenix", "locations": {...}},
            "2": {"name": "Forest", "monster": "Icy Serpent", "locations": {...}},
            "3": {"name": "Mountains", "monster": "Sandy Colossus", "locations": {...}},
            "4": {"name": "Desert", "monster": "Water Chimera", "locations": {...}},
            "5": {"name": "Cosmos", "monster": "Dark Void", "locations": {...}}
        }
        
        self.title = self.create_text("I will create your paradise.\nChoose wisely.", (0, 0.8))
        self.question = self.create_text("", (0, 0.4))
        self.buttons = []
        self.current_question = 0
        self.answers = []
        self.choices = [
            ("What place do you love?", ["Sea", "Forest", "Mountains", "Desert", "Cosmos"]),
            ("What color do you prefer?", ["Blue", "Green", "Red", "Yellow", "Purple"]),
            ("What mood do you enjoy?", ["Silence", "Noise", "Rain", "Sun", "Wind"]),
            ("What makes a place alive?", ["Birds", "People", "Plants", "Water", "Light"])
        ]
        self.show_question()
        self.effects_node = None  # Для эффектов

    def create_text(self, text, pos, scale=0.07, fg=(0, 0, 0, 1)):
        return OnscreenText(text=text, pos=pos, scale=scale, fg=fg, align=TextNode.ACenter, font=self.font)

    def create_button(self, text, pos, command, extra_args=None, scale=0.1):
        return DirectButton(text=text, scale=scale, pos=pos, command=command, extraArgs=extra_args or [],
                            text_scale=0.8, text_fg=(1, 1, 1, 1), frameColor=(0, 0, 0, 1), text_font=self.font)

    def show_question(self):
        if self.current_question < len(self.choices):
            q_text, options = self.choices[self.current_question]
            self.question.setText(q_text)
            self.clear_buttons()
            for i, opt in enumerate(options):
                self.buttons.append(self.create_button(opt, (-0.8 + i * 0.4, 0, 0), self.answer, [opt]))
        else:
            self.start_game()

    def answer(self, choice):
        self.answers.append(choice)
        self.current_question += 1
        self.show_question()

    def clear_buttons(self):
        for btn in self.buttons:
            btn.destroy()
        self.buttons = []

    def clear_effects(self):
        if self.effects_node:
            self.effects_node.removeNode()
        self.effects_node = NodePath("effects")
        self.effects_node.reparentTo(self.render2d)

    def add_rain(self):
        rain = ParticleEffect()
        rain.loadConfig("rain.ptf")  # Файл частиц (нужен отдельный файл или конфиг)
        rain.start(parent=self.effects_node, renderParent=self.render2d)
        rain.setPos(0, 0, 1)  # Капли сверху экрана

    def add_wind(self):
        wind = ParticleEffect()
        wind.loadConfig("wind.ptf")  # Песок или листья
        wind.start(parent=self.effects_node, renderParent=self.render2d)
        wind.setPos(-1, 0, 0)  # Слева направо

    def add_sun(self):
        sun = self.loader.loadModel("models/sphere")
        sun.reparentTo(self.effects_node)
        sun.setScale(0.2)
        sun.setPos(0.8, 0, 0.8)
        sun.setColor(1, 1, 0, 0.5)  # Жёлтое свечение

    def add_birds(self):
        for _ in range(3):  # 3 птицы
            bird = self.loader.loadModel("models/plane")
            bird.reparentTo(self.effects_node)
            bird.setScale(0.05)
            bird.setPos(random.uniform(-1, 1), 0, random.uniform(0, 1))
            self.taskMgr.add(self.move_bird, "move_bird", extraArgs=[bird])

    def move_bird(self, bird):
        x = bird.getX() + 0.01
        if x > 1:
            x = -1
        bird.setPos(x, 0, bird.getZ())
        return True

    def add_people(self):
        person = self.loader.loadModel("models/box")
        person.reparentTo(self.effects_node)
        person.setScale(0.1, 0.1, 0.2)
        person.setPos(0, 0, -0.8)
        person.setColor(0.5, 0.3, 0.2, 1)

    def add_plants(self):
        plant = self.loader.loadModel("models/plant")
        plant.reparentTo(self.effects_node)
        plant.setScale(0.2)
        plant.setPos(-0.5, 0, -0.8)
        plant.setColor(0, 1, 0, 1)

    def add_water(self):
        water = self.loader.loadModel("models/plane")
        water.reparentTo(self.effects_node)
        water.setScale(1, 1, 0.1)
        water.setPos(0, 0, -0.9)
        water.setColor(0, 0, 1, 0.5)

    def add_light(self):
        for _ in range(5):  # 5 огоньков
            light = self.loader.loadModel("models/sphere")
            light.reparentTo(self.effects_node)
            light.setScale(0.02)
            light.setPos(random.uniform(-1, 1), 0, random.uniform(-1, 1))
            light.setColor(1, 1, 0, 0.7)

    def start_game(self):
        self.clear_buttons()
        self.title.destroy()
        self.question.destroy()
        place = str(self.choices[0][1].index(self.answers[0]) + 1)
        if place in self.worlds:
            self.world = self.worlds[place]
            self.color = self.answers[1].lower()
            self.mood = self.answers[2].lower()
            self.life = self.answers[3].lower()
            
            # Установка цвета фона
            colors = {"blue": (0, 0, 1, 1), "green": (0, 1, 0, 1), "red": (1, 0, 0, 1), "yellow": (1, 1, 0, 1), "purple": (0.5, 0, 0.5, 1)}
            self.setBackgroundColor(*colors.get(self.color, (245/255, 245/255, 220/255, 1)))
            
            # Эффекты для настроения
            self.clear_effects()
            if self.mood == "rain":
                self.add_rain()
            elif self.mood == "wind":
                self.add_wind()
            elif self.mood == "sun":
                self.add_sun()
            elif self.mood == "noise":
                self.taskMgr.add(self.noise_effect, "noise_effect")
            # Silence оставляем без эффектов
            
            # Эффекты для жизни
            if self.life == "birds":
                self.add_birds()
            elif self.life == "people":
                self.add_people()
            elif self.life == "plants":
                self.add_plants()
            elif self.life == "water":
                self.add_water()
            elif self.life == "light":
                self.add_light()
            
            self.intro = self.create_text(f"Your world is ready.\nIt’s a {self.color} {self.world['name'].lower()} under {self.mood}.\n{self.life} brings it to life.", (0, 0.4))
            self.loc_prompt = self.create_text("Where to go?", (0, 0.2))
            self.visited = []
            self.hints = {}
            self.show_locations()

    def noise_effect(self, task):
        self.setBackgroundColor(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1)
        return task.again

    # Остальные методы остаются без изменений для краткости

# Start the game
game = ParadiseGame()
game.run()
