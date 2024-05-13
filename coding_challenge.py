import random
import json
import pandas as pd
from aws_lambda_powertools import Logger
from collections import deque


logger = Logger()

# def queue_decrement(arr, coordinates,checked,value):

def recursive_decrement(arr, coordinates,checked, value):
    # Get all possible adjacent coordinates (pull out x and y values to make possible_coords definition cleaner)
    x = coordinates[0]
    y = coordinates[1]
    
    # Possible coordinates should be +1 and -1 for x and y
    possible_coords = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]

    # shuffle to make a prettier graph
    # random.shuffle(possible_coords)

    # Loop through coords and check if they're in bounds and not checked'
    for coord in possible_coords:
        if coord in checked:
            continue
        elif 0 <= coord[0] <=24 and 0 <= coord[1] <= 24:
            # Mark coord as checked
            checked.append(coord)
            try:
                new_val = value - .01
                arr[coord[0]][coord[1]] = new_val
                recursive_decrement(arr, coord, checked, new_val)

            except Exception as error:
                print(f"\ncoord: {coord}")
                print("An error occurred:", error)
        else:
            continue
    return arr

@logger.inject_lambda_context
def get_grid(event, context):
    checked = []
    # Generate initial array
    rows, cols = (24, 24) # TODO maybe get rows and cols from event
    arr = [[0 for i in range(cols)] for j in range(rows)]

    # Get Random starting position.
    rand_x = random.randint(0, rows-1)
    rand_y = random.randint(0, cols-1)
    logger.info(f"starting position: {rand_x, rand_y}")
    
    # Set starting position to 1 and add starting position to checked.
    arr[rand_x][rand_y] = 1
    checked.append((rand_x, rand_y))

    # Call recursive_decrement function and use the returned array.
    solved_arr = recursive_decrement(arr, [rand_x, rand_y],checked,arr[rand_x][rand_y])

    # Convert array to dataframe so we can get the smallest value
    # .min() returns a series, so we need to get the min of the series with another .min()
    lowest = pd.DataFrame(solved_arr).min().min()
    
    body = {
        "grid": solved_arr,
        "lowest": lowest,
        "starting": f"{rand_x,rand_y}"
    }
    # build response with cors headers
    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(body)
    }
    return response
