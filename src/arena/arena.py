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


NET_TRIALS = 100
MAX_MOVES = 100
TIME_LIMIT = 5
MAX_DEPTH = 20
NUM_RANDOM_STARTING_TRIALS = 20


def write_winning_weights_to_file(score, trial_params):
    # open the file and clear it

    with open("src/arena/winning_weights.txt", "w") as file:
        file.truncate(0)
        file.write(f"Score: {score}\n")
        file.write(json.dumps(trial_params, indent=4))
        file.write("\n\n")


def AI_vs_AI_tuning(
    who_moves_first,
    heuristic_white,
    heuristic_black,
    max_depth=None,
    time_limit=None,
    initial_board=None,
    one_piece_down=False,
):
    if time_limit is None:
        time_limit = 1
    if who_moves_first is None:
        who_moves_first = PlayerTurn.BLACK

    if initial_board is None:
        WP, BP, K = get_fresh_board()
        if one_piece_down:
            BP = remove_piece_by_pdntext(BP, "C3")  # black should have a disadvantage
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
                max_depth=MAX_DEPTH,
                time_limit=TIME_LIMIT,
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
    # CHAMPION = partial(
    #     evolve_base_B,
    #     man_weight=221.16517634218417,
    #     king_weight=796.5566144637147,
    #     chebychev_distance_weight=33.03129353308223,
    #     verge_king_weight=22.23650010068536,
    #     mobility_weight=96.05774298185752,
    #     jump_weight=6.1915450814325155,
    #     capture_safety_weight=100.4122019695803,
    #     kinged_mult=6.990009530742195,
    #     land_edge_mult=8.535678462318163,
    #     took_king_mult=4.996558460665898,
    #     back_row_importance_factor=-41.38374019780294,
    #     back_row_weight=118.51889621145315,
    #     backwards_backup_factor=-30.848845657429024,
    #     backwards_backup_weight=83.87206305189319,
    #     center_control_factor=-8.032755208608712,
    #     center_control_weight=31.567795693577306,
    #     kings_main_diagonal_weight=-32.453989920069844,
    #     men_side_diagonals_weight=76.91067085490019,
    #     endgame_threshold=9,
    #     double_corner_weight=133.7288473924311,
    #     single_corner_weight=34.38684084057926,
    #     kgw=-0.47197781248849324,
    #     mgw=3.6132652205727087,
    #     maj_loss_thresh=0.05771824979127871,
    #     attack_weight=8.742653188749493,
    #     agw=0.03826827864720439,
    #     mix_row_not_box_weight=157.65286584499088,
    #     mrnbw=-4.983778283889592,
    #     promotion_weight=128.56156093143366,
    #     pgw=-0.6329411162600866,
    #     cssw=-3.5655993169434708,
    #     vkg=1.464460710636847,
    #     mbgw=-4.195871570387243,
    # )
    CHAMPION = partial(old_heuristic)

    CONTENDER = partial(
        evolve_base_B,
        man_weight=trial.suggest_float("cont_man_weight", 100, 2000),
        man_growth_decay=trial.suggest_float("cont_man_growth_decay", -1.0, 1.0),
        king_weight=trial.suggest_float("cont_king_weight", 100, 2000),
        king_growth_decay=trial.suggest_float("cont_king_growth_decay", -1.0, 1.0),
        back_row_weight=trial.suggest_float("cont_back_row_weight", 0, 300),
        back_growth_decay=trial.suggest_float("cont_back_growth_decay", -1.0, 1.0),
        capture_weight=trial.suggest_float("cont_capture_weight", 0, 300),
        capture_growth_decay=trial.suggest_float(
            "cont_capture_growth_decay", -1.0, 1.0
        ),
        kinged_mult=trial.suggest_float("cont_kinged_mult", 0, 5.0),
        land_edge_mult=trial.suggest_float("cont_land_edge_mult", 0, 5.0),
        took_king_mult=trial.suggest_float("cont_took_king_mult", 0, 5.0),
        distance_weight=trial.suggest_float("cont_distance_weight", 0, 100),
        distance_growth_decay=trial.suggest_float(
            "cont_distance_growth_decay", -1.0, 1.0
        ),
        mobility_weight=trial.suggest_float("cont_mobility_weight", 0, 300),
        mobility_jump_mult=trial.suggest_float("cont_mobility_jump_mult", 1, 10),
        mobility_growth_decay=trial.suggest_float(
            "cont_mobility_growth_decay", -1.0, 1.0
        ),
        safety_weight=trial.suggest_float("cont_safety_weight", 0, 300),
        safety_growth_decay=trial.suggest_float("cont_safety_growth_decay", -1.0, 1.0),
        double_corner_bonus_weight=trial.suggest_float(
            "cont_double_corner_bonus_weight", 0, 300
        ),
        endgame_threshold=trial.suggest_int("cont_endgame_threshold", 4, 9),
    )

    # Play the game
    result = AI_vs_AI_tuning(
        PlayerTurn.BLACK,
        heuristic_white=CHAMPION,
        heuristic_black=CONTENDER,
        max_depth=MAX_DEPTH,
        time_limit=TIME_LIMIT,
    )

    # Calculate the score based on the result
    if result["winner"] == "BLACK":  # Assuming BLACK is the CONTENDER
        print("\nCONTENDOR BEAT THE CHAMPION\n")
        score = abs(result["black_men_left"] + result["black_kings_left"]) - (
            result["white_men_left"] + result["white_kings_left"]
        )
        stress_result = AI_vs_AI_tuning(
            PlayerTurn.BLACK,
            heuristic_white=CHAMPION,
            heuristic_black=CONTENDER,
            max_depth=MAX_DEPTH,
            time_limit=TIME_LIMIT,
            one_piece_down=True,
        )
        if stress_result["winner"] == "BLACK":
            print("\nSTRESS TEST: CONTENDOR BEAT THE CHAMPION WITH A PIECE DOWN\n")
            score *= 2

    elif result["winner"] == "WHITE":  # WHITE the the OG champion.
        score = -1 * (
            abs(result["black_men_left"] + result["black_kings_left"])
            - (result["white_men_left"] + result["white_kings_left"])
        )
    else:
        score = 0

    score *= MAX_MOVES / result["move_count"]

    return score


def run_tpe_study():
    # Use SQLite as a storage backend
    storage_url = "sqlite:///tpe.db"
    study = optuna.create_study(
        direction="maximize",
        storage=storage_url,
        load_if_exists=True,
        study_name="tpe_checkers",
        sampler=optuna.samplers.TPESampler(
            seed=10,
            n_startup_trials=NUM_RANDOM_STARTING_TRIALS,
            prior_weight=2.0,
            constant_liar=True,
            multivariate=True,
        ),
    )

    # Optuna's optimize function will automatically manage parallelization
    study.optimize(
        objective,
        n_trials=NET_TRIALS,
        n_jobs=-1,
        show_progress_bar=True,
    )

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


def run_nsgaii_study():
    # Use SQLite as a storage backend
    storage_url = "sqlite:///nsg.db"
    study = optuna.create_study(
        direction="maximize",
        storage=storage_url,
        load_if_exists=True,
        study_name="tpe_checkers_nsgai",
        sampler=optuna.samplers.NSGAIIISampler(seed=10),
    )

    # Optuna's optimize function will automatically manage parallelization
    study.optimize(
        objective,
        n_trials=NET_TRIALS,
        n_jobs=-1,
        show_progress_bar=True,
    )

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


run_tpe_study()
