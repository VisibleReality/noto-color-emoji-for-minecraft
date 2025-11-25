import json
import os
import re
from itertools import batched

from PIL import Image

emoji_images_path = "noto-emoji/png/72"

grid_width = 38
grid_height = 38


class Emoji:
	def __init__ (self, image: Image, codepoint: int):
		self.image: Image = image
		self.codepoint: int = codepoint


def generate_emoji (path) -> list[Emoji]:
	emoji_filename_regex = re.compile(r"^emoji_u([0-9a-f]{4,5})\.png$")

	paths: list[str] = os.listdir(path)

	emoji: list[Emoji] = []

	for path in paths:
		match = emoji_filename_regex.match(path)

		if not match:
			continue  # Skip any paths for non-single character emoji

		codepoint = int(match.group(1), base = 16)

		if codepoint < 255:
			continue  # Skip non-emoji characters

		emoji.append(Emoji(Image.open(emoji_images_path + "/" + path), codepoint))

	return emoji


def create_atlas (emoji: list[Emoji], width: int, height: int) -> Image:
	assert len(emoji) <= width * height

	w, h = emoji[0].image.size
	grid = Image.new('RGBA', size = (width * w, height * h), color = (0, 0, 0, 0))

	for i, emoji in enumerate(emoji):
		grid.paste(emoji.image, box = (i % width * w, i // height * h))
	return grid


def create_metadata (emoji: list[Emoji], width: int, height: int) -> dict:
	assert len(emoji) <= width * height

	metadata = {"providers": [
		{
			"type": "bitmap",
			"file": "minecraft:font/emoji.png",
			"height": 8,
			"ascent": 8,
			"chars": []
		},
		{
			"type": "space",
			"advances": {
				"\u200d": 0,
				"\ufe0f": 0
			}
		}
	]}

	for line in batched(emoji, width):
		chars = []
		for e in line:
			chars.append(chr(e.codepoint))

		while len(chars) < width:
			chars.append(chr(0))

		metadata["providers"][0]["chars"].append("".join(chars))

	return metadata


def main ():
	emoji: list[Emoji] = generate_emoji(emoji_images_path)
	
	print(len(emoji))

	atlas: Image = create_atlas(emoji, grid_width, grid_height)

	metadata = create_metadata(emoji, grid_width, grid_height)

	atlas.save("emoji.png")

	with open("default.json", "w") as f:
		f.write(json.dumps(metadata))


if __name__ == "__main__":
	main()
