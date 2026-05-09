#!/usr/bin/env python
# -*- coding: utf-8-SIG -*-

"""
This is a behavioural experiment conducted using PsychoPy and assisted by EEG devices to obtain EEG data.

NOTE — Current trial counts are set to small debug values for quick verification.
For the full experiment, follow the instructions inside generate_block_sequence()
to restore the formal trial numbers.

NOTE — Data output is configured for Windows. Two items may need updating before running:
  1. Save path (SAVE_DIR): currently set to the author's local Downloads folder.
     Change this to your own path in the Data Output section at the bottom of the script.
  2. CSV encoding: currently 'utf-8-sig' (UTF-8 with BOM) for Excel compatibility on Windows.
     If running on macOS or Linux, change this to 'utf-8'.
  3. Counterbalanced Scheme will be followed
     In the complete experimental design, both groups of participants will be divided into two halves, 
     and the other half of the participants will first do block 2 and then block 1, with the red ball as the stimulus. 
     Please refer to the Flowchart PDF file for details. The current code is only applicable to half of the participants.
     For the other half of the participants, minor changes need to be made to the presentation order of blocks in the code and the feature settings of stimuli.
"""

from psychopy import visual, core, event, monitors, gui
import random
import os
import csv
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════
# SECTION 0 — Participant Information Dialog
# ═══════════════════════════════════════════════════════════════════
# gui.DlgFromDict() renders a simple GUI form before the experiment
# window opens. If the participant cancels, core.quit() exits cleanly.

exp_info = {
    'Participant ID': '',
    'Age': '',
    'Gender': ['female', 'male'],
    'Group': ['ADHD', 'Control'],   # drop-down list; first item is the default
}
dlg = gui.DlgFromDict(
    dictionary=exp_info,
    title='Oddball Task',
    order=['Participant ID', 'Age', 'Gender','Group']
)
if not dlg.OK:
    core.quit()

participant_id = exp_info['Participant ID']
# Create a unique time-based tag so all output files from this session share the same ID, as "year, month, day_hour, min, sec".
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')


# ═══════════════════════════════════════════════════════════════════
# SECTION 1 — Monitor Configuration
# ═══════════════════════════════════════════════════════════════════
# visual-angle-based units. Without this, it logs a warning and creates a temporary monitor with arbitrary values.
# Adjust width/distance/sizePix to match the actual testing screen.

mon = monitors.Monitor('testMonitor')
mon.setWidth(53)          # physical screen width in cm (typical 24" monitor ≈ 53 cm)
mon.setDistance(60)       # viewing distance in cm
mon.setSizePix([1920, 1080])


# ═══════════════════════════════════════════════════════════════════
# SECTION 2 — Window and Stimulus Definitions
# ═══════════════════════════════════════════════════════════════════
# All stimuli are created once here and reused throughout the experiment.
# Creating stimuli upfront (rather than inside the trial loop) avoids per-trial allocation overhead and keeps timing more precise.

win = visual.Window(
    monitor=mon,
    fullscr=True,
    color='white',
    colorSpace='rgb',
    units='pix',      # pixel units keep circle size constant across screens
    allowGUI=False,   # hides the window chrome for a cleaner display
)
win.mouseVisible = False  # hide the cursor during the task

CIRCLE_RADIUS = 60  # radius in pixels; adjust if the circle appears too small/large

fixation = visual.TextStim(
    win,
    text='+',
    color='black',
    colorSpace='rgb',
    height=60,
    bold=True,
)

circle_black = visual.Circle(win, radius=CIRCLE_RADIUS, fillColor='black', lineColor='black')
circle_blue  = visual.Circle(win, radius=CIRCLE_RADIUS, fillColor='blue',  lineColor='blue')
circle_red   = visual.Circle(win, radius=CIRCLE_RADIUS, fillColor='red',   lineColor='red')

# Generic text stimulus reused for all instruction screens and prompts.
msg_stim = visual.TextStim(
    win,
    text='',
    color='black',
    colorSpace='rgb',
    height=28,
    wrapWidth=900,
    alignText='center',
)

# Mapping colour name → stimulus object allows run_block() to select
# the correct circle with a single dictionary lookup instead of if-elif chains.
CIRCLE_MAP = {
    'black': circle_black,
    'blue':  circle_blue,
    'red':   circle_red,
}


# ═══════════════════════════════════════════════════════════════════
# SECTION 3 — Sequence Generation
# ═══════════════════════════════════════════════════════════════════

def generate_block_sequence():
    """
    Build and return a randomised trial sequence for one block.
 
    Returns
    -------
    list of (colour: str, trial_type: str)
        colour     : 'black' | 'blue' | 'red'
        trial_type : 'regular_black' | 'regular_blue' | 'random_black' | 'violation_blue' | 'red'
 
    Design rationale — two building-block types
    --------------------------------------------
    1. TRIPLET GROUPS
         · Each group holds one or more intact [black, black, blue] triplets.
         · Triplets are never split: the unbroken three-stimulus pattern is what trains the participant's expectation.
         · Labelled 'regular_black' / 'regular_blue' in the output data, serving as the experimental baseline.
 
    2. RANDOM CHUNKS
         · Each chunk is a small, internally shuffled bag containing a mix of:
             - random_black   : non-patterned black circles; disrupts rhythmic prediction.
             - violation_blue : blue circles outside the expected pattern; the critical trials for measuring expectation violation.
             - red            : novel distractors; never be targeted.
 
    Randomisation strategy
    -------------------------------------
    Step 1 — Divide:
         · N_REGULAR_TRIPLETS triplets  →  N_GROUPS triplet groups (evenly distributed).
         · Random pool (random_black + violation_blue + red)  →  N_GROUPS random chunks
           (balanced via modulo assignment; each chunk is shuffled internally).
 
    Step 2 — Macro-level shuffle:
         · All N_GROUPS triplet groups and N_GROUPS random chunks are merged into one list of (N_GROUPS × 2) units and shuffled together.
         · Effect: triplet groups and random chunks are freely interleaved, triplet groups may appear consecutively or be separated by multiple random chunks, and vice versa.
                   Neither type is pinned to a fixed position in the block.
 
    Step 3 — Expand:
         · Each unit is flattened into individual (colour, trial_type) tuples to produce the final trial-by-trial sequence passed to run_block().

    Parameters (DEBUG vs. FULL)
    ---------------------------
    Change the four constants below to switch between test and full-experiment values.
    """
    # ── Parameters ── (DEBUG values for quick testing)
    # The values in 'full' are the numbers of stimuli appearing in one of the block, because generate_block_dequence() will be called twice, once for Block 1 and once for Block 2.
    N_REGULAR_TRIPLETS = 12    # full: 42  — total number of [black, black, blue] triplets
    N_RANDOM_BLACK     = 10   # full: 36  — random (non-patterned) black circles
    N_VIOLATION_BLUE   = 6    # full: 18  — blue circles that violate the expected pattern
    N_RANDOM_RED       = 4    # full: 20  — red distractor circles
    N_GROUPS           = 4    # full: 6  — number of groups (applies to both triplets and random pool)

    # ── Step 1a: Build triplet groups ──────────────────────────────────────────
    # Each triplet is stored as a list of (colour, label) tuples so it can be
    # treated as an atomic unit during shuffling and easily flattened afterward.
    single_triplet = [('black', 'regular_black'),
                      ('black', 'regular_black'),
                      ('blue',  'regular_blue')]
    # Generates a list of N_REGULAR_TRIPLETS independent copies of the single_triplet pattern.
    # The [:] syntax performs a shallow copy to ensure each triplet is a distinct object in memory, preventing unintended side effects during sequence generation.
    all_triplets = [single_triplet[:] for _ in range(N_REGULAR_TRIPLETS)]

    # Distribute triplets into N_GROUPS groups as evenly as possible.
    # If not evenly divisible, the first `remainder` groups get one extra triplet.
    triplet_groups = []
    per_group = N_REGULAR_TRIPLETS // N_GROUPS  # Calculate the base number of triplets per group using integer division.
    remainder = N_REGULAR_TRIPLETS % N_GROUPS  # Determine the number of leftover triplets that cannot be divided evenly
    idx = 0  # Initialize a tracking index to slice the master triplet list sequentially.
    for i in range(N_GROUPS):
        size = per_group + (1 if i < remainder else 0)  # Add one extra triplet to the current group if a remainder still exists.
        # Flatten the triplets in this group into a single list of tuples.
        group_trials = []
        for triplet in all_triplets[idx: idx + size]:
            group_trials.extend(triplet)  # Flatten the nested triplets into a single sequence of individual trials.
        triplet_groups.append(('triplet_group', group_trials))  # Store the flattened group with a descriptive label as a tuple.
        idx += size  # Advance the starting index for the next group's slice.

    # ── Step 1b: Build random chunks ───────────────────────────────────────────
    # Assemble the full random pool, then distribute into N_GROUPS chunks via
    # modulo assignment (ensures balanced chunk sizes regardless of pool size).
    random_pool = (
        [('black', 'random_black')]   * N_RANDOM_BLACK   +
        [('blue',  'violation_blue')] * N_VIOLATION_BLUE +
        [('red',   'red')]            * N_RANDOM_RED
    )
    random.shuffle(random_pool)  # shuffle the pool before splitting so modulo assignment doesn't create colour-biased chunks

    raw_chunks = [[] for _ in range(N_GROUPS)]
    for j, trial in enumerate(random_pool):  # Loop through the shuffled pool of random trials, keeping track of the index j.
        raw_chunks[j % N_GROUPS].append(trial)  # Use the modulo operator to distribute trials into chunks in a round-robin fashion

    random_chunks = []
    for chunk in raw_chunks:
        random.shuffle(chunk)  # shuffle within each chunk
        random_chunks.append(('random_chunk', chunk))  # Save the shuffled chunk as a tuple with a label for identification.

    # ── Step 2: Combine all groups into one list and shuffle ───────────────────
    # Both triplet groups and random chunks are treated as equal-level units.
    # Shuffling this combined list randomises their relative order.
    all_units = triplet_groups + random_chunks
    random.shuffle(all_units)

    # ── Step 3: Expand units into the final flat trial sequence ────────────────
    labeled_sequence = []
    for unit_type, trials in all_units:
        labeled_sequence.extend(trials)  # Append all individual trials from the current unit into the main list, removing the nested structure.

    return labeled_sequence  # list of (colour_str, trial_type_str)
                             # Return the complete, flat list of (color, label) tuples for the experiment to run.


# ═══════════════════════════════════════════════════════════════════
# SECTION 4 — Utility Functions
# ═══════════════════════════════════════════════════════════════════

def show_message(text, keys=None, duration=None):
    """
    Display a text message at screen centre.

    Parameters
    ----------
    text     : str   — message to display
    keys     : list  — if provided, wait until one of these keys is pressed
    duration : float — if provided, wait this many seconds then return
    (keys and duration are mutually exclusive; keys takes priority)
    """
    msg_stim.setText(text)
    msg_stim.draw()
    win.flip()
    if duration is not None:  # for the resting time between blocks
        core.wait(duration)
        win.flip()
    elif keys is not None:  # for participants reading text before strating each blocks
        event.waitKeys(keyList=keys)
        win.flip()


def countdown_rest(seconds=180):  # for the resting time between blocks
    """
    Show a live countdown timer for the inter-block rest period.
    The participant can press Space to end the rest early.
    The display updates every ~50 ms (sufficient for a seconds-precision timer).
    """
    clock = core.Clock()
    while True:
        remaining = seconds - clock.getTime()
        if remaining <= 0:
            break
        mins = int(remaining) // 60
        secs = int(remaining) % 60
        msg_stim.setText(
            f'Rest period\n\n'
            f'The experiment will continue in:\n\n'
            f'{mins:02d}:{secs:02d}\n\n'
            f'(Press Space to continue early)'
        )
        msg_stim.draw()
        win.flip()
        pressed = event.getKeys(keyList=['space', 'escape'])
        if 'escape' in pressed:
            win.close()
            core.quit()
        if 'space' in pressed:
            break
        core.wait(0.05)
    win.flip()


def run_block(block_num, sequence, record_keypresses=True):
    """
    Execute one block of the oddball task.
 
    Parameters
    ----------
    block_num         : int  — block number (1 or 2), stored in output data
    sequence          : list — output of generate_block_sequence()
    record_keypresses : bool — True for Block 1 (overt keypress task);
                               False for Block 2 (covert counting task, no responses recorded)

    Returns
    -------
    results           : list of dicts  — one dict per trial (Block 1 only; empty for Block 2)
    blue_target_count : int            — total blue circles presented (used for Block 2 scoring)

    Trial timing
    ------------
    The very first fixation of the block is shown for 50 ms before the first circle.
    After that, each trial follows:
        [circle 200 ms] → [fixation 800 ms]  (= 1000 ms total per trial)

    Response window
    ---------------
    For Block 1, Space bar is accepted during both the circle period (0–200 ms)
    and the subsequent fixation period (200–1000 ms from circle onset).
    RT is measured from circle onset:
        - If response occurs during the circle:   RT = time since circle onset
        - If response occurs during the fixation: RT = 200 ms + time into fixation

    Key detection note
    ------------------
    event.getKeys() is called WITHOUT the `timeStamped` argument.
    When timeStamped is passed a Clock object, the return value changes from
    a list of strings ['space'] to a list of tuples [('space', 0.12)].
    Iterating over a tuple with `for k in pressed` would then iterate over
    individual characters ('s', 'p', 'a', 'c', 'e'), causing 'e' to be
    misidentified as 'escape' and terminating the experiment prematurely.
    Using the un-timestamped form and tracking RT via a separate Clock avoids this.
    """
    results           = []
    blue_target_count = 0

    # Show the initial fixation cross for 50 ms before the first circle appears.
    # This brief period establishes the visual context at block start.
    fixation.draw()
    win.flip()
    core.wait(0.050)

    for trial_idx, (colour, trial_type) in enumerate(sequence):  # Start a loop to go through each item in the 'sequence' list one by one.

        # Allow experimenter to abort the task at any point.
        if event.getKeys(keyList=['escape']):
            win.close()
            core.quit()

        is_blue  = (colour == 'blue')  # Create a boolean (True/False) to check if the current stimulus is the target color.
        rt       = None  # Reset the Reaction Time variable to None so old data from the last trial doesn't leak in.
        responded = False  # Initialize a flag to False to track if the participant has pressed the key during this trial.

        if is_blue:  # Check if the current trial is a 'target' trial.
            blue_target_count += 1  # Increment the total counter of blue circles presented so far

        # ── Phase 1: Circle presentation — 200 ms ──────────────────────
        CIRCLE_MAP[colour].draw()
        win.flip()

        # Clear any keyboard events that accumulated between trials
        # so that a slow response from the previous trial cannot bleed into the current one.
        if record_keypresses:
            event.clearEvents(eventType='keyboard')

        stim_clock = core.Clock()   # starts immediately after win.flip()

        while stim_clock.getTime() < 0.200:
            if record_keypresses:
                pressed = event.getKeys(keyList=['space', 'escape'])
                for k in pressed:
                    if k == 'escape':
                        win.close()
                        core.quit()
                    if k == 'space' and not responded:
                        rt        = stim_clock.getTime()   # RT from circle onset
                        responded = True
            core.wait(0.001)  # 1 ms sleep prevents CPU spin at 100%

        # ── Phase 2: Fixation cross — 800 ms ───────────────────────────
        fixation.draw()
        win.flip()

        fix_clock = core.Clock()

        while fix_clock.getTime() < 0.800:
            if record_keypresses:
                pressed = event.getKeys(keyList=['space', 'escape'])
                for k in pressed:
                    if k == 'escape':
                        win.close()
                        core.quit()
                    if k == 'space' and not responded:
                        # RT is measured from circle onset, so add the full
                        # circle duration (200 ms) to the time elapsed in fixation.
                        rt        = 0.200 + fix_clock.getTime()
                        responded = True
            core.wait(0.001)

        # ── Record trial outcome (Block 1 only) ────────────────────────
        if record_keypresses:
            if is_blue:
                # Target trial: a response is correct (hit); no response is a miss.
                correct     = responded
                false_alarm = False
            else:
                # Non-target trial (black or red): a response is a false alarm.
                correct     = not responded
                false_alarm = responded

            results.append({
                'block':       block_num,
                'trial_index': trial_idx + 1,
                'colour':      colour,
                'trial_type':  trial_type,
                'is_target':   is_blue,
                'responded':   responded,
                # rt_ms is blank for misses or non-target trials to distinguish
                # "no response" (blank) from a genuine 0 ms RT.
                'rt_ms':       round(rt * 1000, 2) if (responded and is_blue and rt is not None) else '',
                'correct':     correct,
                'false_alarm': false_alarm,
            })

    return results, blue_target_count


def get_typed_number(prompt_text):
    """
    Collect a numeric string typed by the participant on-screen.
    Supports digit keys 0–9, Backspace for correction, and Enter to confirm.

    Returns the typed string (defaults to '0' if nothing was entered).
    This is used after Block 2 to record the participant's blue circle count.
    """
    typed = []
    while True:
        msg_stim.setText(prompt_text + '\n\nYour answer: ' + ''.join(typed))
        msg_stim.draw()
        win.flip()

        pressed = event.getKeys()
        for k in pressed:
            if k == 'escape':
                win.close()
                core.quit()
            elif k == 'return':
                return ''.join(typed) if typed else '0'
            elif k == 'backspace':
                if typed:  # Ensure the 'typed' list is not already empty before attempting to remove an item.
                    typed.pop()  # Remove the very last character added to the list.
            elif k in [str(i) for i in range(10)]:  # Check if the pressed key is a numeric digit between 0 and 9.
                typed.append(k)  #Add the detected number string to the end of the 'typed' list.

        core.wait(0.03)  # ~30 ms polling interval; fast enough for comfortable typing


# ═══════════════════════════════════════════════════════════════════
# SECTION 5 — Main Experiment Flow
# ═══════════════════════════════════════════════════════════════════

show_message(
    'Welcome to the experiment!\n\n'
    'This experiment consists of two parts.\n\n'
    'Please read the instructions carefully before each part.\n\n'
    'Press Space to continue.',
    keys=['space']
)

# ── Block 1 : Overt keypress task ───────────────────────────────────
show_message(
    'PART 1 INSTRUCTIONS\n\n'
    'Circles of different colours will appear one at a time in the centre of the screen.\n\n'
    'Please IGNORE black and red circles.\n\n'
    'Every time you see a BLUE circle, press the SPACE bar as quickly as possible.\n\n'
    'Try to be both fast and accurate.\n\n'
    'Press Space when you are ready to begin Part 1.',
    keys=['space']
)

seq_block1    = generate_block_sequence()  # Call the custom function to create a randomized list of trials 
                                           # (colors and types) (according to portion set) for the first block.
# Retrieve target_comunt from results_b1, as Block 1 records detailed key data, it is more secure to directly 'count' from the data table.
results_b1, _ = run_block(block_num=1, sequence=seq_block1, record_keypresses=True)

# Brief on-screen notice before the rest countdown begins.
show_message(
    'Part 1 complete!\n\n'
    'You now have a 3-minute rest break.\n\n'
    'The experiment will continue automatically.\n'
    '(You may also press Space to skip the rest and continue early.)',
    duration=5
)
countdown_rest(seconds=180)

# ── Block 2 : Covert counting task ─────────────────────────────────
show_message(
    'PART 2 INSTRUCTIONS\n\n'
    'Circles of different colours will again appear one at a time.\n\n'
    'Please IGNORE black and red circles.\n\n'
    'Every time you see a BLUE circle, count it silently in your head.\n'
    'Remember the total number of blue circles you count.\n\n'
    'You do NOT need to press any keys during this part.\n\n'
    'Press Space when you are ready to begin Part 2.',
    keys=['space']
)

seq_block2       = generate_block_sequence()
_, blue_count_b2 = run_block(block_num=2, sequence=seq_block2, record_keypresses=False)

# Ask the participant to report their counted total for Block 2.
counted_str = get_typed_number(
    'Part 2 complete!\n\n'
    'How many BLUE circles did you count in Part 2?\n\n'
    'Type your answer and press Enter to confirm.'
)

try:
    participant_count = int(counted_str)
except ValueError:
    participant_count = -1   # -1 flags an invalid (non-numeric) entry in the output

count_error = participant_count - blue_count_b2


# ═══════════════════════════════════════════════════════════════════
# SECTION 6 — Performance Summary
# ═══════════════════════════════════════════════════════════════════
# Metrics computed here:
#   hit_count   — number of blue circles correctly responded to (Block 1)
#   accuracy    — hit_count / total_blue_count  (Block 1)
#   mean_rt     — average reaction time across hits only  (Block 1)
#   false_alarms — responses made to non-target circles  (Block 1)
#   count_error — difference between participant's reported count and actual count (Block 2)

b1_blue_trials  = [r for r in results_b1 if r['is_target']]
b1_hits         = [r for r in b1_blue_trials if r['responded']]
b1_false_alarms = [r for r in results_b1 if r['false_alarm']]

hit_count    = len(b1_hits)
target_count = len(b1_blue_trials)
accuracy     = hit_count / target_count * 100 if target_count > 0 else 0

rts     = [r['rt_ms'] for r in b1_hits if r['rt_ms'] != '']
mean_rt = sum(rts) / len(rts) if rts else 0

show_message(
    f'Thank you for participating!\n\n'
    f'--- Part 1 (Keypress Task) ---\n'
    f'  Blue circles presented : {target_count}\n'
    f'  Correct responses (Hits) : {hit_count}\n'
    f'  Accuracy : {accuracy:.1f}%\n'
    f'  Mean reaction time : {mean_rt:.1f} ms\n'
    f'  False alarms : {len(b1_false_alarms)}\n\n'
    f'--- Part 2 (Counting Task) ---\n'
    f'  Actual blue circle count : {blue_count_b2}\n'
    f'  Your reported count : {participant_count}\n'
    f'  Counting error : {count_error:+d}\n\n'
    f'Press Space to exit.',
    keys=['space']
)


# ═══════════════════════════════════════════════════════════════════
# SECTION 7 — Data Output
# ═══════════════════════════════════════════════════════════════════
# Two files are written per participant:
#   1. data_<ID>_<timestamp>.csv  — trial-level data (Block 1 only)
#   2. summary_<ID>_<timestamp>.txt — human-readable performance summary
#
# The CSV uses utf-8-sig encoding (UTF-8 with BOM) so that Excel on Windows
# opens it with correct character rendering without a manual import step.

SAVE_DIR = r'C:\Users\cl157\Downloads' # should be adjusted according to user's laptop
os.makedirs(SAVE_DIR, exist_ok=True)

csv_path     = os.path.join(SAVE_DIR, f'data_{participant_id}_{timestamp}.csv')
summary_path = os.path.join(SAVE_DIR, f'summary_{participant_id}_{timestamp}.txt')

fieldnames = [
    'participant_id', 'age', 'gender','group',
    'block', 'trial_index', 'colour', 'trial_type',
    'is_target', 'responded', 'rt_ms', 'correct', 'false_alarm',
]

with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in results_b1:
        # Merge participant-level metadata with trial-level data for each row.
        out = {
            'participant_id': participant_id,
            'age':            exp_info['Age'],
            'gender':          exp_info['Gender'],
            'group':        exp_info['Group'],
        }
        out.update(row)
        writer.writerow(out)

with open(summary_path, 'w', encoding='utf-8') as f:
    f.write(f"Participant ID  : {participant_id}\n")
    f.write(f"Age             : {exp_info['Age']}\n")
    f.write(f"Gender           : {exp_info['Gender']}\n")
    f.write(f"Group         : {exp_info['Group']}\n")
    f.write(f"Timestamp       : {timestamp}\n\n")
    f.write("=== Block 1 (Keypress Task) ===\n")
    f.write(f"Target (blue) trials  : {target_count}\n")
    f.write(f"Hits                  : {hit_count}\n")
    f.write(f"Accuracy              : {accuracy:.2f}%\n")
    f.write(f"Mean RT               : {mean_rt:.2f} ms\n")
    f.write(f"False Alarms          : {len(b1_false_alarms)}\n\n")
    f.write("=== Block 2 (Counting Task) ===\n")
    f.write(f"Actual blue count     : {blue_count_b2}\n")
    f.write(f"Participant's count   : {participant_count}\n")
    f.write(f"Count error           : {count_error:+d}\n")

win.close()
core.quit()