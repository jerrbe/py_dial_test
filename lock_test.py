from LockClass import LockClass
import logging


logging.VERBOSE = 5
logging.addLevelName(logging.VERBOSE, "VERBOSE")
logging.basicConfig(
    filename='lock_test.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

lock = LockClass()
dial_step = 2
limit = 100.0/dial_step
dial_combo = [1.5, 0, 0]
destination = 0
current_position = lock.D / 10
A = 0
B = 1
C = 2


def move_cw(target, turns=0):
    global current_position
    logger.debug(f"    moving_cw {target}, {turns}:  {current_position}")
    if current_position >= target:
        destination = target
    else:
        destination = target - 100
    if turns > 0:
        destination = destination - (turns * 100)
    lock.move(destination)
    destination = target
    current_position = target
    return


def move_ccw(target, turns=0):
    global current_position
    logger.debug(f"    moving_cw {target}, {turns}:  {current_position}")
    if current_position <= target:
        destination = target
    else:
        destination = target + 100

    if turns > 0:
        destination = destination + (turns * 100)

    lock.move(destination)
    destination = target
    current_position = target


def increment_target(index: int, step: float = 2) -> float:
    rollover = 0
    dial_combo[index] += step
    if (dial_combo[index] >= 100):
        dial_combo[index] -= 100
        rollover = 1
    return rollover


def decrement_target(index: int, step: float = 2) -> float:
    rollover = 0
    dial_combo[index] -= step
    if (dial_combo[index] < 0):
        dial_combo[index] += 100
        rollover = 1
    return rollover


def dial_dwell() -> bool:
    # // Check the handle at this point
    # destination.i = handle_pull;
    # prepare_line_to_destination();
    # planner.synchronize();
    if (
        dial_combo[A] == lock.A and
        dial_combo[B] == lock.B and
        dial_combo[C] == lock.C
    ):
        logger.info(f"PASS: Target={dial_combo[A]:2},{dial_combo[B]:2},"
                    f"{dial_combo[C]:2}  Actual={lock.A:2},{lock.B:2},"
                    f"{lock.C:2},{lock.D:2}")
    else:
        logger.info(f"FAIL: Target={dial_combo[A]:2},{dial_combo[B]:2},"
                    f"{dial_combo[C]:2}  Actual={lock.A:2},{lock.B:2},"
                    f"{lock.C:2},{lock.D:2}")
    # GcodeSuite::dwell(pull_dwell_time);
    # bool locked = !endstops.state();
    locked = True
    if (
        dial_combo[A] >= 100-dial_step and
        dial_combo[B] < dial_step and
        dial_combo[C] >= 100-dial_step
    ):
        locked = False
    # if (locked):
    #     destination.i = 0;
    #     prepare_line_to_destination();
    #     planner.synchronize();
    return locked


b_cnt = 1
c_cnt = 1
dial_combo[B] = dial_combo[A]
dial_combo[C] = dial_combo[A]
move_ccw(dial_combo[A], 3)
move_cw(dial_combo[B], 2)
move_ccw(dial_combo[C], 1)
move_cw(0)
locked = dial_dwell()
locked = True
while (locked):
    if (c_cnt < limit):
        # //Need to try more of the third digit
        extra = increment_target(C, dial_step)
        c_cnt += 1
        move_ccw(dial_combo[C], extra)
        move_cw(0)
        locked = dial_dwell()
    elif (b_cnt < limit):
        # //Need to decrement the second digit
        decrement_target(B, dial_step)
        b_cnt += 1
        # sync_plan_position()
        c_cnt = 1
        move_cw(dial_combo[B], 1)
        move_ccw(dial_combo[C], 1)
        move_cw(0)
        locked = dial_dwell()
    else:
        # //Need to increment the first digit
        increment_target(A, dial_step)
        b_cnt = 1
        c_cnt = 1
        dial_combo[B] = dial_combo[A]
        dial_combo[C] = dial_combo[A]
        move_ccw(dial_combo[A], 3)
        move_cw(dial_combo[B], 2)
        move_ccw(dial_combo[C], 1)
        move_cw(0)
        locked = dial_dwell()
