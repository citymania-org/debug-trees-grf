from pathlib import Path
import os
from PIL import Image, ImageDraw

import nml

SPRITE_SIZE = (20, 45)
NUMBERS_SHEET = Image.open('numbers.png')
NUMBERS = [NUMBERS_SHEET.crop((i * 11, 0, i * 11 + 11, 11)) for i in range(20)]
NUMBERS_MASK = [Image.eval(img, (lambda a: 255 if a == 1 else 1)).convert('1') for img in NUMBERS]


class TreeSprite(nml.BaseSprite):
    def __init__(self, sprite_id, index, stage, climate):
        self.index = index
        self.stage = stage
        self.climate = climate
        super().__init__(sprite_id, *SPRITE_SIZE)
        self.ofs_x = -self.w // 2
        self.ofs_y = -self.h

    def draw(self, img):
        x, y, w, h = self.x, self.y, self.w, self.h
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
        px = (w - s) // 2
        imd = ImageDraw.Draw(img)
        imd.rectangle((x, y, x + w, y + h), fill=0)
        imd.rectangle((x + px, y + h - s - 1, x + w - px, y + h - 1), fill=color, outline=1)
        for i in range(self.stage - 1):
            imd.rectangle((x + px + 1 + i, y + h - s - i * 3 - 4, x + w - px - 1 - i, y + h - s - 1 - i * 3), fill=color, outline=1)
        img.paste(NUMBERS[self.index], (x + px + 1, y + h - s), mask=NUMBERS_MASK[self.index])
        # img.paste(NUMBERS[self.index], (x + px + 1, y + h - s))

    def get_nml(self):
        return (f'replace ({self.sprite_id}, "{self.file}") {{ [{self.x}, {self.y}, {self.w}, {self.h}, {self.ofs_x}, {self.ofs_y}] }}'
                f'  // {self.climate} #{self.index} stage:{self.stage}')


base_path = Path(__file__).parent.absolute()

build_dir = Path("build")
build_dir.mkdir(parents=True, exist_ok=True)
os.chdir(build_dir)

trees = [TreeSprite(1576 + x, x // 7, x % 7 + 1, "temperate") for x in range(7 * 19)]
trees += [TreeSprite(1709 + x, x // 7, x % 7 + 1, "arctic") for x in range(7 * 8)]
trees += [TreeSprite(1765 + x, x // 7, x % 7 + 1, "arctic-snow") for x in range(7 * 8)]
trees += [TreeSprite(1821 + x, x // 7, x % 7 + 1, "tropic") for x in range(7 * 18)]
trees += [TreeSprite(1947 + x, x // 7, x % 7 + 1, "toyland") for x in range(7 * 9)]
trees_ss = nml.SpriteSheet(trees)
trees_ss.make_image("debug-trees.png", columns=7)

lang_dir = Path("lang")
lang_dir.mkdir(exist_ok=True)
with open(lang_dir / "english.lng", "w") as f:
    f.write("##grflangid 0x01\n")
    f.write("STR_GRF_NAME :Debug Trees\n")
    f.write("STR_GRF_DESCRIPTION :Trees for debugging\n")

with open('debug-trees.nml', 'w') as f:
    f.write('''\
grf {
    grfid: "CMDT";
    name: string(STR_GRF_NAME);
    desc: string(STR_GRF_DESCRIPTION);
    version: 2;
    min_compatible_version: 1;
}

''')

    trees_ss.write_nml(f)
