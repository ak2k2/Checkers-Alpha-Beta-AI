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

NET_TRIALS = 200
EARLY_STOP_DEPTH = 20
MAX_MOVES = 60


TIME_LIMIT = 6
NUM_RANDOM_STARTING_TRIALS = 5


def write_winning_weights_to_file(score, trial_params):
    # open the file and clear it

    with open("src/arena/winning_weights.txt", "w") as file:
        file.truncate(0)
        file.write(f"Score: {score}\n")
        file.write(json.dumps(trial_params, indent=4))
        file.write("\n\n")


def PLAY_TUNE(
    who_moves_first,
    heuristic_white,
    heuristic_black,
    max_depth=None,
    time_limit=None,
    one_piece_down=False,
    two_piece_down=False,
    early_stop_depth=EARLY_STOP_DEPTH,
    contender_is_white=False,
):
    if time_limit is None:
        time_limit = 1
    if who_moves_first is None:
        who_moves_first = PlayerTurn.BLACK

    if max_depth is None:
        max_depth = 100

    WP, BP, K = get_fresh_board()
    if not contender_is_white:
        if one_piece_down:
            BP = remove_piece_by_pdntext(BP, "C3")  # black should have a disadvantage
        elif two_piece_down:
            BP = remove_piece_by_pdntext(BP, "C3")
            BP = remove_piece_by_pdntext(BP, "E3")
    elif contender_is_white:
        if one_piece_down:
            WP = remove_piece_by_pdntext(WP, "D6")
        elif two_piece_down:
            WP = remove_piece_by_pdntext(WP, "D6")
            WP = remove_piece_by_pdntext(WP, "F6")

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
        elif (
            num_black_pieces - num_white_pieces >= 5
        ):  # if the challenger has a 4 piece advantage, it's a win
            return {
                "winner": "BLACK",
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
                max_depth=max_depth,
                time_limit=TIME_LIMIT,
                heuristic=heuristic_black
                if current_player == PlayerTurn.BLACK
                else heuristic_white,
                early_stop_depth=early_stop_depth,
            )

        if best_move is None:
            game_over = True
            break

        WP, BP, K = do_move(WP, BP, K, best_move, current_player)
        current_player = switch_player(current_player)
        move_count += 1
        # print(f"Heuristic White: {heuristic_white(WP, BP, K)}")
        # print(f"Heuristic Black: {heuristic_black(WP, BP, K)}")
        # print_board(WP, BP, K)

    result = {
        "winner": None if not game_over else switch_player(current_player).name,
        "white_men_left": count_bits(WP & ~K),
        "white_kings_left": count_bits(WP & K),
        "black_men_left": count_bits(BP & ~K),
        "black_kings_left": count_bits(BP & K),
        "move_count": move_count,
    }

    if not game_over:
        result = {
            "winner": "DRAW",
            "white_men_left": count_bits(WP & ~K),
            "white_kings_left": count_bits(WP & K),
            "black_men_left": count_bits(BP & ~K),
            "black_kings_left": count_bits(BP & K),
            "move_count": move_count,
        }

    return result


def objective(trial):
    CHAMPION = partial(old_heuristic)

    CONTENDER = partial(
        evolve_base_B,
        man_weight=trial.suggest_float("cont_man_weight", 100, 3000),
        man_growth_decay=trial.suggest_float("cont_man_growth_decay", -1.0, 1.0),
        king_weight=trial.suggest_float("cont_king_weight", 100, 3000),
        king_growth_decay=trial.suggest_float("cont_king_growth_decay", -1.0, 1.0),
        back_row_weight=trial.suggest_float("cont_back_row_weight", 0, 1000),
        back_growth_decay=trial.suggest_float("cont_back_growth_decay", -1.0, 1.0),
        capture_weight=trial.suggest_float("cont_capture_weight", 0, 1000),
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
        mobility_weight=trial.suggest_float("cont_mobility_weight", 0, 1000),
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
        turn_advantage_weight=trial.suggest_float("cont_turn_advantage_weight", 0, 200),
        majority_loss_weight=trial.suggest_float("cont_majority_loss_weight", 0.2, 0.8),
        verge_weight=trial.suggest_float("cont_verge_weight", 0, 200),
        verge_growth_decay=trial.suggest_float("cont_verge_growth_decay", -1.0, 1.0),
        opening_thresh=trial.suggest_int("cont_opening_thresh", 18, 24),
        center_control_weight=trial.suggest_float("cont_center_control_weight", 0, 200),
        edge_weight=trial.suggest_float(
            "cont_edge_weight", -200, 200
        ),  # may want to penalize edges
        edge_growth_decay=trial.suggest_float("cont_edge_growth_decay", -1.0, 1.0),
        kings_row_weight=trial.suggest_float("cont_kings_row_weight", 0, 200),
        kings_row_growth_decay=trial.suggest_float(
            "cont_kings_row_growth_decay", -1.0, 1.0
        ),
    )

    score = 0

    warmup_qualafier = PLAY_TUNE(
        PlayerTurn.BLACK,
        heuristic_white=CONTENDER,  # contender is white
        heuristic_black=CHAMPION,
        time_limit=1,
        early_stop_depth=2,
    )

    if warmup_qualafier["winner"] == "WHITE" or warmup_qualafier["winner"] == "DRAW":
        print("\ncontendor passed the warmup:\n")
        score = 0
    elif warmup_qualafier["winner"] == "BLACK":
        print("\ncontendor lost the warmup:\n")
        return -10000

    pre_finals = PLAY_TUNE(
        PlayerTurn.BLACK,
        heuristic_white=CONTENDER,  # contender is white
        heuristic_black=CHAMPION,
        early_stop_depth=4,
    )

    if pre_finals["winner"] == "WHITE" or pre_finals["winner"] == "DRAW":
        print("\ncontendor passed the pre-finals:\n")
        score = 0
    elif pre_finals["winner"] == "BLACK":
        print("\ncontendor lost the pre-finals:\n")
        return -1000

    # Play the first game
    result = PLAY_TUNE(
        PlayerTurn.BLACK,
        heuristic_white=CHAMPION,
        heuristic_black=CONTENDER,
        early_stop_depth=9,
        time_limit=TIME_LIMIT,
    )

    # Calculate the score based on the result
    if result["winner"] == "BLACK":  # Assuming BLACK is the CONTENDER
        print("\nCONTENDOR BEAT THE CHAMPION\n")
        score = abs(result["black_men_left"] + result["black_kings_left"]) - (
            result["white_men_left"] + result["white_kings_left"]
        )
        stress_result_one = PLAY_TUNE(
            PlayerTurn.BLACK,
            heuristic_white=CHAMPION,
            heuristic_black=CONTENDER,
            max_depth=100,
            early_stop_depth=10,
            time_limit=TIME_LIMIT,
            one_piece_down=True,
        )
        if stress_result_one["winner"] == "BLACK":
            print("\nSTRESS TEST: CONTENDOR BEAT THE CHAMPION WITH A PIECE DOWN\n")
            score *= 4
            stress_test_two = PLAY_TUNE(
                PlayerTurn.BLACK,
                heuristic_white=CHAMPION,
                heuristic_black=CONTENDER,
                max_depth=100,
                early_stop_depth=100,
                time_limit=TIME_LIMIT,
                two_piece_down=True,
            )
            if stress_test_two["winner"] == "BLACK":
                print(
                    "\nSTRESS TEST: CONTENDOR BEAT THE CHAMPION WITH TWO PIECES DOWN\n"
                )
                score *= 8

    elif result["winner"] == "WHITE":  # WHITE is the OG champion.
        score = -1 * (
            abs(
                (result["black_men_left"] + result["black_kings_left"])
                - (result["white_men_left"] + result["white_kings_left"])
            )
        )
    else:  # penalty for draw with less pieces left
        score = (result["black_men_left"] + result["black_kings_left"]) - (
            result["white_men_left"] + result["white_kings_left"]
        )
        if score > 1:
            score = 0  # draw is not good enough
        else:
            score *= 2

    score *= MAX_MOVES / result["move_count"]

    if score > 0:
        as_white = PLAY_TUNE(
            PlayerTurn.WHITE,
            heuristic_white=CONTENDER,
            heuristic_black=CHAMPION,
            time_limit=TIME_LIMIT,
            early_stop_depth=10,
            contender_is_white=True,
        )
        if as_white["winner"] == "BLACK":
            print("\nCONTENDOR LOST TO THE CHAMPION AS WHITE\n")
            score == 0  # if the contender loses as white its uneven and not good enough
        else:
            print("\nCONTENDOR BEAT THE CHAMPION AS WHITE\n")
            score *= 8  # reward for winning as black and white
            as_white_stress_test_one = PLAY_TUNE(
                PlayerTurn.WHITE,
                heuristic_white=CONTENDER,
                heuristic_black=CHAMPION,
                early_stop_depth=100,
                one_piece_down=True,
                contender_is_white=True,
            )
            if (
                as_white_stress_test_one["winner"] == "WHITE"
                or as_white_stress_test_one["winner"] == "DRAW"
            ):
                print("\nCONTENDOR BEAT THE CHAMPION AS WHITE AND DOWN A PIECE\n")
                score *= 10

    return score


def run_tpe_study():
    # Use SQLite as a storage backend
    storage_url = "sqlite:///tpe_final_again_ak2k2_assdsdxdm.db"
    storage = storage = optuna.storages.RDBStorage(
        url=storage_url, engine_kwargs={"connect_args": {"timeout": 30}}
    )
    # generate a random 8 char string
    string = "abcdefghijklmnopqrstuvwxyz0123456789"
    study_name = "".join(random.sample(string, 8))

    study = optuna.create_study(
        direction="maximize",
        storage=storage,
        load_if_exists=True,
        study_name=study_name,
        # sampler=optuna.samplers.TPESampler(
        #     seed=123,
        #     n_startup_trials=NUM_RANDOM_STARTING_TRIALS,
        #     prior_weight=3,
        #     constant_liar=True,
        # ),
        sampler=optuna.samplers.NSGAIIISampler(),
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


if __name__ == "__main__":
    run_tpe_study()
