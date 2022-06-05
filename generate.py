from pathlib import Path
import os
from PIL import Image, ImageDraw

import grf

SPRITE_SIZE = (20, 45)
NUMBERS_SHEET = Image.open('numbers.png')
NUMBERS = [NUMBERS_SHEET.crop((i * 11, 0, i * 11 + 11, 11)) for i in range(20)]
NUMBERS_MASK = [Image.eval(img, (lambda a: 255 if a == 1 else 1)).convert('1') for img in NUMBERS]


class TreeSprite(grf.GraphicsSprite):
    def __init__(self, index, stage, climate):
        w, h = SPRITE_SIZE
        super().__init__(w, h, xofs=-w // 2, yofs=-h)
        self.index = index
        self.stage = stage
        self.climate = climate

    def get_image(self):
        green_colors = [0x1c, 0x24, 0x57, 0xd0, 0x5c, 0x1d, 0x63, 0xd0]  # min 8 (arctic)
        blue_colors = [0x84, 0x8d, 0x97, 0x9e, 0xac, 0xcd, 0xd6, 0xa1]  # min 8 (arctic-snow)
        misc_colors = [0xb6, 0xbe, 0x39, 0x41, 0x3f, 0x4d, 0x77, 0xa5, 0xad, 0x15]  # min 10 (tropic)
        color = {
            'temperate': green_colors + blue_colors[:4] + misc_colors,
            'arctic': green_colors,
            'arctic-snow': blue_colors,
            'tropic': green_colors + misc_colors,
            'toyland': misc_colors,
        }[self.climate][self.index]
        # color = {"arctic": 0x8C, "arctic-snow": 0x98, "temperate": 0x57, "tropic": 0x43, "toyland": 0xA5}[self.climate]
        s = 12
        px = (self.w - s) // 2
        img = Image.new('P', (self.w, self.h))
        img.putpalette(grf.PALETTE)
        imd = ImageDraw.Draw(img)
        imd.rectangle((px, self.h - s - 1, self.w - px, self.h - 1), fill=color, outline=1)
        for i in range(self.stage - 1):
            imd.rectangle((px + 1 + i, self.h - s - i * 3 - 4, self.w - px - 1 - i, self.h - s - 1 - i * 3), fill=color, outline=1)
        img.paste(NUMBERS[self.index], (px + 1, self.h - s), mask=NUMBERS_MASK[self.index])
        return img, 8


g = grf.NewGRF(
    grfid=b'CMDT',
    name='Debug Trees',
    description='Trees for debugging',
    version=2,
    min_compatible_version=1,
    url='https://github.com/citymania-org/debug-trees-grf',
)

RANGES = {
    "temperate": (1576, 19),
    "arctic": (1709, 8),
    "arctic-snow": (1765, 8),
    "tropic": (1821, 18),
    "toyland": (1947, 9),
}

g.add(grf.ReplaceOldSprites([(first, count * 7) for first, count in RANGES.values()]))
for climate, (_, amount) in RANGES.items():
    for x in range(7 * amount):
        g.add(TreeSprite(x // 7, x % 7 + 1, climate))

base_path = Path(__file__).parent.absolute()
build_dir = base_path / 'build'
build_dir.mkdir(exist_ok=True)
g.write(build_dir / 'debug-trees.grf')
