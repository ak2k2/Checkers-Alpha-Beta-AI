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

NET_TRIALS = 300
EARLY_STOP_DEPTH = 20
MAX_MOVES = 90


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
    three_piece_down=False,
    early_stop_depth=EARLY_STOP_DEPTH,
    contender_is_white=False,
    move_limit=MAX_MOVES,
    endgame_test_2v1=False,
    endgame_test_3v2=False,
):
    if time_limit is None:
        time_limit = 1
    if who_moves_first is None:
        who_moves_first = PlayerTurn.BLACK

    if max_depth is None:
        max_depth = 100

    WP, BP, K = get_fresh_board()
    if not contender_is_white:  # if the contender is black
        if one_piece_down:
            BP = remove_piece_by_pdntext(
                BP, "C3"
            )  # contender should have a disadvantage
        elif two_piece_down:
            BP = remove_piece_by_pdntext(BP, "C3")
            BP = remove_piece_by_pdntext(BP, "E3")
        elif three_piece_down:
            BP = remove_piece_by_pdntext(BP, "C3")
            BP = remove_piece_by_pdntext(BP, "E3")
            BP = remove_piece_by_pdntext(BP, "E1")
    elif contender_is_white:
        if one_piece_down:
            WP = remove_piece_by_pdntext(
                WP, "D6"
            )  # contender should have a disadvantage
        elif two_piece_down:
            WP = remove_piece_by_pdntext(WP, "D6")
            WP = remove_piece_by_pdntext(WP, "F6")
        elif three_piece_down:
            WP = remove_piece_by_pdntext(WP, "D6")
            WP = remove_piece_by_pdntext(WP, "F6")
            WP = remove_piece_by_pdntext(WP, "H8")
    if endgame_test_2v1:
        if not contender_is_white:
            WP, BP, K = setup_board_from_position_lists(
                ["KD4"], ["KB6", "KD6"]
            )  # black is the contender and has 2 kings and white has 1 king
    if endgame_test_3v2:
        if not contender_is_white:
            WP, BP, K = setup_board_from_position_lists(
                ["KB6", "KF2"], ["KD6", "KE5", "KF4"]
            )

    current_player = who_moves_first
    move_count = 0
    game_over = False
    local_move_lim = MAX_MOVES

    if endgame_test_2v1 or endgame_test_3v2:
        local_move_lim = 50

    while move_count < local_move_lim and not game_over:
        legal_moves = generate_legal_moves(WP, BP, K, current_player)

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
        man_weight=trial.suggest_int("cont_man_weight", 400, 600),
        man_growth_decay=trial.suggest_float("cont_man_growth_decay", -1, 1),
        king_weight=trial.suggest_int("cont_king_weight", 675, 875),
        king_growth_decay=trial.suggest_float("cont_king_growth_decay", 0.0, 1.0),
        back_row_weight=trial.suggest_int("cont_back_row_weight", 200, 600),
        back_growth_decay=trial.suggest_float("cont_back_growth_decay", -1.0, 0),
        capture_weight=trial.suggest_int("cont_capture_weight", 0, 50),
        capture_growth_decay=trial.suggest_float(
            "cont_capture_growth_decay", -1.0, 1.0
        ),
        kinged_mult=trial.suggest_float("cont_kinged_mult", 1.5, 3.2),
        land_edge_mult=trial.suggest_float("cont_land_edge_mult", 1.6, 3.2),
        took_king_mult=trial.suggest_float("cont_took_king_mult", 1.7, 4.3),
        distance_weight=trial.suggest_int("cont_distance_weight", 0, 100),
        distance_growth_decay=trial.suggest_float("cont_distance_growth_decay", 0, 1.0),
        mobility_weight=trial.suggest_int("cont_mobility_weight", 0, 150),
        mobility_jump_mult=trial.suggest_float("cont_mobility_jump_mult", 1.5, 4),
        mobility_growth_decay=trial.suggest_float("cont_mobility_growth_decay", 0, 1),
        safety_weight=trial.suggest_int("cont_safety_weight", 0, 400),
        safety_growth_decay=trial.suggest_float("cont_safety_growth_decay", 0, 1.0),
        double_corner_bonus_weight=trial.suggest_int(
            "cont_double_corner_bonus_weight", 0, 100
        ),
        turn_advantage_weight=trial.suggest_int("cont_turn_advantage_weight", 0, 400),
        verge_weight=trial.suggest_int("cont_verge_weight", 0, 50),
        verge_growth_decay=trial.suggest_float("cont_verge_growth_decay", -1.0, 1),
        center_control_weight=trial.suggest_int("cont_center_control_weight", 10, 200),
        edge_weight=trial.suggest_int(
            "cont_edge_weight", -100, 100
        ),  # may want to penalize edges
        edge_growth_decay=trial.suggest_float("cont_edge_growth_decay", -1.0, 1),
        kings_row_weight=trial.suggest_int("cont_kings_row_weight", 0, 200),
        kings_row_growth_decay=trial.suggest_float(
            "cont_kings_row_growth_decay", -1.0, 0
        ),
    )

    score = 0

    warmup_qualafier = PLAY_TUNE(
        PlayerTurn.BLACK,
        heuristic_white=CONTENDER,  # contender is white
        heuristic_black=CHAMPION,
        time_limit=1,
        early_stop_depth=2,
        move_limit=120,
        contender_is_white=True,
    )

    if warmup_qualafier["winner"] == "WHITE":  # WHITE is the CONTENDER
        print("\ncontendor passed the warmup by WINNING:\n")
        score = 0
    elif warmup_qualafier["winner"] == "BLACK":  # BLACK is the CHAMPION
        print("\ncontendor lost the warmup:\n")
        return -10000

    # Play the first game
    result = PLAY_TUNE(
        PlayerTurn.BLACK,
        heuristic_white=CHAMPION,
        heuristic_black=CONTENDER,  # contender is black
        early_stop_depth=100,
        time_limit=3,
        one_piece_down=True,
    )

    # Calculate the score based on the result
    if result["winner"] == "BLACK":  # BLACK is the CONTENDER
        print("\nCONTENDOR BEAT THE CHAMPION AS BLACK GAME 1\n")
        score = abs(result["black_men_left"] + result["black_kings_left"]) - (
            result["white_men_left"] + result["white_kings_left"]
        )

        endgame1 = PLAY_TUNE(
            PlayerTurn.BLACK,
            heuristic_white=CHAMPION,
            heuristic_black=CONTENDER,  # contender is black
            early_stop_depth=5,
            time_limit=3,
            endgame_test_2v1=True,
        )
        if endgame1["winner"] == "BLACK":
            print("\nCONTENDOR BEAT THE CHAMPION AS BLACK in 2v1 ENDGAME\n")
            score *= 4

            endgame2 = PLAY_TUNE(
                PlayerTurn.BLACK,
                heuristic_white=CHAMPION,
                heuristic_black=CONTENDER,  # contender is black
                early_stop_depth=5,
                time_limit=3,
                endgame_test_3v2=True,
            )
            if endgame2["winner"] == "BLACK":
                print("\nCONTENDOR BEAT THE CHAMPION AS BLACK in 3v2 ENDGAME\n")
                score *= 16

                one_piece_down = PLAY_TUNE(
                    PlayerTurn.BLACK,
                    heuristic_white=CHAMPION,
                    heuristic_black=CONTENDER,  # contender is black
                    early_stop_depth=5,
                    time_limit=3,
                    one_piece_down=True,
                )
                if one_piece_down["winner"] == "BLACK":
                    score *= 32
                    two_piece_down = PLAY_TUNE(
                        PlayerTurn.BLACK,
                        heuristic_white=CHAMPION,
                        heuristic_black=CONTENDER,  # contender is black
                        early_stop_depth=5,
                        time_limit=3,
                        two_piece_down=True,
                    )
                    if two_piece_down["winner"] == "BLACK":
                        score *= 64
        return score

    else:
        score = -1 * (
            abs(
                (result["black_men_left"] + result["black_kings_left"])
                - (result["white_men_left"] + result["white_kings_left"])
            )
        )
        return score


def run_tpe_study():
    # Use SQLite as a storage backend
    storage_url = "sqlite:///dbqmaf.db"
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
        sampler=optuna.samplers.TPESampler(seed=12122223),
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
