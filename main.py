import asyncio
import pygame
from pathlib import Path
import time 
import random

BASE_DIR = Path(__file__).parent
ASSET_DIR = BASE_DIR / "assets"
WIDTH, HEIGHT = 900, 600
TEXT_DIR = BASE_DIR / "text"


def story(filename):
    return (TEXT_DIR / filename).read_text(encoding="utf-8").strip()

class Monster:
    def __init__(self, name, health, attack, description, weakness, resistance):
        self.name = name
        self.health = health
        self.attack = attack
        self.description = description
        self.weakness = weakness
        self.resistance = resistance

class Weapon:
    def __init__(self, name, damage, element, description):
        self.name = name
        self.damage = damage
        self.description = description
        self.element = element

class Item:
    def __init__(self, name, description, takeability):
        self.name = name
        self.description = description
        self.takeability = takeability

class Person:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        

class Room:
    def __init__(self, name, description, music=None, enter_sound=None,):
        self.name = name
        self.description = description
        self.neighbors = {}
        self.enter_sound = enter_sound
        self.monsters = []
        self.items = []
        self.weapon = None
        self.people = []
        self.music = music

    def add_neighbor(self, direction, room):
        self.neighbors[direction] = room

    def get_neighbor(self, direction):
        return self.neighbors.get(direction)

    def list_exits(self):
        return ", ".join(self.neighbors.keys())

class TextAdventure:
    def __init__(self):
        self.current_input = ""
        self.game_over = False
        self.inv = []
        self.equip_inv = []
        self.room_visited = []
        self.exposition = True
        self.richard_talk = 1
        self.gravekeeper_talk = 1
        self.current_music = None
        self.music_started = False
        self.music_muted = False
        self.default_music = "Background.wav.ogg"
        self.grave_music = "Dark Spooky Ambient.wav.ogg"
        self.messages = []
        self.dialogue = []
        self.dialogue_active = False
        self.dialogue_index = 0
        self.dialogue_callback = None
        self.choice_active = False
        self.choice_callback = None
        self.choice_options = []
        self.bell_sequence = []
        self.correct_bell_sequence = [2, 3, 1]
        self.bell_puzzle_solved = False
        self.shards_got = 0


        self.sounds = {
                    "move": pygame.mixer.Sound(ASSET_DIR / "move.wav.ogg"),
                    "take": pygame.mixer.Sound(ASSET_DIR / "take.wav.ogg"),
                    "danger": pygame.mixer.Sound(ASSET_DIR / "danger.mp3.ogg"),
                    "kill": pygame.mixer.Sound(ASSET_DIR / "enemy_death.wav.ogg"),
                    "equip": pygame.mixer.Sound(ASSET_DIR / "equip.mp3.ogg"),
                    "hurt": pygame.mixer.Sound(ASSET_DIR / "bite.mp3.ogg"),
                    "heal": pygame.mixer.Sound(ASSET_DIR / "deltarune-heal.mp3.ogg"), 
                    "crash": pygame.mixer.Sound(ASSET_DIR / "Meteor.wav.ogg"),}





        

        # Enemies (name, health, attack, description, weakness, resistance) #
        rat = Monster("rat", 2, 1, "a very abnormally sized rat", "", "")
        shadow_creature = Monster("creature", 6, 2, "a creature that seems to be made of only shadow", "psychic", "force")
        skeleton = Monster("skeleton", 5, 1, "A skeleton made of very old bones, the eyes cast a hateful gaze towards you.", "psychic", "dark")
        skeleton_king = Monster("king", 10, 3, "The king of the skeleton hierarchy down here, its eyes are burning flames of rage", "psychic", "dark")
        evil_richard = Monster("richard", 15, 2, "The evil spirit of the mountain, pretending to be richard to confuse you.", "force", "dark")

        # Items (name, description, takeability)# 
        nail = Item("nail", "a rusty nail about 4 inches long", True)
        book_Gailor = Item("red book", 'a red book titled "Sewanee and Its History of Meteors". The book is very old, having been repaired in multiple places', True)
        book_E1 = Item("blue-green book", 'a blue-green book titled "Examining and You! - Examining for Dummies Vol 1"', True)
        keys = Item("keys", "a ring of keys on the ground, looks familiar.", True)
        bandages = Item("bandages", "a pack of bandages with a roll of decent quality guaze", True)
        document = Item("document", "a faded, old document on the table here.", True)
        note = Item("note", "a note on the ground here,", True)
        richard_shovel = Item("shovel", "the shovel used by the false richard, take it quick", True)
        
        grave_a = Item("rusty grave","a rusty grave which plaque has long since rusted over", False)
        grave_b = Item("mossy grave", "a mossy grave, covered with a deep green moss", False)
        grave_c = Item("cross grave", "a large cross grave. It has fresh flowers circled in front of it", False)

        the_bells = Item("three bells", "a set of three golden bells here, each with a different symbol. 1: Spiral, 2: Sunrise, 3: Sword", False)
        alter = Item("alter", "an old, wooden alter with a red and gold cloth across it", False)
        window = Item("window", "a window of stained glass much older than the ones that surround it.", False)
        tablet = Item("tablet", "a stone tablet in the back of the bell tower.", True)

        self.gold_shard = Item("gold shard", "a golden shard with a warm glow", True )
        self.white_shard = Item("white shard", "A white shard with a soft glow.", True)
        self.dark_shard = Item("black shard", "A black shard with a ghostly glow.", True)
        self.red_shard = Item("red shard", "a red shard with a flaming glow", True)
        self.document2 = Item("yellow document", "a yellow colored document at the bottom of the box.", True)

        self.horse_key = Item("horse key", "a key with a horse attached on the chain", True)
        self.grave_key = Item("skull key", "the key to the basement door, it has the shape of a skull on top, eyes of gold.", True)

        car = Item("car", "a 1997 Nissan pickup here, you got it from your grandpa after you moved out.", False)
        door_GR = Item("locked door", "a locked door here, it has the symbol of a horse on it", False)
        self.box = Item("box", "a sealed wooden crate, one could very easily break it with a heavy object", False)
        shard_door = Item("Gilded door", "a door lined with what looks like gold, it has 4 crystal spheres at the top.", False)
        
        # Weapons (name, damage, type, description)
        self.shard = Weapon("shard", 3, "psychic", "a sleek shard of a deep purple crystal")
        self.axe = Weapon("axe", 4, "force", "an old axe with the paint faded and peeling" )


        # People (name, description) #
        self.richard = Person("Richard", "Your coworker who you met when you started this project, seems to be a very chill person," \
        " who notices a lot about everyone")
        self.gravekeeper = Person("Gravekeeper", "a mysterious old man charged with guarding the graveyard")
        


        # Rooms (name, description, music, sound) #
        self.CS_west = Room("Construction Site-West", "the west side of the construction site you work at")
        self.CS_east = Room("Construction Site-East", "the east side of the construction site you work at")
        self.CS_hole = Room("Construction Site-Hole", "the giant hole dug in the middle of the construction site")

        self.Gailor = Room('Gailor Hall', "the former dorm and dining hall of Sewanee, now one of the main acedemic buildings on campus")
        self.Gailor_downstairs = Room("Gailor Hall-downstairs","the downstairs area of Gailor Hall")
        self.Gailor_left = Room("Gailor Bathroom","the downstairs bathroom of Gailor")
        self.Gailor_right = Room("Right Hallway", "the downstairs right side of Gailor, there are offices here, but all seem to be locked")
        self.Gailor_auditorium = Room("Gailor Auditorium", "a small auditorium in the downstairs of Gailor Hall")
        self.Gailor_locked_room = Room("Gailor Office", "an office that has not been used by anyone in a long time")

        self.Playground = Room("Playground", "the empty playground near the parking lot")

        self.Forest = Room("Forest", "the dense forest west of sewanee. You can see a building in the distance, but its too shrouded to see clearly")
        self.forest_shack = Room("Forest Shack", "a concrete shack with a rusted, metal roof in the middle of the forest")
        self.forest_shack_inside = Room("Inside Shack", "the inside of the shack. The air is cold and damp")

        self.Chapel_hall = Room("Hall of All Saints Chapel", "The entry hall, the windows are full of unique portraits")
        self.Chapel_sanctum = Room("All Saints Chapel", "the sanctum of the chapel. A mysterious air hangs around every room inside")
        self.Chapel_bells = Room("All Saints Chapel Bell Tower", "The top of the bell tower, over 100 feet tall")

        self.Library = Room("Library", "the multi story Sewanee library")
        self.Library_basement = Room("Basement", "the basement of the Sewanee library")

        self.Quad = Room("Quad", "a clearing of trees and benches next to the Chapel")

        self.Graveyard = Room("Graveyard","the Sewanee graveyard, its been in use for over 200 years, likely many more than that", self.grave_music )
        self.Graveyard_north = Room("North Graveyard", "the north side of the graveyard", self.grave_music)

        self.crash_site = Room("Crash Site-Entrance", "the entrance to the santuary that is the ancient crash site. ONLY GO FORWARD IF YOU ARE PREPARED")
        self.crash_sanctuary = Room("Crash Site-Santuary", "the santuary of the ancient crash site. Surrounded by lush, purple trees")

        self.Catacombs_entrance = Room("Catacombs Entrance", "the dark, damp stone entrance of the Sewanee underground")
        self.Catacombs_a = Room("Catacombs", "the Catacombs, you are going the right way")
        self.Catacombs_b = Room("Catacombs", "the Catacombs, you are going the right way")
        self.Catacombs_c = Room("Catacombs", "the Catacombs, you are going the right way")
        self.Catacombs_d = Room("Catacombs", "the Catacombs, you are going the right way")
        self.Catacombs_e = Room("Catacombs", "the Catacombs, you are going the right way")
        self.Catacombs_1 = Room("Catacombs", "the Catacombs, This is not the right way")
        self.Catacombs_2 = Room("Catacombs", "the Catacombs, This is not the right way")
        self.Catacombs_3 = Room("Catacombs", "the Catacombs, This is not the right way")
        self.Catacombs_4 = Room("Catacombs", "the Catacombs, This is not the right way")
        self.Catacombs_5 = Room("Catacombs", "the Catacombs, This is not the right way")
        self.Catacombs_final = Room("Catacombs Grand Chamber", "The final chamber of the Catacombs")






        self.Parking_lot = Room("Parking Lot-Zone J","the parking lot, this is where you parked your car")

        # Room Connections #

        self.CS_west.add_neighbor("east", self.CS_east)
        self.CS_east.add_neighbor("west", self.CS_west)
        self.CS_east.add_neighbor("down", self.CS_hole)
        self.CS_west.add_neighbor("south", self.Parking_lot)
        self.CS_hole.add_neighbor("up", self.CS_east)
        self.Parking_lot.add_neighbor("north", self.CS_west)

    


        # Room Enemies #
        self.CS_hole.monsters.append(rat)
        self.forest_shack_inside.monsters.append(shadow_creature)
        self.forest_shack_inside.monsters.append(Monster("creature", 7, 2, "a creature that seems to be made of only shadow","psychic", "force"))
        self.Catacombs_1.monsters.append(skeleton)
        self.Catacombs_2.monsters.append(Monster("skeleton", 5, 1, "A skeleton made of very old bones, the eyes cast a hateful gaze towards you.", "psychic", "dark"))
        self.Catacombs_3.monsters.append(Monster("skeleton", 5, 1, "A skeleton made of very old bones, the eyes cast a hateful gaze towards you.", "psychic", "dark"))
        self.Catacombs_4.monsters.append(Monster("skeleton", 5, 1, "A skeleton made of very old bones, the eyes cast a hateful gaze towards you.", "psychic", "dark"))
        self.Catacombs_5.monsters.append(Monster("skeleton", 5, 1, "A skeleton made of very old bones, the eyes cast a hateful gaze towards you.", "psychic", "dark"))
        self.Catacombs_final.monsters.append(skeleton_king)
        self.crash_sanctuary.monsters.append(evil_richard)
    
    
        

        # Room Items #
        self.CS_east.items.append(nail)
        self.Gailor.items.append(book_Gailor)
        self.CS_hole.items.append(keys)
        self.Parking_lot.items.append(car)
        self.Gailor_left.items.append(bandages)
        self.Gailor_auditorium.items.append(book_E1)
        self.Gailor_right.items.append(door_GR)
        self.Gailor_locked_room.items.append(document)
        self.forest_shack_inside.items.append(self.box)
        self.Graveyard_north.items.append(grave_a)
        self.Graveyard_north.items.append(grave_b)
        self.Graveyard_north.items.append(grave_c)
        self.Chapel_bells.items.append(the_bells)
        self.Chapel_bells.items.append(tablet)
        self.Chapel_hall.items.append(window)
        self.Chapel_sanctum.items.append(alter)
        self.Library_basement.items.append(shard_door)
        self.Library_basement.items.append(note)
        self.Catacombs_final.items.append(self.red_shard)
        self.crash_sanctuary.items.append(richard_shovel)
    
        

        # Room People #
        self.CS_west.people.append(self.richard)
        self.Graveyard.people.append(self.gravekeeper)
        

        # Room Weapons #
        self.Gailor_locked_room.weapon = self.axe

        # Stats #
        self.current_room = self.Parking_lot
        self.element_read = 0
        self.monster_prof = 0
        self.best_weapon_damage = 100
        self.current_weapon = "fist"
        self.weapon_element = "force"
        self.health = 10
        self.current_health = 10
        self.inv.append(keys)
        self.equip_inv.append(self.axe)






    def say(self, *messages, sep=" "):
        self.messages.append(sep.join(map(str, messages)))

    def play_sound(self, name):
            if name in self.sounds:
                self.sounds[name].play()

    def start_music(self):
        self.music_started = True
        self.update_music()
    
    def update_music(self):

        filename = self.current_room.music or self.default_music
        if not self.music_started or filename == self.current_music:
            return
        pygame.mixer.music.load(str(ASSET_DIR / filename))
        pygame.mixer.music.set_volume(0.0 if self.music_muted else 0.25)
        pygame.mixer.music.play(-1)  # Repeat indefinitely; the game keeps running.
        self.current_music = filename

    def toggle_music(self):
        self.music_muted = not self.music_muted
        pygame.mixer.music.set_volume(0.0 if self.music_muted else 0.25)
    
    def update_map(self):

        self.CS_west.add_neighbor("west", self.Gailor)
        self.CS_west.add_neighbor("north", self.Library)

        self.Gailor.add_neighbor("east", self.CS_west)
        self.Gailor.add_neighbor("southwest", self.Playground)
        self.Gailor.add_neighbor("west", self.Forest)
        self.Gailor.add_neighbor("northwest", self.Chapel_hall)
        self.Gailor.add_neighbor("down", self.Gailor_downstairs)
        self.Gailor_downstairs.add_neighbor("up", self.Gailor)
        self.Gailor_downstairs.add_neighbor("left", self.Gailor_left)
        self.Gailor_downstairs.add_neighbor("right", self.Gailor_right)
        self.Gailor_downstairs.add_neighbor("forward", self.Gailor_auditorium)
        self.Gailor_auditorium.add_neighbor("back", self.Gailor_downstairs)
        self.Gailor_left.add_neighbor("right", self.Gailor_downstairs)
        self.Gailor_right.add_neighbor("left",self.Gailor_downstairs)

        self.Playground.add_neighbor("northeast", self.Gailor)

        self.Forest.add_neighbor("east", self.Gailor)
        self.Forest.add_neighbor("northeast", self.Chapel_hall)
        self.forest_shack.add_neighbor("in", self.forest_shack_inside)
        self.forest_shack_inside.add_neighbor("out", self.forest_shack)

        self.Chapel_hall.add_neighbor("southwest", self.Forest)
        self.Chapel_hall.add_neighbor("southeast", self.Gailor)
        self.Chapel_hall.add_neighbor("northwest", self.Quad)
        self.Chapel_hall.add_neighbor("north", self.Chapel_sanctum)
        self.Chapel_sanctum.add_neighbor("south", self.Chapel_hall)
        self.Chapel_sanctum.add_neighbor("up", self.Chapel_bells)
        self.Chapel_bells.add_neighbor("down", self.Chapel_sanctum)

        self.Quad.add_neighbor("southeast", self.Chapel_hall)
        self.Quad.add_neighbor("east", self.Library)

        self.Library.add_neighbor("west", self.Quad)
        self.Library.add_neighbor("east", self.Graveyard)
        self.Library.add_neighbor("south", self.CS_west)
        self.Library.add_neighbor("down", self.Library_basement)
        self.Library_basement.add_neighbor("up", self.Library)

        self.Graveyard.add_neighbor("west", self.Library)
        self.Graveyard.add_neighbor("north", self.Graveyard_north)
        self.Graveyard_north.add_neighbor("south", self.Graveyard)



        self.Catacombs_entrance.add_neighbor("forward", self.Catacombs_a)

        self.Catacombs_a.add_neighbor("back", self.Catacombs_entrance)
        self.Catacombs_a.add_neighbor("left", self.Catacombs_1)
        self.Catacombs_a.add_neighbor("right", self.Catacombs_b)

        self.Catacombs_b.add_neighbor("left", self.Catacombs_a)
        self.Catacombs_b.add_neighbor("right", self.Catacombs_2)
        self.Catacombs_b.add_neighbor("forward", self.Catacombs_c)

        self.Catacombs_c.add_neighbor("left", self.Catacombs_d)
        self.Catacombs_c.add_neighbor("right", self.Catacombs_3)
        self.Catacombs_c.add_neighbor("forward", self.Catacombs_4)
        self.Catacombs_c.add_neighbor("back", self.Catacombs_b)

        self.Catacombs_d.add_neighbor("left", self.Catacombs_e)
        self.Catacombs_d.add_neighbor("right", self.Catacombs_c)
        self.Catacombs_d.add_neighbor("forward", self.Catacombs_5)

        self.Catacombs_e.add_neighbor("right", self.Catacombs_d)
        self.Catacombs_e.add_neighbor("left", self.Catacombs_final)

        self.Catacombs_final.add_neighbor("right", self.Catacombs_e)

        self.Catacombs_1.add_neighbor("right", self.Catacombs_a)
        self.Catacombs_2.add_neighbor("left", self.Catacombs_b)
        self.Catacombs_3.add_neighbor("left", self.Catacombs_c)
        self.Catacombs_4.add_neighbor("back", self.Catacombs_c)
        self.Catacombs_5.add_neighbor("back", self.Catacombs_d)

        self.CS_west.people.remove(self.richard)
    


        
    def get_choice(self, question, options, callback):
        self.say(question)

        for number, option in enumerate(options, 1):
            self.say(f"{number} - {option}")

        self.choice_active = True
        self.choice_callback = callback
        self.choice_options = options


    def process_choice(self, answer):
        if not self.choice_active:
            return

        answer = answer.strip().lower()

        try:
            selection = int(answer) - 1
        except ValueError:
            self.say("Please enter a number corresponding to your choice.")
            return

        if selection < 0 or selection >= len(self.choice_options):
            self.say("That is not a valid choice.")
            return

        self.choice_active = False

        callback = self.choice_callback
        self.choice_callback = None
        self.choice_options = []

        if callback:
            callback(selection)


    def start_dialogue(self, lines, callback=None):
    
        self.dialogue = lines
        self.dialogue_index = 0
        self.dialogue_active = True
        self.dialogue_callback = callback

        if self.dialogue:
            self.say(self.dialogue[0])


    def advance_dialogue(self):
    
        if not self.dialogue_active:
            return

        self.dialogue_index += 1

        if self.dialogue_index < len(self.dialogue):
            self.say(self.dialogue[self.dialogue_index])
            if self.dialogue[self.dialogue_index] == "Behind it, a trail of colors burned into the air. It came closer and closer until, eventually, it plummeted into the mountain.":
                self.play_sound("crash")

        else:
            self.dialogue_active = False
            self.dialogue = []
            self.dialogue_index = 0

            self.say("--- End Dialogue ---")

            if self.dialogue_callback is not None:
                callback = self.dialogue_callback
                self.dialogue_callback = None
                callback()


    def dialogue_choice(self, question, options):
    
        self.dialogue_active = True
        self.dialogue = []
        self.dialogue_index = 0
        self.say(question)
        for number, option in enumerate(options, 1):
            self.say(f"{number}. {option}")


    def announce_room(self):
        self.say(f"You are in the {self.current_room.name}.")

    def look(self):
        self.say((f"You are in {self.current_room.description}."))
        self.say()
        if self.current_room.monsters is not []:
            for i in range(len(self.current_room.monsters)):
                self.say((f"   There is {self.current_room.monsters[i].description} here."))

        if self.current_room.weapon is not None:
            self.say((f"   There is {self.current_room.weapon.description} here."))

        if self.current_room.items is not []:
            for i in range(len(self.current_room.items)):
                self.say((f"   There is {self.current_room.items[i].description}"))

        if self.current_room.people is not []:
            for i in range(len(self.current_room.people)):
                self.say((f"   {self.current_room.people[i].name} is here"))



        self.say((f"   Exits: {self.current_room.list_exits()}"))
        if self.exposition == True:
            self.say("   There are other ways to go, but best stay on the jobsite for now.")

    def final_boss(self):

        self.start_dialogue([
            "You finally make it to the crash site. The five shards are tucked neatly in your bag.",
            "You can feel them bump your back as you hurry toward the crater.",
            "At the center, you see a tree—a magnificent, extraordinarily beautiful tree, with purple leaves and golden bark, vibrant fruits dangling from its branches.",
            "You: Spirit…is this it? Is this where the shards are meant to be?",
            "Spirit: Yes, Mike…you've brought them home. You must return them to the soil beneath the tree so that they may nourish the dirt once more.",
            "You: Wow, I can't believe it's over…",
            "??? It's not…",
            "You turn around swiftly. Your gaze is met by a familiar face, though it isn't the same. It is the twisted, contorted, sinister smile of an evil force…",
            "It's pretending to be Richard, your boss. You see through it's lies…",
            "You: Richard, what's going on?",
            "Richard: You stole something from me… I want it back. I need it back.",
            "Richard: I need it, Mike",
            "Richard: Give it to me now…or you will die.",
            "Richard brandishes a shovel, sharp enough to kill. You do not recognize his tone, but you are sure that it isn’t him.",
            "As you look to the sky, you see the comet inching closer.",
            "You: I can't give it to you, Richard… the entire mountain will fall! We will both die! We will ALL die…",
            "Richard: I'd sooner die than live without my shard.",
            "Richard: I will take what is mine…",
            "You: You may try...",
        ])



    def go(self, direction):
        if len(self.current_room.monsters) != 0:
            self.say("The monster prevents you from doing that")
            return

        destination = self.current_room.get_neighbor(direction)
        if destination is None:
            self.say(("You can't go that way from here."))
            return
        if self.exposition == True and destination == self.CS_east and self.richard_talk == 1:
            self.say("You: Better talk to Richard first.")
            return
        if destination == self.Library_basement and self.shards_got == 4:
            self.Library_basement.items.append(self.grave_key)
        if destination == self.crash_sanctuary:
            self.final_boss()
        self.play_sound("move")
        self.current_room = destination
        self.update_music()
        self.room_visited.append(self.current_room)
        self.announce_room()




    def take(self, name):
        item = next((item for item in self.current_room.items if item.name == name), None)
        weapon = self.current_room.weapon

        if len(self.current_room.monsters) != 0:
            self.say("The monster prevents you from doing that")
            return
    
        if item is not None:
            if item.takeability == True:
                self.current_room.items.remove(item)
                self.inv.append(item)
                self.say(f"You took the {name}.")
                self.play_sound("take")
                if item.name == "keys":
                    self.shard_find()
                    self.shards_got += 1
                if item.name == "gold shard" or item.name == "white shard" or item.name == "red shard":
                    self.shards_got += 1

                if item.name == "gold shard":
                    self.start_dialogue([
                        "",
                        "As you pick up the gold shard, you can feel the energy coursing through it.",
                        'You decide to call out to the spirit',
                        "You: Spirit, can you hear me?",
                        "???: ...",
                        "You: Spirit?",
                        "???...",
                        "???: Hello, Mike.",
                        "You then see the shadows of the bell tower start to change, twisting to give it form",
                        "You can't decipher a sex, nor any definitive features… only the illumination that comes with its presence.",
                        "You: Took your time! Tell me your name. If I am to call upon you, I'd rather not sound like a maniac yelling at the clouds!",
                        "???: My name is irrelevant.",
                        "???: But the second shard is yours at last! I believe the next to be in the Grave, if you have not already gotten it.",
                        "You: Helpful. Might I ask if there are gonna be any more creatures like the ones around this one?",
                        "???: There certainly will be. The power of the shards tends to attract those that seek it. Especially monsters",
                        "???: The man who took the fifth shard became sick with greed—he lived worshiping the power of the shard and he even took it into his tomb,",
                        "???: I'd wager that he won't depart from it easily, were you to get there.",
                        "You: How do you know?",
                        "???: Greed possessed him to take it from me in the first place.",
                        "???: Eventually, the power of the shard broke his mind. He sealed himself beneath the school so that no-one could take it from him.",
                        "You: I think I can handle a dead guy, spirit.",
                        "???: We will see.",
                        "You: Spirit, these shards…do they have magical properties?",
                        "Spirit: All will be revealed in time... good luck, Mike.",
                    ])
                    return
                if item.name == "white shard":
                    self.start_dialogue([
                        "",
                        "After a hard-won victory, the white shard feels heavy in your tired hands—but all the more deserved.",
                        "You are curious to find out the power of this shard and to expose its secrets.",
                        "You: Spirit, are you there?",
                        "Spirit: Well-done Mike! You are well on your way to saving the mountain.",
                        "You: You know, you still haven't told me what I'm saving the mountain from...",
                        "Spirit: Itself.",
                        "You: Right… and when is this doom anyway?",
                        "Spirit: You have until dusk to collect the remaining shards and return them to the crash site...",
                        "Spirit: You must stay on task, Mike. Get to the next shard and take care of any difficulties.",
                        "Spirit: Seek me after the last shard, you'll need me",
                        "You: where am I going?",
                        "Spirit: Try the chapel, there are secrets around the place that will lead you to the next shard.",
                        "You: On it."
                    ])
                    return

                if item.name == "red shard":
                    self.start_dialogue([
                        "As you catch your breath from that fight, you take a second to make sure that you have the last shard safely in your free hand.",
                        "You exit the catacombs, coming to rest in the Quad.",
                        "You: Spirit? Are you there? What now?",
                        "Spirit: .",
                        "Spirit: ..",
                        "Spirit: ...",
                        "Silence.",
                        "You remember the last thing the spirit said—the crash site from the meteor that hit a hundred years ago.",
                        "Suddenly, You realize the five shards are pointing you somewhere.",
                        "As you pull them out, you notice the sky.",
                        "It's darker. Red lashes are painted in the clouds behind the massive rock plummeting toward you.",
                        "You are running out of time...",
                        "",
                        "(You can now go further west in the forest, bringing you to the crash-site)"
                    ])
                    self.current_room = self.Quad
                    self.announce_room()
                    self.forest_shack.add_neighbor("west", self.crash_site)
                    return
                if item.name == "shovel":
                    self.start_dialogue([
                        "As you stand over a depleted Richard, you turn once more to the sky.",
                        "The comet is minutes away from crashing into Sewanee. The tree is so close, but you are so tired.",
                        "Spirit: You must find the will, Mike…I know you can do it!!!",
                        "You stand, slowly, and edge toward the mystic roots.",
                        "You use Richard's shovel to scrape out the dirt beneath the tree. ",
                        "You take out the shards, one by one, and lay them in the dirt",
                        "You cover them up and lie back as the comet comes hurling toward you…",
                        "You: Maybe I was too late, spirit.",
                        "You feel a hand on your exhausted head…",
                        "Spirit: you are right on time, Mike",
                        "Before you stands a magnificent warrior—tiger-fur clad and intimidating.",
                        "His black hair cascades down his muscular back with ease.",
                        "He raises his hands and thrusts them toward the comet…",
                        "It splits right down the middle and freezes in midair— mere meters from the warriors fingertips.",
                        "With a simple clap, the comet evaporates into dust, blown out into the canyon by the mountain breeze.",
                        "You: Who…are you?",
                        "Tiger-Heart: I am Chief Tiger-Heart…and you, Mike, just saved Sewanee.",
                        "",
                        "THE END",
                    ])
                    self.game_over = True
                    return
            else:
                 self.say(f"You can't take the {name}")
        
        elif weapon is not None and weapon.name == name:
            self.current_room.weapon = None
            self.current_weapon = weapon.name
            self.best_weapon_damage = weapon.damage
            self.weapon_element = weapon.element
            self.equip_inv.append(weapon)
            self.say(f"You took the {weapon.name}.")
            self.play_sound("take")
        
        else:
            self.say(f"There is no {name} here.")

    def inventory(self):
        self.say("You are carrying:")
        for item in self.inv:
            self.say(item.name)
        self.say("You also have these weapons:")
        for weapon in self.equip_inv:
            self.say(weapon.name)

    def attack(self, name):
        monster = next((monster for monster in self.current_room.monsters if monster.name == name), None)
        attack = self.best_weapon_damage
        x = ""
        if monster is not None:
            if monster.weakness == self.weapon_element:
                attack = attack * 2
                x = f"The {name} was weak to your attack!"
            elif monster.resistance == self.weapon_element:
                attack = attack // 2
                x = f"The {name} resisted your attack!"
                if monster.name == "creature":
                    self.say("(Try using a different weapon!)")

            monster.health -= attack

            if monster.health <= 0:
                self.current_room.monsters.remove(monster)
                self.say(f"You did {attack} damage with your {self.current_weapon}, The {name} is dead!")
                self.play_sound("kill")
            else:
                self.play_sound("hurt")
                self.current_health -= monster.attack
                self.say(f"The {name} took {attack} damage from your {self.current_weapon}.")
                self.say(f"You took {monster.attack} damage from the {name}.")

            if self.current_health <= 0:
                self.say("GAME OVER")
                self.game_over = True

        else: 
            self.say(f"There is no {name} here.")

    def stats(self):
        self.say()
        self.say("Your maximum health is",self.health)
        self.say("Your current health is",self.current_health)
        self.say("Your current attack is",self.best_weapon_damage,"using your",self.current_weapon)
        if self.element_read >= 1:
            self.say("Your current attack element is", self.weapon_element)
        elif self.element_read == 0:
            self.say("You dont know anything special about your weapon just yet")
        self.say("You have", self.shards_got, "shards")

    def read(self, name):
    
        #self.say("You have the following books:")
        #if "red book" in self.inv:
            #self.say('red book: "Sewanee and Its History of Meteors"')
        #if "blue-green book" in  self.inv:
            #self.say('blue-green book: "Examining and You! - Examining for Dummies Vol 1"')
        #choice = input("Which color book would you like to read?")
        
        book = self.find_item(name)
        if book is None:
            self.say("You dont have that.")
            return

        if book.name == "document":
            self.start_dialogue([
            "To whomever may find this paper:",
            "First of all, you shouldnt really be in this room, as it should be locked, and the key on my person at all times.",
            "But if you have, as you clearly are reading this document, my name is Professor Edrick.",
            "I discovered something that I no longer want to think about nor even see.",
            "It has haunted me since the day I found it in a nearby cave, and I worry for my mental health.",
            "It causes these visions of monstrous beings coming for me and the discovery.",
            "While I used to believe these were real, I have since been advised to simply get rid of the artifact and see if these visions stop.",
            "And so that is what I plan to do. I will put it in the old storage shack in the forest, and hopefully I will be cured.",
            "This office too, will be locked away for fear of my findings on the artifact.",
            "The forest is unruly, so I will be using an axe to clear my way.",
            "I will be free!",
            "...",
            "The document is signed by the professor at the bottom."
            ])
        elif book.name == "yellow document":
            self.start_dialogue([
                "yellow document things here"
            ])
        
        elif book.name == "red book":
            self.start_dialogue([
                "",
                'You flip to a random page and read the following:',
                "",
                "The above-average fallen meteor amount around sewanee has been a very intriguing discovery for scientists and fanatics alike.",
                "Usually, places around the world have a very similar amount of recovered meteor fragments, yet Sewanee seems to be a hot spot for the like.",
                "This could be to many factors, such as an increase in magnetic properties... ",
                "",
                "The book then goes on to describe many different reasonings, and what each would mean for science",
                ""
            ])

        elif book.name == "blue-green book":
            self.start_dialogue([
                "",
                "You realize that it is honestly more of a magazine then a book.",
                "",
                'Hey there Dummies! Did you know about the wonderful world of examining!',
                'Thats right! You can examine so many wonderful, wonderous things!',
                'Monsters to find out info, people to find out about them, items that you own...',
                "Even the Rooms you stand in!",
                "Tune in next week as we go over the specifics of what to look for!",
                "(psst, as a bonus, because you read this, you should be a bit better at examining monsters! You're welcome!)",
                "       Some ROOMS will have more detail if you EXAMINE them."
            ])
            if self.monster_prof == 0:
                self.monster_prof += 1
        
        elif book.name == "note":
            self.start_dialogue([
                "The handwriting is in cursive, and is very hastily drawn:",
                '"When you have aquired the 4 shards, I will leave you a gift here at this spot."',
                '"Use it to get inside the ancient catacombs, and you will find the final shard waiting.',
                '"Be as prepared as you can, what lies beneath is dangerous"'
            ])

        else: 
            self.say("You cant read that")
 

    def equip(self, name): 
        weapon = next((weapon for weapon in self.equip_inv if weapon.name == name), None)


        if weapon is not None:
            self.current_weapon = weapon.name
            self.best_weapon_damage = weapon.damage
            self.weapon_element = weapon.element
            self.say(f"You equipped the {weapon.name} ")
            self.play_sound("equip")
        
        else:
            self.say("You cant equip that")

    def find_item(self, name):
        return next((item for item in self.inv if item.name == name),None)

    def find_item2(self,name):
        return next((item for item in self.current_room.items if item.name == name),None)

    def use(self, name):
        item = self.find_item(name)

        if item is None:
            self.say("You cant do that")
            return

        if item.name == "keys" and self.current_room == self.Parking_lot:
            if self.exposition:
                def car_choice(selection):
                    if selection == 0:
                        self.say("You used the keys to unlock your car")
                        self.house_dialouge()
                        self.exposition = False
                        self.update_map()

                    else:
                        self.say("You decided not to unlock the car.")

                self.get_choice(
                    "Use the keys on your car?",
                    ["Yes", "No"],
                    car_choice
                )
            elif self.shards_got < 5:
                self.say("You: I probably should'nt leave until I have all the shards.")


        elif item.name == "bandages":
            temp = self.current_health
            self.current_health += 3

            if self.current_health > self.health:
                self.current_health = self.health

            health_healed = self.current_health - temp
            self.play_sound("heal")
            self.inv.remove(item)

            self.say("You used the bandages on yourself, you healed",
                    health_healed, "health")

        elif item.name == "skull key" and self.current_room == self.Library_basement:
            def door_choice(selection):
                if selection == 0:
                    self.inv.remove(item)
                    self.say("You unlocked the door")
                    self.say("You can now go inside the catacombs")

                    self.Library_basement.add_neighbor("in", self.Catacombs_entrance)
                    self.Catacombs_entrance.add_neighbor("out", self.Library_basement)
                else:
                    self.say("You decided not to use the key")
            self.get_choice(
                "Use the skull key on the door?",
                ["Yes", "No"],
                door_choice
            )

        elif item.name == "horse key" and self.current_room == self.Gailor_right:

            def door_choice(selection):
                if selection == 0:
                    self.inv.remove(item)
                    self.say("You unlocked the door.")
                    self.say("You can now go inside the office")

                    self.Gailor_right.add_neighbor("in", self.Gailor_locked_room)
                    self.Gailor_locked_room.add_neighbor("out", self.Gailor_right)
                else:
                    self.say("You decided not to use the key.")

            self.get_choice(
                "Use the horse key on the door?",
                ["Yes", "No"],
                door_choice
            )

        else:
            self.say("You cant use that")

    def smash(self, name):
        if self.current_room.monsters:
            self.say("The monster prevents you from doing that")
            return
        item = next(
            (item for item in self.current_room.items if item.name == name),
            None
        )

        if item is None:
            self.say("There is nothing like that here.")
            return

        if item.name == "box":

            def smash_choice(selection):
                if selection == 0 and self.axe in self.equip_inv:
                    self.say("You broke the box open with your axe")

                else:
                    self.say("You broke the box open with your fist, and took 1 damage")
                    self.current_health -= 1

                    if self.current_health <= 0:
                        self.current_health = 1

                self.forest_shack_inside.items.remove(self.box)
                self.forest_shack_inside.items.append(self.document2)
                self.forest_shack_inside.items.append(self.white_shard)

            options = ["Use the axe", "Use your fist"]

            self.get_choice(
                "What will you break it with?",
                options,
                smash_choice
            )

    def exposition_text(self):
        self.start_dialogue([
            "A hundred years ago, when the mountain was just a mountain, the waters were still and untroubled.",
            "Its lakes were calm; its waterfalls gentle and kind.",
            "They ran carefree through the mountain, like a child's laugh echoing in summer air. The trees and the leaves and the breeze were full of life and hope.",
            "Green and red and purple and blue filled the grassy pastures. Creatures of all kinds were welcome amongst the pines—even those that history hadn't found.",
            "The mountain was perfect...",
            "And then came man.",
            "They came with their fire and with their envy, their lust for gold and for power.",
            "They stripped the trees and cut them from the earth. They opened new caves and ravaged the old—hungry for the taste of wealth.",
            "They slew just about anything they could sink their blades into. Pigs, sheep, cows, deer—everything was theirs.",
            "Some attempted to contain the rampage. Chief Tiger-Heart, who had lived amongst the trees for all his life, summoned his warriors to combat the threat.",
            "The mountain was his home... he would defend it at any cost.",
            "The following weeks were a bloody time for Tiger-Heart and his men. They lost many men, many women; even children.",
            "Finally, Tiger-Heart decided to call upon the spirits.",
            "He performed the ritual, the battle dance. He leapt and prayed and spun and whisked away under the moonlight.",
            "By morning, the spirits had answered.",
            "The sky was rich. Pink and orange streaks swirled in and amongst the clouds, a new day had come.",
            "Above the clouds, above the mist and the mountains, a ball of light came crashing toward the earth.",
            "Behind it, a trail of colors burned into the air. It came closer and closer until, eventually, it plummeted into the mountain.",
            "Tiger-Heart ventured to the crash site. A deep crater was buried amongst the trees. When he climbed into it, he admired the rock that had fallen from outer space.",
            "He ordered his men to break it open. Within it was a gift from the spirits.",
            "Seven brightly colored shards illuminated the surrounding void... each containing a mystic property, given to Tiger-Heart to help him maintain the peace of nature.",
            "But one night, Tiger-Heart was ambushed, and the shards fell into the hands of the invaders.",
            "They cut off his head and took his intestines from his belly—determined to make an example of him.",
            "He died a miserable death...",
            "But not before he cursed the shards.",
            "One by one, the men who seized the shards mysteriously died. The curse did not.",
            "Tiger-Heart made sure the shards would destroy the mountain if man ever corrupted its beautiful land.",
            "He gave man one hundred years to prove they could live in peace with the land...or else.",
            "Eventually, the shards were lost to history. The prophecy died too; man became even hungrier and the fate of Sewanee was all but sealed.",
            "The shards would summon another comet. This one, however, would destroy the mountain forever.",
            "But on the eve of the destruction of Sewanee, fate would intervene.",
            "One man could save the Mountain."
        ])

    def talk(self, name):

        if name == "" or name == "to":
            self.say("Talk to whom?")
            return

        if self.current_room == self.CS_west and name == "richard":
            if self.find_item("keys") is None and self.richard_talk == 1:
                self.start_dialogue([
                    "Richard: Oh hey Mike!",
                    "Richard: I coulda sworn you were done for the day? Why you still here?",
                    "You: Yeah... I couldnt find my keys, figure I left 'em somewhere around here.",
                    "You: Have you seen 'em?",
                    "Richard: Well let me think...",
                    "Richard: ...",
                    "Richard: You know what, I think I have! See I saw something at the bottom of the hole on the other side of the site earlier.",
                    "You: Awesome, thanks Rick, I'll be on my way then.",
                    "Richard: Hold on there Mike.",
                    "You: ?",
                    "Richard: See, thats the reason I'm here so late, theres this freakishly big rodent down in that hole.",
                    "Richard: I've been trying to figure out how to get rid of it for about an hour now.",
                    "You: Why dont you get down there and just... y'know?",
                    "Richard: ...",
                    "Richard: Im scared of rats.",
                    "You: ...",
                    "You: Alright I'll deal with it and get my damn keys.",
                    "Richard: Thank you Mike."
                ])
                self.richard_talk = 2
                return

            elif self.find_item("keys") is None and self.richard_talk == 2:
                self.start_dialogue([
                    "Richard: Find 'em yet Mike?",
                    "You: Not yet Rick."
                ])
                return

            elif self.find_item("keys") is not None and self.richard_talk in [1, 2]:
                self.start_dialogue([
                    "You: Well I took care of that rat problem for you.",
                    "Richard: Really? I appreciate it, truly.",
                    "Richard: Did it give you any trouble?",
                    "You: Well it did scratch me up a tad, but I got my keys and thats what matters!",
                    "You: (And that weird shard of some crystal, but best not tell him about that until I know what exactly it is.)",
                    "Richard: Ehhhh just slap some dirt on it and it'll be fine by morning.",
                    "You: Right you are Rick, right you are.",
                    "You: I'll catch you Monday buddy, see ya later."
                ])

                self.richard_talk = 3
                return

            elif self.richard_talk == 3:
                self.start_dialogue([
                    "Richard: ?"
                ])
                return

        if self.current_room == self.Graveyard and name == "gravekeeper":
            if self.gravekeeper_talk == 1:
                self.start_dialogue([
                    "Gravekeeper: Hello there.",
                    "You: Do I know you?",
                    "Gravekeeper: Oh no you dont, but I do know why you are here.",
                    "You: And what would that be for?",
                    "Gravekeeper: You seek the shards, and the power that comes with them.",
                    "You: Sure yeah thats what im seeking.",
                    "You: So how can you help me with that?",
                    "Gravekeeper: I myself hold one of these ancient shards, and I alone can bestow you with it.",
                    "You: So can I have it?",
                    "Gravekeeper: If you can answer my questions, then I will be glad to give it over.",
                    "Gravekeeper: Go to the northern graveyard, my questions will be about the stones there.",
                    "Gravekeeper: Answer them all correctly, and I will give you the shard",
                    "You: Got it"
                ])
                self.gravekeeper_talk = 2
                return
            elif self.gravekeeper_talk == 2:
                self.start_dialogue([
                    "Gravekeeper: Question 1, How many graves can you see total? "
                ])
                def riddle_choice(selection):
                    if selection == 0:
                        self.say("Gravekeeper: Incorrect.")
                    elif selection == 1:
                        self.say("Gravekeeper: Thats Correct!")
                        self.gravekeeper_talk = 3
                    elif selection == 2:
                        self.say("Gravekeeper: Incorrect.")
                self.get_choice(
                    "Number of Graves?",
                    ["2", "3", "5"],
                    riddle_choice
                    )
                return
            elif self.gravekeeper_talk == 3:
                self.start_dialogue([
                    "Gravekeeper: Question 2, Which stone is the oldest?"
                ])
                def riddle_choice(selection):
                    if selection == 0:
                        self.say("Gravekeeper: Incorrect")
                    elif selection == 1:
                        self.say("Gravekeeper: Incorrect")
                    elif selection == 2:
                        self.say("Gravekeeper: That's Correct!")
                        self.gravekeeper_talk = 4
                self.get_choice(
                    "Oldest stone?",
                    ["rusty","mossy","cross"],
                    riddle_choice
                )
                return
            elif self.gravekeeper_talk == 4:
                self.start_dialogue([
                    "Gravekeeper: Finally, Question 3, What is the average of all of the birthyears on the stones?"
                ])
                def riddle_choice(selection):
                    if selection == 0:
                        self.say("Gravekeeper: Incorrect")
                    elif selection == 1:
                        self.say("Gravekeeper: Incorrect")
                    elif selection == 2:
                        self.say("Gravekeeper: That's Correct!")
                        self.gravekeeper_talk = 5
                self.get_choice(
                    "Average Birthyear?",
                    ["1929","1942","1934"],
                    riddle_choice
                )
                return
            elif self.gravekeeper_talk == 5:
                self.start_dialogue([
                    "You: Any more questions?",
                    "Gravekeeper: That is fortunately all of my questions for you sir.",
                    "Gravekeeper: And so, here you are good sir, that which you seek to aid you in your mission.",
                    "You: Thank you.",
                    "You got the dark shard.",
                    "Gravekeeper: Good Luck",
                    "",
                    "The smell of wet stone and old trees lingers in your nostrils as you walk away from the gravekeeper.",
                    "The second to last shard is firmly in your grasp—a black, jagged stone of undeniable beauty and intrigue. ",
                    "You call to the spirit…nothing. You walk further away and try once more but to no avail.",
                    "Suddenly, it lunges toward you from the sky.",
                    "Spirit: Mike! I haven't got long!",
                    "Spirit: There are more spirits on their way to try and stop you getting the last shard, evil ones with malice in their withered souls.",
                    "You: What? I don't understand?",
                    "Spirit: The shard you have now, go to the library—there is one more that lies beneath the surface. It is the last one.",
                    "You: How will I find it?",
                    "Spirit: I have put an ancient key there now that you have the rest of the shards.",
                    "Spirit: Hurry!",
                    "And just like that, you watch the spirit vanish.",
                    "You are close to the end; you must save Sewanee!",
                ])
                self.gravekeeper_talk = 6
                self.inv.append(self.dark_shard)
                self.shards_got += 1
                return
            elif self.gravekeeper_talk == 6:
                self.start_dialogue([
                    "Gravekeeper: Remember, the library."
                ])
                return


        self.say("There is not anybody here with that name.")

    def ring_bell(self, number):

        if self.current_room != self.Chapel_bells:
            self.say("There are no bells here.")
            return

        if self.bell_puzzle_solved:
            self.say("The bells have already been rung.")
            return

        if number not in [1, 2, 3]:
            self.say("There is no bell with that number.")
            return

        self.bell_sequence.append(number)

        bell_sounds = {
            1: "DONG...",
            2: "DOONG...",
            3: "DING..."
        }

        self.say("You pull the rope of bell", number)
        self.say(bell_sounds[random.randint(1,3)])

        if len(self.bell_sequence) == 3:

            if self.bell_sequence == self.correct_bell_sequence:

                self.say("The three bells ring together in harmony.")
                self.say("A bright light shines through the bell tower.")
                self.say("You hear a loud noise coming from the alter below.")

                self.bell_puzzle_solved = True

                self.Chapel_sanctum.items.append(self.gold_shard)

            else:

                self.say("The bells ring in a terrible noise.")
                self.say("Something about that sequence was wrong.")

                self.bell_sequence = []
        
    def house_dialouge(self):
        def skip_choice(selection):

            if selection == 1:
                self.start_dialogue([
                "(This is not the final script for this portion)",
                "As you drive home, you think about that shard you found, and what that voice you heard could possibly mean.",
                "When you get back to your place down the mountain, you just put the shard on you nightstand, eat some dinner and go to bed.",
                ".",
                "..",
                "...",
                "???: Mike.",
                'You: Hello? Who are you? Where am I?',
                "As you look around, you see that you are in a floating world of purple and gold colored clouds all around. There is a glowing figure in front of you.",
                '???: You are in a realm of which we can communicate, what you humans call, "dreaming".',
                "???: As for me, who I am is not important to you currently. Just know I am here to help you in your journey ahead.",
                "You: Journey ahead? What are you talking about?",
                "???: The shard you found, it is just one part of an ancient catastrophe, that only you can put a stop to.",
                "???: The fragment is of a much greater power, one that could bring the end of the world if not dealt with.",
                "You: And how exactly am I to deal with this terrible catastrophe?",
                "???: Gather the rest of the shards Mike, make them whole once again and all will be well.",
                "You: And where the hell are they exactly?",
                "???: My powers have weakened due to them being split. I can not sense the others very well.",
                "???: However, I believe you will find a clue to them in the building called 'Gailor'",
                "You: And when I find these, I'll learn more about the rest right?",
                "???: Yes Mike, all will be shown in good time.",
                "The glowing spirit begins to fade, and as it does you can feel yourself being to wake up.",
                "???: Dont... Forget... Mike...",
                "",
                "As soon as you wake up, you reach for the shard.",
                "You: Great catastrophe huh? Don't think that would be too good. Might as well see what I can do.",
                "You get ready and head back to Sewanee, to see What Lies Beneath.",
                ""
            ])
                self.say("-THE NEXT DAY-")
                self.announce_room()
            else:
                self.say("You skipped the house sequence")
                self.say("-THE NEXT DAY-")
                self.announce_room()

        self.get_choice( "Skip house sequence?", ["Yes", "No"],
        skip_choice
    )
           

    def shard_find(self):
        
        self.start_dialogue([
            "",
            "Next to the keys, you notice something.",
            "You: What the?",
            "You walk over to a spot in the dirt that is glowing a reddish purple.",
            "The thing glowing is actually a purple shard, which is perfectly placed in the slot of a larger rectangular stone.",
            "The larger stone is smoothed out, with symbols you've never seen before etched along the sides.",
            "You reach down and take the stone.",
            "You: Some crystal shard looking thing, but whats it doing here?",
            "Suddenly, a bright light shines from the shard.",
            "???: FIND.... THEM....",
            "You: What the hell was that? Good lord my eyes hurt.",
            "You got the shard"
        ])
        self.equip_inv.append(self.shard)
        self.equip("shard")
        
        
    def examine(self, name):
        item = self.find_item(name)
        item_2 = self.find_item2(name)
        monster = next((monster for monster in self.current_room.monsters if monster.name == name), None)
        self.say("")
        if name == "richard" and self.current_room == self.CS_west:
            self.say("Richard:", self.richard.description)

        elif name == "gravekeeper" and self.current_room == self.Graveyard:
            self.say("Gravekeeper:", self.gravekeeper.description)

        elif monster is not None:
            self.say(monster.name,": ", monster.description, sep="")
            self.say("The monster has ",monster.health," health left",  sep = "")
            if self.monster_prof >= 1:
                self.say("The monster has", monster.attack,"attack")
            if self.element_read >= 1:
                self.say("The monster resists", monster.resistance,"type damage")
            if self.element_read >= 2:
                self.say("the monster is weak to", monster.weakness, "type damage")
            if self.element_read == 0:
                self.say("You can't examine anything special about the monster for now")
            if self.monster_prof == 0:
                self.say("you can't tell how powerful the monster is")

        elif name == "room" or name == "the room":
            
            if self.current_room == self.Gailor_auditorium and self.find_item("horse key") is None:
                self.start_dialogue([
                    "You notice something you hadn't seen before: A key had fallen in between one of the front row seats.",
                    "You go over to grab it.",
                    "It is a key with a symbol of a horse dangling from the chain.",
                    "You took the horse key."
                    ])
                self.inv.append(self.horse_key)
            
            
            if self.current_room == self.Forest:
                self.say("The trail leading to the building you can see in the distance is completely blocked by bushes and vines.")

                if self.axe in self.equip_inv:

                    def axe_choice(selection):
                        if selection == 0:
                            self.Forest.add_neighbor("west", self.forest_shack)
                            self.forest_shack.add_neighbor("east", self.Forest)

                            self.say("You used the axe to cut through a path")
                            self.say("You can now go further west")
                        else:
                            self.say("You decide not to cut through the bushes.")

                    self.get_choice(
                        "Use the axe to clear the path?",
                        ["Yes", "No"],
                        axe_choice
                    )
            else:
                self.say("Nothing special about this room")

        elif item is not None:
            self.say(item.description)
            if item.name == "bandages":
                self.say("These can heal up to 3 damage that you have taken. One time use")
            if item.name == "horse key":
                self.say("Can likely be used on a door with anything horse related on it")
            if item.name == "tablet":
                self.say("The tablet is worn by time and mostly illegible, but you can make out the words: ")
                self.say("The final bell, the signal of eternity.")
            

        elif item_2 is not None:
            if item_2.name == "rusty grave":
                self.say("The stone says the following:")
                self.say("Lauren Kilter. Born: April 3, 1950. Died: Dec 23, 2010.")
            elif item_2.name == "mossy grave":
                self.say("The stone says the following:")
                self.say("Brody Robinson. Born: June 17, 1948. Died: Jan 19, 2012.")
            elif item_2.name == "cross grave":
                self.say("The stone says the following:")
                self.say("Peter McCartney. Born: ??? 1904. Died: August 3, 1970.")

            elif item_2.name == "alter":
                self.start_dialogue([
                    "On the back of the alter, the wood contains the words:",
                    '"The first bell, of new beginnings'
                ])

            elif item_2.name == "window":
                self.start_dialogue([
                "The glass depicts a meteor of purple and gold across a great forest,",
                "Underneath the meteor, are words etched into the glass.",
                '"The second bell, a heros sacrifice."'
                ])
            
            else:
                self.say(item_2.description)
            


        else: 
            self.say("You can't examine that.")


    def help(self):
            self.say("go (direction) - go in whatever direction you type")
            self.say("look - view the things in the current room")
            self.say("take (item) - take whatever item is in the room with you, you wont ever need spaces")
            self.say("inventory - view all things you have in your possession")
            self.say("attack (monster) - use your current weapon on the monster in the room")
            self.say("stats - view your current stats")
            self.say("use (thing) - a general use for many different things")
            self.say("talk to (person) - talk to somebody")
            self.say("any other ones you must figure out for yourself!")


    def handle_command(self, line):
        if self.game_over:
            return

        self.say(f"> {line}")
        words = line.lower().split()
        if not words:
            return

        command = words[0]

        if command == "":
            return
        elif command == "look" or command == "l":
            self.look()
        elif command == "go" and len(words) > 1:
            self.go(words[1])
        elif command == "quit":
            self.game_over = True
            return
        elif command == "help":
            self.help()
        elif command == "take" and len(words) > 1:
            item_name = " ".join(words[1:])
            self.take(item_name)
        elif command == "inventory" or command == "i":
            self.inventory()
        elif command == "attack" and len(words) > 1:
            monster_name = " ".join(words[1:])
            self.attack(monster_name)
        elif command == "stats":
            self.stats()
        elif command == "read" and len(words) > 1:
            item_name = " ".join(words[1:])
            self.read(item_name)
        elif command == "equip" and len(words) > 1:
            self.equip(words[1])
        elif command == "use" and len(words) > 1:
            item_name = " ".join(words[1:])
            self.use(item_name)
        elif command == "talk" and len(words) == 2:
            self.talk(words[1])
        elif command == "talk" and len(words) == 3:
            self.talk(words[2])
        elif command == "talk":
            self.talk("")
        elif command == "examine" and len(words) > 1:
            item_name = " ".join(words[1:])
            self.examine(item_name)
        elif (command == "break" or command == "smash") and len(words) > 1:
            item_name = " ".join(words[1:])
            self.smash(item_name)
        elif command == "ring" and len(words) > 2:
            if words[1] == "bell":
                    number = int(words[2])
                    self.ring_bell(number)
        else:
            self.say(("I don't understand that."))


def wrap_text(text, font, max_width):

    if not text:
        return [""]
    # Preserve paragraph breaks from the story files on screen.
    if "\n" in text:
        lines = []
        for paragraph in text.splitlines():
            lines.extend(wrap_text(paragraph, font, max_width))
        return lines
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = word if not current else current + " " + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_game(screen, font, small_font, game):
    screen.fill((24, 24, 28))
    screen.blit(font.render("What Lies Beneath", True, (235, 235, 240)), (30, 20))
    label = "Music: muted" if game.music_muted else "Music: on"
    screen.blit(small_font.render(label + " (M)", True, (180, 180, 190)), (650, 25))

    lines = []
    for message in game.messages:
        lines.extend(wrap_text(message, small_font, WIDTH - 60))
    lines = lines[-20:]

    y = 70
    for line in lines:
        screen.blit(small_font.render(line, True, (220, 220, 225)), (30, y))
        y += 23

    pygame.draw.line(screen, (100, 100, 110), (30, HEIGHT - 70), (WIDTH - 30, HEIGHT - 70), 2)
    screen.blit(small_font.render("> " + game.current_input, True, (255, 255, 255)), (30, HEIGHT - 50))
    pygame.draw.line(
    screen,
    (100, 100, 110),
    (30, HEIGHT - 70),
    (WIDTH - 30, HEIGHT - 70),
    2)

    if game.dialogue_active:
        screen.blit(
            small_font.render(
                "Press ENTER to continue...",
                True,
                (180, 180, 200)
            ),
            (WIDTH - 290, HEIGHT - 50)
        )

    else:
        screen.blit(
            small_font.render(
                "> " + game.current_input,
                True,
                (255, 255, 255)
            ),
            (30, HEIGHT - 50)
        )

async def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("What Lies Beneath")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 22)

    game = TextAdventure()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif not game.music_started and event.key == pygame.K_RETURN:
                    game.start_music()
                    game.say("Background audio started.")
                    game.say("Type commands into console, type help for command list")
                    game.say("Some important text will appear in all caps.")
                    game.say("")
                    def choice_result(selection):
                        if selection == 0:
                            game.exposition_text()
                            game.announce_room()

                        elif selection == 1:
                            game.say("You skipped the exposition.")
                            game.announce_room()


                    game.get_choice(
                        "New Game?(See exposition)",
                        ["Y, see exposition", "N, skip"],
                        choice_result
                        )
                    
                elif event.key == pygame.K_m and not game.current_input:
                    game.toggle_music()
                elif event.key == pygame.K_RETURN:

                    if game.dialogue_active:
                        game.advance_dialogue()

                    elif game.choice_active:
                        answer = game.current_input
                        game.current_input = ""
                        game.process_choice(answer)

                    elif not game.game_over:
                        command = game.current_input.strip()
                        game.current_input = ""
                        game.handle_command(command)
                
                
                
                elif event.key == pygame.K_BACKSPACE:
                    game.current_input = game.current_input[:-1]
                elif event.unicode and event.unicode.isprintable():
                    game.current_input += event.unicode

        draw_game(screen, font, small_font, game)
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
