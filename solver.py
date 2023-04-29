from random import choices, randint
from ortools.sat.python import cp_model
from itertools import product

AdjList = dict[int, list[int]]

def solve(
    width: int, 
    height: int, 
    left_adj: AdjList, 
    right_adj: AdjList, 
    up_adj: AdjList, 
    down_adj: AdjList,
    weights: dict[int, int]
) -> list[list[int]]:
    tiles = left_adj.keys()

    model = cp_model.CpModel()
    has_tile = {}
    for row, col in product(range(height), range(width)):
        for tile in tiles:
            has_tile[row, col, tile] = model.NewBoolVar(f'has_tile{row, col, tile}')

    # One tile per position
    for row, col in product(range(height), range(width)):
        model.Add(
            sum(has_tile[row, col, tile] for tile in tiles) == 1
        )

    # Use all tiles
    for tile in tiles:
        model.Add(
            sum(
                has_tile[row, col, tile] 
                for row, col in product(range(height), range(width))
            )   >= 1
        )
    
    # Adjacency constraints
    for row, col in product(range(height), range(width)):
        for tile in tiles:
            # left
            if col > 0:
                left_adj_satisfied = model.NewBoolVar('')
                model.AddImplication(has_tile[row, col, tile], left_adj_satisfied)
                
                model.AddBoolOr([
                    has_tile[row, col-1, adj_tile] for adj_tile in left_adj[tile]
                ]).OnlyEnforceIf(left_adj_satisfied)
            
            # right
            if col < width-1:
                right_adj_satisfied = model.NewBoolVar('')
                model.AddImplication(has_tile[row, col, tile], right_adj_satisfied)
                
                model.AddBoolOr([
                    has_tile[row, col+1, adj_tile] for adj_tile in right_adj[tile]
                ]).OnlyEnforceIf(right_adj_satisfied)
            
            # up
            if row > 0:
                up_adj_satisfied = model.NewBoolVar('')
                model.AddImplication(has_tile[row, col, tile], up_adj_satisfied)
                
                model.AddBoolOr([
                    has_tile[row-1, col, adj_tile] for adj_tile in up_adj[tile]
                ]).OnlyEnforceIf(up_adj_satisfied)
            
            # down
            if row < height-1:
                down_adj_satisfied = model.NewBoolVar('')
                model.AddImplication(has_tile[row, col, tile], down_adj_satisfied)
                
                model.AddBoolOr([
                    has_tile[row+1, col, adj_tile] for adj_tile in down_adj[tile]
                ]).OnlyEnforceIf(down_adj_satisfied)

    total_weight = sum(weights.values())
    normalized_weights = {tile: weight / total_weight for tile, weight in weights.items()}
    tiles_list = list(tiles)
    normalized_weights_list = [normalized_weights[tile] for tile in tiles_list]
    
    # random hinting for artistic value
    for row, col in product(range(height), range(width)):
        if randint(0, 10) == 0:
            weighted_random_tile, = choices(tiles_list, normalized_weights_list, k=1)
            model.AddHint(has_tile[row, col, weighted_random_tile], 1)

    score = 0
    for tile in tiles_list[1:]:
        times_used = sum(
            has_tile[row, col, tile]
            for row, col in product(range(height), range(width))
        )
        diff = model.NewIntVar(-width * height, width * height, '')
        abs_diff = model.NewIntVar(0, width * height, '')
        expected_times_used = int(normalized_weights[tile] * width * height)
        model.Add(diff == times_used - expected_times_used)
        model.AddAbsEquality(abs_diff, diff)
        score += abs_diff
        
    model.Minimize(score)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    # solver.parameters.max_number_of_conflicts = 0
    solver.parameters.preferred_variable_order = solver.parameters.IN_RANDOM_ORDER
    code = solver.Solve(model)
    if code in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        print('Score:', solver.Value(score))
        output_grid = [[None] * width for _ in range(height)]
        for row, col in product(range(height), range(width)):
            for tile in tiles:
                if solver.Value(has_tile[row, col, tile]):
                    output_grid[row][col] = tile
    
        return output_grid

    elif code == cp_model.UNKNOWN:
        raise ValueError('Timed out before a solution was found.')

    raise ValueError('No solution!')