from dataclasses import dataclass


@dataclass
class Hero:
    id: int
    opendota_id: int
    name: str
    pos: list[int]
    alt_pos: list[int]


HEROES = [
    Hero(0, 0, "<UNK>", [], []),
    Hero(1, 1, "Anti-Mage", [1], []),
    Hero(2, 2, "Axe", [3], []),
    Hero(3, 3, "Bane", [5], [4]),
    Hero(4, 4, "Bloodseeker", [1, 3], [2]),
    Hero(5, 5, "Crystal_Maiden", [5], [4]),
    Hero(6, 6, "Drow_Ranger", [1], []),
    Hero(7, 7, "Earthshaker", [3, 4], []),
    Hero(8, 8, "Juggernaut", [1], []),
    Hero(9, 9, "Mirana", [4], [3]),
    Hero(10, 10, "Morphling", [1], [2]),
    Hero(11, 11, "Shadow_Fiend", [1, 2], []),
    Hero(12, 12, "Phantom_Lancer", [1], []),
    Hero(13, 13, "Puck", [2], []),
    Hero(14, 14, "Pudge", [1, 4], [2, 3]),
    Hero(15, 15, "Razor", [1, 3], []),
    Hero(16, 16, "Sand_King", [3], []),
    Hero(17, 17, "Storm_Spirit", [2], []),
    Hero(18, 18, "Sven", [1], []),
    Hero(19, 19, "Tiny", [2, 4], []),
    Hero(20, 20, "Vengeful_Spirit", [5], [4]),
    Hero(21, 21, "Windranger", [2, 4], [3]),
    Hero(22, 22, "Zeus", [2], [4]),
    Hero(23, 23, "Kunkka", [2, 3], [4]),
    Hero(24, 25, "Lina", [1, 2], [4]),
    Hero(25, 26, "Lion", [5], [4]),
    Hero(26, 27, "Shadow_Shaman", [5], [4]),
    Hero(27, 28, "Slardar", [3], []),
    Hero(28, 29, "Tidehunter", [3], []),
    Hero(29, 30, "Witch_Doctor", [5], [4]),
    Hero(30, 31, "Lich", [5], [4]),
    Hero(31, 32, "Riki", [4, 1], []),
    Hero(32, 33, "Enigma", [3], [4]),
    Hero(33, 34, "Tinker", [2], []),
    Hero(34, 35, "Sniper", [1], [2]),
    Hero(35, 36, "Necrophos", [2, 3], []),
    Hero(36, 37, "Warlock", [5], [4]),
    Hero(37, 38, "Beastmaster", [3], []),
    Hero(38, 39, "Queen_of_Pain", [2], []),
    Hero(39, 40, "Venomancer", [3, 4], []),
    Hero(40, 41, "Faceless_Void", [1], []),
    Hero(41, 42, "Wraith_King", [1], []),
    Hero(42, 43, "Death_Prophet", [2, 3], []),
    Hero(43, 44, "Phantom_Assassin", [1], []),
    Hero(44, 45, "Pugna", [2, 4], []),
    Hero(45, 46, "Templar_Assassin", [1, 2], []),
    Hero(46, 47, "Viper", [2, 3], []),
    Hero(47, 48, "Luna", [1], []),
    Hero(48, 49, "Dragon_Knight", [1, 2, 3], []),
    Hero(49, 50, "Dazzle", [5, 4], []),
    Hero(50, 51, "Clockwerk", [5, 4], []),
    Hero(51, 52, "Leshrac", [2], []),
    Hero(52, 53, "Natures_Prophet", [1, 3], [4]),
    Hero(53, 54, "Lifestealer", [1], []),
    Hero(54, 55, "Dark_Seer", [3], []),
    Hero(55, 56, "Clinkz", [1, 2], []),
    Hero(56, 57, "Omniknight", [5, 3], [4]),
    Hero(57, 58, "Enchantress", [5], [4]),
    Hero(58, 59, "Huskar", [1, 2], []),
    Hero(59, 60, "Night_Stalker", [3], []),
    Hero(60, 61, "Broodmother", [3], [2]),
    Hero(61, 62, "Bounty_Hunter", [4], []),
    Hero(62, 63, "Weaver", [1], []),
    Hero(63, 64, "Jakiro", [5, 4], []),
    Hero(64, 65, "Batrider", [2, 3], []),
    Hero(65, 66, "Chen", [5], [4]),
    Hero(66, 67, "Spectre", [1], []),
    Hero(67, 68, "Ancient_Apparition", [5], [4]),
    Hero(68, 69, "Doom", [3], []),
    Hero(69, 70, "Ursa", [1], []),
    Hero(70, 71, "Spirit_Breaker", [4], [3]),
    Hero(71, 72, "Gyrocopter", [1, 4], []),
    Hero(72, 73, "Alchemist", [1], [2]),
    Hero(73, 74, "Invoker", [2], []),
    Hero(74, 75, "Silencer", [5, 4], []),
    Hero(75, 76, "Outworld_Destroyer", [2], []),
    Hero(76, 77, "Lycan", [3], [1]),
    Hero(77, 78, "Brewmaster", [3], []),
    Hero(78, 79, "Shadow_Demon", [5], [4]),
    Hero(79, 80, "Lone_Druid", [1, 3], [2]),
    Hero(80, 81, "Chaos_Knight", [1], [3]),
    Hero(81, 82, "Meepo", [2], []),
    Hero(82, 83, "Treant_Protector", [5, 4], []),
    Hero(83, 84, "Ogre_Magi", [5, 4], []),
    Hero(84, 85, "Undying", [5], [4, 3]),
    Hero(85, 86, "Rubick", [5], [4]),
    Hero(86, 87, "Disruptor", [5], [4]),
    Hero(87, 88, "Nyx_Assassin", [4], []),
    Hero(88, 89, "Naga_Siren", [1], []),
    Hero(89, 90, "Keeper_of_the_Light", [4], [5, 2]),
    Hero(90, 91, "Io", [4], [5]),
    Hero(91, 92, "Visage", [2, 3], [1, 4]),
    Hero(92, 93, "Slark", [1], []),
    Hero(93, 94, "Medusa", [1], []),
    Hero(94, 95, "Troll_Warlord", [1], []),
    Hero(95, 96, "Centaur_Warrunner", [3], []),
    Hero(96, 97, "Magnus", [3], [4]),
    Hero(97, 98, "Timbersaw", [3], []),
    Hero(98, 99, "Bristleback", [3], []),
    Hero(99, 100, "Tusk", [2, 4], [3]),
    Hero(100, 101, "Skywrath_Mage", [4], [5, 2]),
    Hero(101, 102, "Abaddon", [1, 3], [4]),
    Hero(102, 103, "Elder_Titan", [4], [5, 3]),
    Hero(103, 104, "Legion_Commander", [3], []),
    Hero(104, 105, "Techies", [4], []),
    Hero(105, 106, "Ember_Spirit", [2], []),
    Hero(106, 107, "Earth_Spirit", [4], []),
    Hero(107, 108, "Underlord", [3], []),
    Hero(108, 109, "Terrorblade", [1], []),
    Hero(109, 110, "Phoenix", [4, 3], [5]),
    Hero(110, 111, "Oracle", [5], []),
    Hero(111, 112, "Winter_Wyvern", [4, 5], []),
    Hero(112, 113, "Arc_Warden", [2], [1]),
    Hero(113, 114, "Monkey_King", [1, 4], []),
    Hero(114, 119, "Dark_Willow", [4], [2, 5]),
    Hero(115, 120, "Pangolier", [2, 3, 4], []),
    Hero(116, 121, "Grimstroke", [4], [5]),
    Hero(117, 123, "Hoodwink", [4], [5]),
    Hero(118, 126, "Void_Spirit", [2], [3, 4]),
    Hero(119, 128, "Snapfire", [4, 5], []),
    Hero(120, 129, "Mars", [3], []),
    Hero(121, 135, "Dawnbreaker", [3, 4], []),
    Hero(122, 136, "Marci", [3, 1], [4, 5]),
    Hero(123, 137, "Primal_Beast", [3, 4], [2]),
    Hero(124, 138, "Muerta", [1, 2], []),
]

TKINTER_BIG_FONT = ("Helvetica", 18)
