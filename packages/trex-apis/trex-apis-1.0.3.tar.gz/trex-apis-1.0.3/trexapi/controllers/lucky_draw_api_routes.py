

import random, logging
from flask.blueprints import Blueprint


lucky_draw_api_bp = Blueprint('lucky_draw_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/lucky-draw')

logger = logging.getLogger('debug')

@lucky_draw_api_bp.route('/draw', methods=['GET'])
def draw():

    # Define the prizes and their respective weights (i.e., the likelihood of winning each prize)
    prizes = {"First Prize": 1, "Second Prize": 4, "Third Prize": 10, "Consolation Prize": 40, "Try again": 144}
    
    # Get the total weight of all the prizes
    total_weight = sum(prizes.values())
    
    # Generate a random number between 1 and the total weight
    random_num = random.randint(1, total_weight)
    
    # Determine the prize based on the random number and the weights of the prizes
    draw_prize = None
    for prize, weight in prizes.items():
        if random_num <= weight:
            print(f"You've won the {prize}!")
            draw_prize = prize
            break
        else:
            random_num -= weight
            
    return draw_prize, 200
        
        