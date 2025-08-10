import random

class Character:
    def __init__(self, name, health, attack):
        self.name = name
        self.health = health
        self.attack = attack

    def is_alive(self):
        return self.health > 0

    def attack_enemy(self, enemy):
        damage = random.randint(0, self.attack)
        enemy.health -= damage
        print(f"{self.name} attacks {enemy.name} for {damage} damage!")

class Game:
    def __init__(self):
        self.player = Character("Hero", 100, 20)
        self.enemy = Character("Goblin", 50, 10)

    def play(self):
        print("A wild Goblin appears!")
        while self.player.is_alive() and self.enemy.is_alive():
            self.player.attack_enemy(self.enemy)
            if self.enemy.is_alive():
                self.enemy.attack_enemy(self.player)
                print(f"{self.player.name} has {self.player.health} health left.")
            else:
                print(f"{self.enemy.name} has been defeated!")

        if not self.player.is_alive():
            print(f"{self.player.name} has been defeated! Game Over.")

if __name__ == "__main__":
    game = Game()
    game.play()