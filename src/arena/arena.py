import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor
from functools import partial

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))

import json

import optuna
from threadsafe_alpha_beta import threadsafe_AI

from checkers import *
from heuristic import *
from util.helpers import *

MAX_MOVES = 150


def write_winning_weights_to_file(score, trial_params):
    with open("src/arena/winning_weights.txt", "a") as file:
        file.write(f"Score: {score}\n")
        json.dump(trial_params, file)
        file.write("\n\n")


def AI_vs_AI_tuning(
    who_moves_first,
    heuristic_white,
    heuristic_black,
    max_depth,
    time_limit,
    initial_board=None,
):
    if time_limit is None:
        time_limit = 1
    if who_moves_first is None:
        who_moves_first = PlayerTurn.BLACK

    if initial_board is None:
        WP, BP, K = get_fresh_board()
    else:
        WP, BP, K = initial_board

    current_player = who_moves_first
    move_count = 0
    game_over = False

    while move_count < MAX_MOVES and not game_over:
        legal_moves = generate_legal_moves(WP, BP, K, current_player)
        num_white_pieces = count_bits(WP)
        num_black_pieces = count_bits(BP)
        if (
            num_white_pieces - num_black_pieces >= 5
        ):  # if the champion has a 4 piece advantage, it's a win
            return {
                "winner": "WHITE",
                "white_men_left": count_bits(WP & ~K),
                "white_kings_left": count_bits(WP & K),
                "black_men_left": count_bits(BP & ~K),
                "black_kings_left": count_bits(BP & K),
                "move_count": move_count,
            }

        if not legal_moves:
            game_over = True
            break

        immediate_move = len(legal_moves) == 1
        if immediate_move:
            best_move = legal_moves[0]
        else:
            best_move, depth_reached = threadsafe_AI(
                (WP, BP, K),
                current_player,
                max_depth=100,
                time_limit=7,
                heuristic=heuristic_black
                if current_player == PlayerTurn.BLACK
                else heuristic_white,
            )

        if best_move is None:
            game_over = True
            break

        WP, BP, K = do_move(WP, BP, K, best_move, current_player)
        current_player = switch_player(current_player)
        move_count += 1

    result = {
        "winner": None if not game_over else switch_player(current_player).name,
        "white_men_left": count_bits(WP & ~K),
        "white_kings_left": count_bits(WP & K),
        "black_men_left": count_bits(BP & ~K),
        "black_kings_left": count_bits(BP & K),
        "move_count": move_count,
    }

    if not game_over:
        result["winner"] = "Draw"

    return result


def objective(trial):
    # Initialize the CONTENDER
    CHAMPION = partial(
        evolve_base,
        man_weight=703.0013689332421,
        king_weight=742.0181308525031,
        chebychev_distance_weight=115.76682955495899,
        verge_king_weight=56.67775009304168,
        mobility_weight=50.1582997888212,
        jump_weight=9.378160411934207,
        capture_safety_weight=94.5652792759392,
        kinged_mult=6.362973149622056,
        land_edge_mult=0.38480787077298406,
        took_king_mult=1.0131168126451606,
        back_row_importance_factor=43.04383692865011,
        back_row_weight=17.874331360077267,
        backwards_backup_factor=45.622932127330245,
        backwards_backup_weight=38.10038709306349,
        center_control_factor=23.61850346296953,
        center_control_weight=23.62445621620175,
        kings_main_diagonal_weight=18.27923086275151,
        men_side_diagonals_weight=11.050875827750238,
        endgame_threshold=6,
        double_corner_weight=115.76682955495899,
        single_corner_weight=115.76682955495899,
        kgw=0,
    )

    CONTENDER = partial(
        evolve_base,
        man_weight=trial.suggest_float("cont_man_weight", 100, 1000),
        king_weight=trial.suggest_float("cont_king_weight", 150, 1000),
        chebychev_distance_weight=trial.suggest_float(
            "cont_chebychev_distance_weight", 0, 200
        ),
        verge_king_weight=trial.suggest_float("cont_verge_king_weight", 0, 200),
        mobility_weight=trial.suggest_float("cont_mobility_weight", 0, 200),
        jump_weight=trial.suggest_float("cont_jump_weight", 0, 10),
        capture_safety_weight=trial.suggest_float("cont_capture_safety_weight", 0, 200),
        kinged_mult=trial.suggest_float("cont_kinged_mult", 0, 10),
        land_edge_mult=trial.suggest_float("cont_land_edge_mult", 0, 10),
        took_king_mult=trial.suggest_float("cont_took_king_mult", 0, 10),
        back_row_importance_factor=trial.suggest_float(
            "cont_back_row_importance_factor", 0, 50
        ),
        back_row_weight=trial.suggest_float("cont_back_row_weight", 0, 150),
        backwards_backup_factor=trial.suggest_float(
            "cont_backwards_backup_factor", 0, 50
        ),
        backwards_backup_weight=trial.suggest_float(
            "cont_backwards_backup_weight", 0, 100
        ),
        center_control_factor=trial.suggest_float("cont_center_control_factor", 0, 50),
        center_control_weight=trial.suggest_float("cont_center_control_weight", 0, 100),
        kings_main_diagonal_weight=trial.suggest_float(
            "cont_kings_main_diagonal_weight", 0, 20
        ),
        men_side_diagonals_weight=trial.suggest_float(
            "cont_men_side_diagonals_weight", 0, 20
        ),
        endgame_threshold=trial.suggest_int("cont_endgame_threshold", 4, 9),
        double_corner_weight=trial.suggest_float("cont_double_corner_weight", 0, 200),
        single_corner_weight=trial.suggest_float("cont_single_corner_weight", 0, 200),
        kgw=trial.suggest_float("cont_kgw", 0, 5),
    )

    # Play the game
    result = AI_vs_AI_tuning(
        PlayerTurn.BLACK,
        heuristic_white=CHAMPION,
        heuristic_black=CONTENDER,
        max_depth=100,
        time_limit=7,
    )

    # Calculate the score based on the result
    if result["winner"] == "BLACK":  # Assuming BLACK is the CONTENDER
        print("\n\nCONTENDOR BEAT THE CHAMPION\n\n")
        score = abs(result["black_men_left"] + result["black_kings_left"]) - (
            result["white_men_left"] + result["white_kings_left"]
        )
        winning_weights = trial.params
        write_winning_weights_to_file(score, winning_weights)
    elif result["winner"] == "WHITE":
        score = -1 * abs(result["black_men_left"] + result["black_kings_left"]) - (
            result["white_men_left"] + result["white_kings_left"]
        )
    else:
        score = 0

    score *= MAX_MOVES / result["move_count"]

    return score


if __name__ == "__main__":
    # Use SQLite as a storage backend
    storage_url = "sqlite:///example.db"
    study = optuna.create_study(direction="maximize", storage=storage_url)

    # Optuna's optimize function will automatically manage parallelization
    study.optimize(objective, n_trials=5, n_jobs=-1)

    print("Best hyperparameters:", study.best_params)
    completed_trials = [
        t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE
    ]

    # Filter successful trials
    successful_trials = [t for t in completed_trials if t.value is not None]

    # Choose the trial with the highest score
    if successful_trials:
        best_trial = max(successful_trials, key=lambda t: t.value)
        print("\n\nDONE!\n\n")
        print("Best successful trial hyperparameters:", best_trial.params)
        print(f"\n\nBEST SCORE: {best_trial.value}\n\n")
