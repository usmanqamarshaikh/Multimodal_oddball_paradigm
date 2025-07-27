# Visual / Auditory Oddball Paradigm

A **light‑weight, Kivy‑based ERP task** that runs out‑of‑the‑box on desktop **and** Android (Pydroid 3).  
It implements four classic oddball paradigms (visual, audio, and cross‑modal) and streams event markers via **Lab Streaming Layer** for synchronised EEG recording.

---

## Why oddballs?

In an *oddball* design, infrequent **target** stimuli are randomly embedded among frequent **standard** stimuli.  
The human brain responds to these probability violations with a large **P300** (≈300 ms post‑stimulus) and other mismatch fields—corner‑stones of cognitive and clinical EEG research.  
Applications range from attention studies and workload monitoring to P300‑based brain‑computer interfaces.

---

## What the project does

| Mode | Visual stream | Auditory stream | Typical use‑case | Event codes (LSL / CSV) |
|------|---------------|-----------------|------------------|--------------------------|
| **0 Visual** | Colour oddball (grey → blue square) | — | Pure visual P300 | 1 = std, **2 = tgt** |
| **1 AV target** | Same as above | Tone **only** on targets (1 kHz) | Cross‑modal P300 boost | 1 = std, **3 = AV tgt** |
| **2 Bimodal** | Colour oddball | 500 Hz standard / 1 kHz target | Classical multimodal oddball | 11 = std, **12 = tgt** |
| **3 Auditory** | Fixation cross only | 500 Hz standard / 1 kHz target | Auditory‑only P300 | 21 = std, **22 = tgt** |

Every trial also flashes a **50 × 50 px white square** in the upper‑left for photodiode timing.

---

## Quick start

```bash
git clone https://github.com/usmanqamarshaikh/Multimodal_oddball_paradigm.git
cd Multimodal_oddball_paradigm
pip install -r requirements.txt            # Kivy, PyYAML, PyLSL
python -m src.run_paradigm                 # runs with config.yaml defaults
```

## Configure the experiment
All user‑tunable parameters live in config.yaml:

```yaml
paradigm_mode: 1          # 0‑3 (see table above)
n_trials: 200             # total trials
std_to_target_ratio: 0.8  # 80 % standards
pre_start_delay_s: 10
fixation_duration_s: 0.5
stim_duration_s: 0.3
isi_mean_s: 0.8
isi_jitter_s: 0.2
std_color:  [0.6,0.6,0.6,1]   # RGBA
targ_color: [0.0,0.6,1.0,1]
```

Save the file and rerun the 'run_paradigm' from src folder.

## Output files & streams
paradigm_log.csv – trial index, mode, stimulus type, event code, Unix timestamp.

LSL stream – integer event codes for real‑time EEG sync (OddballMarkers).

Photodiode flash for hardware‑ground‑truth onset detection.

## Requirements

Install with
```bash
pip install -r requirements.txt
```

If you use this paradigm, please cite classic P300 oddball work such as:

Farwell, L. A., & Donchin, E. (1988). Talking off the top of your head: toward a mental prosthesis utilizing event‑related brain potentials. Human Factors, 30(2), 203–211.

and reference this GitHub repository. :)
