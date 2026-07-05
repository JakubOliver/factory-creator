from factory_creator.graph_to_matrix import Grid, GridEntry, GraphToMatrix

import prettytable

# Until the pytoml is created and added packege by pip install -e .
# the test have to be run by command PYTHONPATH=src pytest
# PYTHONPATH=src pytest -s     for seeing outputs

def print_grid(grid: dict):
    min_x = min(x for x, y in grid.keys())
    min_y = min(y for x, y in grid.keys())

    max_x = max(x for x, y in grid.keys())
    max_y = max(y for x, y in grid.keys())

    header = ["#"]
    for x in range(min_x, max_x + 1):
        header.append(str(x))

    table = prettytable.PrettyTable(header)

    for y in range(min_y, max_y + 1):
        row = [str(y)]
        for x in range(min_x, max_x + 1):
            if (x, y) not in grid.keys():
                row.append("_")
            else:
                row.append(grid[(x, y)])

        table.add_row(row)

    print(table)


def test_under_obstacle():
    # _ _ | | _
    # X _ | S |
    # _ _ | | _

    grid = Grid()
    final_cord = (1,1)
    start_cord = (1,3)

    grid[final_cord] = GridEntry("assembler-1")
    grid[start_cord] = GridEntry("assembler-2")

    grid.set_occupied((0,2))
    grid.set_occupied((0,3))
    grid.set_occupied((1,2))
    grid.set_occupied((1,4))
    grid.set_occupied((2,2))
    grid.set_occupied((2,3))

    from_cords = [start_cord]
    to_cords = [final_cord]
    is_in_successor = lambda cord : cord in to_cords

    active_cord, visited_matrix = GraphToMatrix.a_star(
        from_cords=from_cords,
        is_in_successor=is_in_successor,
        to_cords=to_cords,
        grid=grid
    )

    print(active_cord)
    print_grid(visited_matrix)

    assert active_cord == final_cord
    assert visited_matrix[final_cord] == 1

def test_under_obstacle2():
    # _ _ | _ _
    # X _ | _ S
    # _ _ | _ _

    grid = Grid()
    final_cord = (1,1)
    start_cord = (1,3)

    grid[final_cord] = GridEntry("assembler-1")
    grid[start_cord] = GridEntry("assembler-2")

    grid.set_occupied((0,2))
    grid.set_occupied((1,2))
    grid.set_occupied((2,2))

    from_cords = [start_cord]
    to_cords = [final_cord]
    is_in_successor = lambda cord : cord in to_cords

    active_cord, visited_matrix = GraphToMatrix.a_star(
        from_cords=from_cords,
        is_in_successor=is_in_successor,
        to_cords=to_cords,
        grid=grid
    )

    print(active_cord)
    print_grid(visited_matrix)

    assert active_cord == final_cord
    assert visited_matrix[final_cord] == 1

def test_under_obstacle3():
    grid = Grid()
    grid.add_source((10, 10), "barrel")
    grid.add_source((20, 20), "barrel")

    cords = set()

    k = 10
    for i in range(k):
        cords.add((0, i))
        cords.add((k - 1, i))
        cords.add((i, 0))
        cords.add((i, k - 1))

    for cord in cords:
        grid.add_transportation(
            cord=cord,
            name="transportation-belt",
            orientation=0,
            from_cord=(10, 10),
            to_cord=(20, 20)
        )

    grid.add_source((4, 5), "barrel")
    grid.add_source((5, 15), "barrel")

    GraphToMatrix.find_path(
        (4, 5),
        [(4, 5)],
        lambda x: x == (4, 5),
        (5, 15),
        [(5, 15)],
        lambda x: x == (5, 15),
        grid
    )

    print(grid)

    assert True == False #TODO: remove dummy