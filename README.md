# Assistive and Educational Robotics System (Simulation) for Neurodiverse Children (ADHD & ASD)

## Problem statement
Many neurodiverse children (including ADHD and ASD) can face challenges such as:
- sustaining attention across multi-step activities
- transitioning between tasks
- frustration tolerance when a task feels too hard
- needing consistent, supportive feedback and structure

Assistive robotics can help by providing **predictable routines**, **engaging prompts**, and **adaptive support**. This repository is a **simulation** of an assistive educational robot that runs as a clean, modular Python project.

> Important note: This is **not** a clinical tool. It is a learning-oriented software simulation that demonstrates core concepts used in HRI/assistive robotics.

## Project goals
Simulate a robot that:
- guides a user through short tasks
- monitors engagement (simulated, or optionally via face presence)
- adapts behavior based on performance (simplify on failures, increase difficulty on successes)
- demonstrates a robotics-style loop: **sense → decide → act**

## Project structure
```
assistive-robotics/
  main.py              # entry point
  interaction.py       # sense/decide/act loop
  task_manager.py      # task generation + scoring + difficulty adaptation
  attention_module.py  # simulated attention (+ optional OpenCV face presence proxy)
  feedback.py          # supportive feedback and redirection messages
  utils.py             # shared types and helpers
  README.md
```

## System design
### Interaction loop (sense → decide → act)
Each cycle:
1. **Sense**: estimate attention (`attentive`, `distracted`, `absent`)
2. **Decide**: choose whether to present a task or pause/redirect
3. **Act**: prompt a task, give feedback, and adapt difficulty

### Adaptive logic
- If the user **succeeds**, difficulty increases slightly
- If the user **fails**, difficulty decreases (simplify)
- If attention is **distracted/absent**, the robot avoids pushing tasks and instead redirects gently

## Technical components
### Task manager (`task_manager.py`)
Provides two simple educational task types:
- **Sequence memory**: repeat a short digit sequence
- **Follow instruction**: type a short action sequence in order

Difficulty controls the length/complexity.

### Attention model (`attention_module.py`)
Two modes:
- **Simulated attention** (default): rule-based random model with a stable seed
- **Optional OpenCV**: webcam face presence is used as a crude attention proxy (face detected → attentive-ish)

### Feedback system (`feedback.py`)
Generates short messages with supportive tone:
- encouragement on failures
- celebration on streaks
- redirection when distracted/absent

## Requirements
Python 3.9+ recommended.

```bash
pip install numpy
```

Optional (only if you want webcam face proxy):
```bash
pip install opencv-python
```

## Run
From inside `assistive-robotics/`:

```bash
python main.py
```

Options:
```bash
python main.py --tasks 10
python main.py --seed 123
python main.py --use-opencv
```

Type `quit` to end the session early.

## Limitations
- No real robot hardware (no motors, sensors, physical embodiment)
- Simplified “attention” (random or face-presence proxy, not real engagement estimation)
- No personalization across days or users (no user model, no long-term memory)
- No clinical validation or stakeholder feedback loop

## Future improvements
- Real sensing: camera + gaze estimation, speech prosody, interaction timing signals
- ROS2 integration: nodes for perception, planning, dialogue, and logging
- Better adaptation: reinforcement learning / bandits for choosing prompts and difficulty
- Accessibility and caregiver controls: adjustable language level, timeouts, consent + privacy controls
- Richer interaction: multimodal (speech + visuals), social cues, co-regulation strategies

