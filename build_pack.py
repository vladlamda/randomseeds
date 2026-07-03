"""Generates the random_chunk_seeds datapack files that depend on vanilla 26.2 data."""
import json
import random
from pathlib import Path

ROOT = Path(__file__).parent
PACK = ROOT / "random_chunk_seeds"

rng = random.Random(20260702)

# --- 1. Biome list (all 66 biomes in 26.2) ---
biomes = json.loads((ROOT / "biomes_262.json").read_text(encoding="utf-8"))
biomes = [f"minecraft:{b}" for b in biomes]

# --- 2. multi_noise biome source: a 20x20 grid over (temperature, humidity)
#     climate space. The 66 biomes are assigned to the 400 cells in shuffled
#     round-robin order, so climate-neighboring cells are unrelated biomes.
#     Combined with the high-frequency temperature/humidity noises in the
#     noise settings below, this yields a fully random ~chunk-sized patchwork
#     with no diagonal alignment (unlike the checkerboard biome source). ---
N = 20
SPAN = 0.8
edges = [-SPAN + 2 * SPAN * i / N for i in range(N + 1)]

cells = [(i, j) for i in range(N) for j in range(N)]
rng.shuffle(cells)
assignment = biomes * (len(cells) // len(biomes) + 1)
rng.shuffle(assignment)

entries = []
for (i, j), biome in zip(cells, assignment):
    entries.append({
        "biome": biome,
        "parameters": {
            "temperature": [edges[i], edges[i + 1]],
            "humidity": [edges[j], edges[j + 1]],
            "continentalness": [-2.0, 2.0],
            "erosion": [-2.0, 2.0],
            "weirdness": [-2.0, 2.0],
            "depth": [-2.0, 2.0],
            "offset": 0.0,
        },
    })

dimension = {
    "type": "minecraft:overworld",
    "generator": {
        "type": "minecraft:noise",
        "settings": "random_chunks:scrambled",
        "biome_source": {
            "type": "minecraft:multi_noise",
            "biomes": entries,
        },
    },
}

# --- 3. Custom noise settings: vanilla overworld with the climate router
#     entries replaced by high-frequency noises so the biome lookup above
#     becomes effectively random per ~chunk. Terrain is untouched. ---
noise_settings = json.loads(
    (ROOT / "vanilla_noise_settings_262.json").read_text(encoding="utf-8"))
for router_key, noise_id in [("temperature", "random_chunks:biome_temperature"),
                             ("vegetation", "random_chunks:biome_humidity")]:
    noise_settings["noise_router"][router_key] = {
        "type": "minecraft:flat_cache",
        "argument": {
            "type": "minecraft:cache_2d",
            "argument": {
                "type": "minecraft:noise",
                "noise": noise_id,
                "xz_scale": 1.0,
                "y_scale": 0.0,
            },
        },
    }

# Distinct noise files get independent seeds (seeded by their registry ID).
climate_noise = {"firstOctave": -9, "amplitudes": [1.0, 0.2]}

# --- 4. Override vanilla overworld/offset: keep the whole vanilla spline,
#     add a high-frequency scramble noise inside the flat_cache/cache_2d
#     wrappers so depth, sloped_cheese and preliminary_surface_level all
#     stay consistent with each other ---
offset = json.loads((ROOT / "vanilla_offset_262.json").read_text(encoding="utf-8"))
assert offset["type"] == "minecraft:flat_cache"
assert offset["argument"]["type"] == "minecraft:cache_2d"
inner = offset["argument"]["argument"]
offset["argument"]["argument"] = {
    "type": "minecraft:add",
    "argument1": inner,
    "argument2": "random_chunks:scramble_offset",
}

# --- 5. Village biome tags: allow all biomes so villages always generate ---
village_tag = {"replace": True, "values": biomes}
village_types = ["village_plains", "village_desert", "village_savanna",
                 "village_snowy", "village_taiga"]

files = {
    PACK / "data/minecraft/dimension/overworld.json": dimension,
    PACK / "data/minecraft/worldgen/density_function/overworld/offset.json": offset,
    PACK / "data/random_chunks/worldgen/noise_settings/scrambled.json": noise_settings,
    PACK / "data/random_chunks/worldgen/noise/biome_temperature.json": climate_noise,
    PACK / "data/random_chunks/worldgen/noise/biome_humidity.json": climate_noise,
}
for v in village_types:
    files[PACK / f"data/minecraft/tags/worldgen/biome/has_structure/{v}.json"] = village_tag

for path, content in files.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")

print(f"{len(biomes)} biomes in {len(entries)} climate cells")
