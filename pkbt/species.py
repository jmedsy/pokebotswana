from dataclasses import dataclass

@dataclass(frozen=True)
class SpriteCheck:
    crosshair: tuple[int, int]
    normal_hex: str
    shiny_hex: str | None = None

@dataclass(frozen=True)
class Species:
    wild: SpriteCheck
    summary: SpriteCheck | None = None

SPECIES = {
    "CATERPIE": Species(
        wild=SpriteCheck(
            crosshair=(174, 56),
            normal_hex="#7b9c63"
        )
    ),
    "CLEFAIRY": Species(
        wild=SpriteCheck(
            crosshair=(183, 44),
            normal_hex="#ad6331"
        )
    ),
    "GEODUDE": Species(
        wild=SpriteCheck(
            crosshair=(173, 48),
            normal_hex="#adb563"
        )
    ),
    "JIGGLYPUFF": Species(
        wild=SpriteCheck(
            crosshair=(180, 54),
            normal_hex="#7363de"
        )
    ),
    "KAKUNA": Species(
        wild=SpriteCheck(
            crosshair=(174, 56),
            normal_hex="#8c7b00"
        )
    ),
    "MANKEY": Species(
        wild=SpriteCheck(
            crosshair=(178, 52),
            normal_hex="#f7deb5"
        )
    ),
    "METAPOD": Species(
        wild=SpriteCheck(
            crosshair=(174, 56),
            normal_hex="#9cd64a"
        )
    ),
    "NIDORAN♀": Species(
        wild=SpriteCheck(
            crosshair=(174, 56),
            normal_hex="#94cebd"
        )
    ),
    "NIDORAN♂": Species(
        wild=SpriteCheck(
            crosshair=(174, 56),
            normal_hex="#63426b"
        )
    ),
    "PARAS": Species(
        wild=SpriteCheck(
            crosshair=(168, 46),
            normal_hex="#ff7b7b"
        )
    ),
    "PIDGEY": Species(
        wild=SpriteCheck(
            crosshair=(174, 53),
            normal_hex="#ce8c63"
        )
    ),
    "PIKACHU": Species(
        wild=SpriteCheck(
            crosshair=(174, 56),
            normal_hex="#ffef00"
        )
    ),
    "RATTATA": Species(
        wild=SpriteCheck(
            crosshair=(174, 53),
            normal_hex="#b573b5"
        )
    ),
    "SPEAROW": Species(
        wild=SpriteCheck(
            crosshair=(182, 50),
            normal_hex="#f7525a"
        )
    ),
    "SUICUNE": Species(
        wild=SpriteCheck(
            crosshair=(174, 53),
            normal_hex="#5a73d6"
        )
    ),
    "WEEDLE": Species(
        wild=SpriteCheck(
            crosshair=(174, 56),
            normal_hex="#efad42"
        )
    ),
    "ZUBAT": Species(
        wild=SpriteCheck(
            crosshair=(173, 51),
            normal_hex="#6b8cbd"
        )
    )
}