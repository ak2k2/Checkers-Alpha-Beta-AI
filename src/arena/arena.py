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
    with open("src/arena/winning_weights.txt", "w") as file:
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
            num_white_pieces - num_black_pieces >= 4
        ):  # if the champion has a 4 piece advantage, it's a win
            return {
                "winner": "WHITE",
                "white_men_left": count_bits(WP & ~K),
                "white_kings_left": count_bits(WP & K),
                "black_men_left": count_bits(BP & ~K),
                "black_kings_left": count_bits(BP & K),
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
                max_depth=3,
                time_limit=2,
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
    }

    if not game_over:
        result["winner"] = "Draw"

    return result


def objective(trial):
    # Initialize the CONTENDER
    CHAMPION = partial(
        evolve_base,
        man_weight=500,
        king_weight=750,
        chebychev_distance_weight=100,
        verge_king_weight=50,
        mobility_weight=50,
        jump_weight=4,
        capture_safety_weight=50,
        kinged_mult=5,
        land_edge_mult=5,
        took_king_mult=5,
        back_row_importance_factor=24,
        back_row_weight=50,
        backwards_backup_factor=24,
        backwards_backup_weight=50,
        center_control_factor=24,
        center_control_weight=25,
        kings_main_diagonal_weight=10,
        men_side_diagonals_weight=10,
    )

    CONTENDER = partial(
        evolve_base,
        man_weight=trial.suggest_float("cont_man_weight", 0, 1000),
        king_weight=trial.suggest_float("cont_king_weight", 0, 1000),
        chebychev_distance_weight=trial.suggest_float(
            "cont_chebychev_distance_weight", 0, 200
        ),
        verge_king_weight=trial.suggest_float("cont_verge_king_weight", 0, 100),
        mobility_weight=trial.suggest_float("cont_mobility_weight", 0, 100),
        jump_weight=trial.suggest_float("cont_jump_weight", 0, 10),
        capture_safety_weight=trial.suggest_float("cont_capture_safety_weight", 0, 100),
        kinged_mult=trial.suggest_float("cont_kinged_mult", 0, 10),
        land_edge_mult=trial.suggest_float("cont_land_edge_mult", 0, 10),
        took_king_mult=trial.suggest_float("cont_took_king_mult", 0, 10),
        back_row_importance_factor=trial.suggest_float(
            "cont_back_row_importance_factor", 0, 50
        ),
        back_row_weight=trial.suggest_float("cont_back_row_weight", 0, 100),
        backwards_backup_factor=trial.suggest_float(
            "cont_backwards_backup_factor", 0, 50
        ),
        backwards_backup_weight=trial.suggest_float(
            "cont_backwards_backup_weight", 0, 100
        ),
        center_control_factor=trial.suggest_float("cont_center_control_factor", 0, 50),
        center_control_weight=trial.suggest_float("cont_center_control_weight", 0, 50),
        kings_main_diagonal_weight=trial.suggest_float(
            "cont_kings_main_diagonal_weight", 0, 20
        ),
        men_side_diagonals_weight=trial.suggest_float(
            "cont_men_side_diagonals_weight", 0, 20
        ),
    )

    # Play the game
    result = AI_vs_AI_tuning(
        PlayerTurn.BLACK,
        heuristic_white=CHAMPION,
        heuristic_black=CONTENDER,
        max_depth=20,
        time_limit=1,
    )

    # Calculate the score based on the result
    if result["winner"] == "BLACK":  # Assuming BLACK is the CONTENDER
        score = (result["black_men_left"] + result["black_kings_left"]) - (
            result["white_men_left"] + result["white_kings_left"]
        )
        if score > 0:
            print("\n\nCONTENDOR BEAT THE CHAMPION\n\n")
            winning_weights = trial.params
            write_winning_weights_to_file(score, winning_weights)
    else:
        score = 0  # Loss or draw results in a score of 0

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
