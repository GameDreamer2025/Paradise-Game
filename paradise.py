from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from panda3d.core import TextNode, loadPrcFileData
import random

# UTF-8 encoding setup
loadPrcFileData("", "text-encoding utf8")

class ParadiseGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setBackgroundColor(245/255, 245/255, 220/255)  # Default beige
        
        # Load a reliable font with fallback
        self.font = self.loader.loadFont("cmss12")  # Comic Sans-like, often available
        if not self.font.isValid():
            self.font = self.loader.loadFont("Arial")  # Fallback to Arial
            if not self.font.isValid():
                self.font = None  # Use built-in if all fails
        
        self.worlds = {  # Миры остаются без изменений для краткости
            "1": {
                "name": "Sea", "monster": "Flaming Phoenix",
                "locations": {
                    "1": {"name": "Singers' Bay", "npc": "Old Fisherman", "desc": "A red sea under the sun, boats jingle, the old fisherman sings.",
                          "riddles": [("Is the sea blue when the sun shines?", "Yes", [("Yes", True), ("No", False)]), ...],
                          "hint": "Fire fears the storm, shout ‘Storm’ three times to calm it.", "action_word": "storm", "action_count": 3,
                          "success": "The storm extinguishes the phoenix in the bay!", "fail": "The storm is weak, the bay burns."},
                    # Остальные локации опущены для краткости
                },
                "wormhole": "Panicked Sailor", "wormhole_cry": "Save us! Fire comes from the hole!",
                "super_final": "You banished the phoenix forever.\nThe sea shines brighter.\nThe AI whispers: ‘You became its guardian.’"
            },
            # Другие миры аналогично опущены
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

    # Универсальная функция для текста
    def create_text(self, text, pos, scale=0.07, fg=(0, 0, 0, 1)):
        return OnscreenText(text=text, pos=pos, scale=scale, fg=fg, align=TextNode.ACenter, font=self.font)

    # Универсальная функция для кнопок
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
            # Меняем цвет фона в зависимости от выбора
            colors = {"blue": (0, 0, 1, 1), "green": (0, 1, 0, 1), "red": (1, 0, 0, 1), "yellow": (1, 1, 0, 1), "purple": (0.5, 0, 0.5, 1)}
            self.setBackgroundColor(*colors.get(self.color, (245/255, 245/255, 220/255, 1)))
            self.intro = self.create_text(f"Your world is ready.\nIt’s a {self.color} {self.world['name'].lower()} under {self.mood}.\n{self.life} brings it to life.", (0, 0.4))
            self.loc_prompt = self.create_text("Where to go?", (0, 0.2))
            self.visited = []
            self.hints = {}
            self.show_locations()

    def show_locations(self):
        self.clear_buttons()
        remaining = [loc_id for loc_id in self.world["locations"] if loc_id not in self.visited]
        if remaining:
            for i, loc_id in enumerate(remaining):
                loc_data = self.world["locations"][loc_id]
                self.buttons.append(self.create_button(loc_data["name"], (-0.6 + i * 0.6, 0, 0), self.visit_location, [loc_id]))

    def visit_location(self, loc_id):
        self.clear_buttons()
        if hasattr(self, "intro"):
            self.intro.destroy()
            self.loc_prompt.destroy()
        loc_data = self.world["locations"][loc_id]
        self.current_loc = loc_id
        self.loc_text = self.create_text(f"You are in {loc_data['name']}.\n{loc_data['desc']}", (0, 0.6))
        # Случайное событие (20% шанс)
        if random.random() < 0.2:
            self.npc_text = self.create_text(f"{loc_data['npc']} says:\n‘Beware, the {self.world['monster']} stirs nearby!’", (0, 0.4))
        else:
            self.npc_text = self.create_text(f"{loc_data['npc']} says:\n‘Answer my riddles, and I’ll help.’", (0, 0.4))
        self.riddle_index = 0
        self.correct = 0
        self.show_riddle()

    def show_riddle(self):
        self.clear_buttons()
        if self.riddle_index < len(self.world["locations"][self.current_loc]["riddles"]):
            riddle, _, options = self.world["locations"][self.current_loc]["riddles"][self.riddle_index]
            if hasattr(self, "riddle_text"):
                self.riddle_text.destroy()
            self.riddle_text = self.create_text(riddle, (0, 0.2))
            for i, (opt, correct) in enumerate(options):
                self.buttons.append(self.create_button(opt, (-0.4 + i * 0.4, 0, 0), self.check_riddle, [correct]))
        else:
            self.finish_location()

    def check_riddle(self, correct):
        if correct:
            self.correct += 1
        self.riddle_index += 1
        self.show_riddle()

    def finish_location(self):
        self.loc_text.destroy()
        self.npc_text.destroy()
        loc_data = self.world["locations"][self.current_loc]
        if self.correct >= 4:  # Снижено с 5 до 4
            self.hint_text = self.create_text(f"{loc_data['npc']}:\n‘{loc_data['hint']}’", (0, 0.4))
            self.hints[self.current_loc] = (loc_data["action_word"], loc_data["action_count"])
        else:
            self.hint_text = self.create_text(f"{loc_data['npc']}:\n‘You’re not ready, think again.’", (0, 0.4))
        self.visited.append(self.current_loc)
        self.next_btn = self.create_button("Next", (0, 0), self.check_progress)

    # Остальные методы (check_progress, start_wormhole и т.д.) остаются почти без изменений, только с использованием create_button/create_text

    def start_wormhole(self):
        self.wormhole_text = self.create_text(f"A Wormhole opens in your world.\n{self.world['wormhole']} cries:\n‘{self.world['wormhole_cry']}’\nTime to fight the {self.world['monster']}.", (0, 0.4))
        self.fight_btn = self.create_button("Fight", (0, 0), self.show_fight_locations)
        self.successes = 0
        self.attempted = []

    def show_fight_locations(self):
        self.clear_buttons()
        if hasattr(self, "wormhole_text"):
            self.wormhole_text.destroy()
        self.fight_prompt = self.create_text(f"Where to fight the {self.world['monster']}?", (0, 0.4))
        remaining = [loc_id for loc_id in self.world["locations"] if loc_id not in self.attempted]
        for i, loc_id in enumerate(remaining):
            loc_data = self.world["locations"][loc_id]
            self.buttons.append(self.create_button(loc_data["name"], (-0.4 + i * 0.6, 0, 0.2), self.fight_in_location, [loc_id]))
        if self.attempted:
            self.end_btn = self.create_button("End", (0, 0), self.end_game)

    # Оставшиеся методы опущены для краткости, но они тоже используют новые функции

# Start the game
game = ParadiseGame()
game.run()
