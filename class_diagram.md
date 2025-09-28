classDiagram
    direction LR
    class GameObject {
        #_image: Surface
        #_rect: Rect
        #_speed: int
        +__init__(image, rect, speed)
        +rect(): Rect
        +draw(surface: Surface)
        +update()
    }
    class Player {
        #_images: list<Surface>
        #_img_index: int
        +__init__(images, speed)
        +move(keys: dict)
        +change_image()
    }
    class Enemy {
        +update()
    }
    class Bonus {
        +update()
    }
    class Game {
        -screen: Surface
        -clock: Clock
        -player: Player
        -enemies: list<Enemy>
        -bonuses: list<Bonus>
        -scores: int
        -high_score: int
        +__init__()
        +run()
        +handle_gameplay()
        +create_enemy()
        +create_bonus()
        +load_highscore(): int
        +save_highscore()
    }

    GameObject <|-- Player : Успадкування
    GameObject <|-- Enemy : Успадкування
    GameObject <|-- Bonus : Успадкування

    Game *-- Player : Композиція (1)
    Game *-- Enemy : Композиція (1..*)
    Game *-- Bonus : Композиція (1..*)
