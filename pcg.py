from itertools import product
from collections import defaultdict
import json
from pprint import pprint
from turtle import left
from PIL import Image
from solver import solve

cardinals = ['n', 's', 'e', 'w']
directions = ['n', 's', 'e', 'w', 'nw', 'ne', 'sw', 'se']
opposite = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e', 'nw': 'se', 'se': 'nw', 'ne': 'sw', 'sw': 'ne'}
dir_adjacencies = defaultdict(lambda: defaultdict(list))

# for dir1 in directions:
#     for side in cardinals:
#         if dir1 == side:
#             dir_adjacencies[dir1][side] = [
#                 dir2 for dir2 in directions 
#                 if opposite[side] in dir2
#             ]
#         if dir1 == opposite['side']:
#             dir_adjacencies[dir1][side] = [side]
#         elif dir1 in cardinals:
#             dir_adjacencies[dir1][side] = [
#                 dir2 for dir2 in directions 
#                 if dir2 == dir1 or (dir1 in dir2 )
#             ]

dir_adjacencies = {
    'n': {
        'left': {'n', 'nw'},
        'right': {'n', 'ne'},
        'up': {'s', 'sw', 'se'},
        'down': {'s', 'c'},
    },
    's': {
        'left': {'s', 'sw'},
        'right': {'s', 'se'},
        'up': {'n', 'c'},
        'down': {'n', 'nw', 'ne'},
    },
    'e': {
        'left': {'w', 'c'},
        'right': {'w', 'nw', 'sw'},
        'up': {'e', 'ne'},
        'down': {'e', 'se'},
    },
    'w': {
        'left': {'e', 'ne', 'se'},
        'right': {'e', 'c'},
        'up': {'w', 'nw'},
        'down': {'w', 'sw'},
    },
    'nw': {
        'left': {'e', 'se', 'ne'},
        'right': {'n', 'ne'},
        'up': {'s', 'se', 'sw'},
        'down': {'w', 'sw'}
    },
    'ne': {
        'left': {'n', 'nw'},
        'right': {'w', 'sw', 'nw'},
        'up': {'s', 'se', 'sw'},
        'down': {'e', 'se'}
    },
    'sw': {
        'left': {'e', 'ne', 'se'},
        'right': {'s', 'se'},
        'up': {'w', 'nw'},
        'down': {'n', 'ne', 'nw'}
    },
    'se': {
        'left': {'s', 'sw'},
        'right': {'w', 'nw', 'sw'},
        'down': {'n', 'ne', 'nw'},
        'up': {'e', 'ne'},
    },
    'c': {
        'left': {'c', 'w'},
        'right': {'c', 'e'},
        'down': {'c', 's'},
        'up': {'c', 'n'},
    }
}

def generate(input_folder):
    WIDTH = 20
    HEIGHT = 20

    tiles_to_img, left_adj, right_adj, up_adj, down_adj, weights = parse_config(input_folder)

    layout = solve(WIDTH, HEIGHT, left_adj, right_adj, up_adj, down_adj, weights)
    visualize(layout, input_folder, tiles_to_img)

def parse_config(input_folder, better_config=False):
    tiles_to_img = {}
    left_adj = defaultdict(set)
    right_adj = defaultdict(set)
    up_adj = defaultdict(set)
    down_adj = defaultdict(set)
    weights = {}
    if better_config:
        id_to_tiles = {}
        cls_to_tiles = defaultdict(list)

        with open(f'{input_folder}/better_config.json') as config_file:
            config = json.loads(config_file.read())

        for tile in config['tiles']:
            tile_id = tile['id']
            id_to_tiles[tile_id] = tile
            tiles_to_img[tile_id] = tile['img']
            cls_to_tiles[tile['class']].append(tile_id)
            weights[tile_id] = tile['weight']

        for tile_id in id_to_tiles:
            tile = id_to_tiles[tile_id]
            cls_tiles = cls_to_tiles[tile['class']]
            for dir in tile['directions']:
                left_adj[tile_id].update(
                    tile2 for tile2 in cls_tiles
                    if not dir_adjacencies[dir]['left'].isdisjoint(id_to_tiles[tile2]['directions'])
                )
                left_adj[tile_id].update(
                    tile2_id for tile2_id, tile2 in id_to_tiles.items()
                    if tile2_id not in cls_tiles
                    if 'w' in dir and any('e' in dir2 for dir2 in tile2['directions'])
                )
                right_adj[tile_id].update(
                    tile2 for tile2 in cls_tiles
                    if not dir_adjacencies[dir]['right'].isdisjoint(id_to_tiles[tile2]['directions'])
                )
                right_adj[tile_id].update(
                    tile2_id for tile2_id, tile2 in id_to_tiles.items()
                    if tile2_id not in cls_tiles
                    if 'e' in tile['directions'] and any('w' in dir2 for dir2 in tile2['directions'])
                )
                up_adj[tile_id].update(
                    tile2 for tile2 in cls_tiles
                    if not dir_adjacencies[dir]['up'].isdisjoint(id_to_tiles[tile2]['directions'])
                )
                up_adj[tile_id].update(
                    tile2_id for tile2_id, tile2 in id_to_tiles.items()
                    if tile2_id not in cls_to_tiles
                    if 'n' in tile['directions'] and any('s' in dir2 for dir2 in tile2['directions'])
                )
                down_adj[tile_id].update(
                    tile2 for tile2 in cls_tiles
                    if not dir_adjacencies[dir]['down'].isdisjoint(id_to_tiles[tile2]['directions'])
                )
                down_adj[tile_id].update(
                    tile2_id for tile2_id, tile2 in id_to_tiles.items()
                    if tile2_id not in cls_tiles
                    if 's' in tile['directions'] and any('n' in dir2 for dir2 in tile2['directions'])
                )
                #     match dir:
                #         case 'n':
                #             left_adj[tile].update(
                #                 tile for tile in tiles 
                #                 if {'n', 'nw'}.issubset(tile['direction'])
                #             )
                #             right_adj[tile].update(
                #                 tile for tile in tiles 
                #                 if {'n', 'ne'}.issubset(tile['direction'])
                #             )
                        
                #         case 's':

        return tiles_to_img, left_adj, right_adj, up_adj, down_adj, weights     

    with open(f'{input_folder}/config.json') as config_file:
        config = json.loads(config_file.read())

    for tile in config['tiles']:
        tile_id = tile['id']
        tiles_to_img[tile_id] = tile['img']
        left_adj[tile_id] = tile['allowed_left']
        right_adj[tile_id] = tile['allowed_right']
        up_adj[tile_id] = tile['allowed_up']
        down_adj[tile_id] = tile['allowed_down']
        weights[tile_id] = tile['weight']

    return tiles_to_img, left_adj, right_adj, up_adj, down_adj, weights

def visualize(layout, input_folder, tiles_to_img_path):
    # pprint(layout)
    tiles_to_img_obj = {}
    for tile, img_path in tiles_to_img_path.items():
        img = Image.open(f'{input_folder}/{img_path}')
        tiles_to_img_obj[tile] = img
    
    tile_width = img.width
    tile_height = img.height
    layout_width = len(layout[0])
    layout_height = len(layout)


    output_img = Image.new('RGB', (tile_width * layout_width, tile_height * layout_height))
    for row, col in product(range(layout_height), range(layout_width)):
        tile = layout[row][col]
        tile_img = tiles_to_img_obj[tile]
        output_img.paste(tile_img, (col * tile_width, row * tile_height))

    output_img.save('output.png')

generate('inputs/simple_knots')
