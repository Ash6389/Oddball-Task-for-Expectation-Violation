# Oddball-Task-for-Expectation-Violation
This is a behavioral experiment conducted using psychopy and assisted by EEG devices to obtain EEG data.

Expectation-Structure Visual Oddball Task — ADHD vs. Neurotypical Adults
========================================================================
 
Research Question:
    Does expectation violation in a learned sequence-structure task modulate P3b amplitude and latency differently in adults with ADHD compared to neurotypical (NT) controls?
 
Overview:
    This task combines EEG and behavioural measurement to examine expectation-based attention in adults (aged 30–55) with ADHD versus NT controls. 
    The paradigm is built on the classic oddball task and introduces a structured expectation pattern that is periodically violated, targeting the P3b ERP component (an index of context updating and working memory).
 
    Two data streams are collected simultaneously:
      - EEG data: continuous 128-channel recording, analysed for P3b amplitude and latency.
      - Behavioural data: reaction time (RT) and accuracy from Block A (keypress responses) and Block B (counting result reports).
 
Stimuli:
    All stimuli are circles presented at the centre of the screen. Three colours are used:
 
      - Black circle  (60% of trials, 240/block) — Standard & frequent stimulus.
        Never a response target in either block. 
        High frequency establishes a familiar baseline, making target and novel stimuli perceptually salient by contrast.
 
      - Blue circle   (30% of trials, 120/block) — Target stimulus.
        Subdivided into two sub-types to **create and then violate expectation**:
          · **Expected targets**   (70% of blue, 84/block): appear in a fixed [black–black–blue] triplet sequence. **The regularity builds a learnable expectation pattern** in the participant's cognitive model.
          · **Unexpected targets** (30% of blue, 36/block): appear at **random positions**, **breaking the established pattern**. These are the critical trials for measuring expectation violation (P3b modulation and behavioural costs).
 
      - Red circle    (10% of trials, 40/block) — Novel distractor & foil.
        Never a response target in either block. 
        Introduced to elicit P3a (automatic attentional orienting to novelty), which in turn helps isolate the P3b signal.
 
Block Design:
    Both two blocks present the same trial sequence and stimulus proportions.
    Only the participant's task differs:
 
      - Block A  (Button-press / Overt):
        Participants press **Space** when they see a blue circle; ignore black and red.
        Purpose: provides behavioural measures (RT, accuracy) that confirm active, overt engagement with the task — a necessary check that participants are cognitively participating, not passively watching.
 
      - Block B  (Silent-counting / Covert):
        Participants silently count blue circles and report the total at the end; no keypresses.
        Purpose: eliminates motor-related EEG artefacts (muscle movement, button-press potentials) that would contaminate the ERP signal in Block A.
        The absence of any motor response yields cleaner, movement-free EEG data, which in turn helps get the clean data for the whole experiment statistically afterwards.
 
Trial Setting:
        800 trials in total, 400  trials for each blocks
        Stimulus Duration (SD)    = 200 ms
        Inter-Stimulus Interval (ISI)   = 1 000 ms 
        Timeline: [first fixation cross]-50ms-[circle]-200ms-[fixation cross]-800ms-[circle]-200ms-[fixation cross]-800ms-[circle]...
 
Output Files (saved to Downloads in Win System):
    data_<ID>_<timestamp>.csv    — trial-level behavioural data for Block A (keypress task)
    summary_<ID>_<timestamp>.txt — performance summary: RT, accuracy, false alarms (Block A) and counting error (Block B)
 
NOTE — FULL EXPERIMENT MODE:
    Parameters are set to full experimental values (400 trials per block, 800 total).
    To run a quick debug pass, change five constants inside generate_block_sequence():
        N_REGULAR_TRIPLETS = 5
        N_RANDOM_BLACK     = 10
        N_VIOLATION_BLUE   = 3
        N_RANDOM_RED       = 4
        N_GROUPS           = 3
