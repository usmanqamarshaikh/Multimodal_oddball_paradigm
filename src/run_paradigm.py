import yaml, csv, random, time, sys
from pathlib import Path

...

# ---------- load config ------------------------------------
cfg = yaml.safe_load(open(Path(__file__).parent.parent/'config.yaml'))

PARADIGM_MODE       = cfg['paradigm_mode']
PRE_START_DELAY_S   = cfg['pre_start_delay_s']
N_TRIALS            = cfg['n_trials']
STD_TO_TARGET_RATIO = cfg['std_to_target_ratio']
FIXATION_DURATION_S = cfg['fixation_duration_s']
STIM_DURATION_S     = cfg['stim_duration_s']
ISI_MEAN_S          = cfg['isi_mean_s']
ISI_JITTER_S        = cfg['isi_jitter_s']
FULLSCREEN          = cfg['fullscreen']

# Photodiode rectangle (upper-left)
MARKER_SIZE_PX      = cfg['marker_size_px']
MARKER_ON_MS        = cfg['marker_on_ms']
MARKER_OFF_MS       = cfg['marker_off_ms']


STD_COLOR           = tuple(cfg['std_color'])
TARG_COLOR          = tuple(cfg['targ_color'])
SQUARE_REL_SIZE     = cfg['square_rel_size']


STD_TONE_FILE       = "sounds/500Hz.wav"
TARG_TONE_FILE      = "sounds/1000Hz.wav"
LOG_FILENAME        = cfg['log_filename']


# -----------------------------------------------------------

import csv, random, time
from pathlib import Path
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.core.audio import SoundLoader

try:
    from pylsl import StreamInfo, StreamOutlet
    LSL_AVAILABLE = True
except ModuleNotFoundError:
    LSL_AVAILABLE = False

# ------------- Stimulus widget -----------------------------
class StimulusWidget(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas:
            Color(0,0,0)
            self.bg = Rectangle(size=Window.size, pos=(0,0))
        with self.canvas.after:
            self.square_color = Color(0,0,0,0)
            self.square_rect  = Rectangle(pos=(0,0), size=(0,0))
            self.marker_color = Color(0,0,0,1)
            self.marker_rect  = Rectangle(pos=(0, Window.height-MARKER_SIZE_PX),
                                          size=(MARKER_SIZE_PX, MARKER_SIZE_PX))
        Window.bind(on_resize=self._layout)
        self.fix = None

    def _layout(self,*_):
        self.bg.size = Window.size
        self.marker_rect.pos = (0, Window.height-MARKER_SIZE_PX)
        if self.fix: self.fix.center = Window.center

    def show_fix(self):
        if self.fix is None:
            self.fix = Label(text="+", font_size="60sp", color=(1,1,1,1))
        if not self.fix.parent:
            self.fix.center = Window.center
            self.add_widget(self.fix)

    def clear_visual(self):
        self.square_color.a = 0
        if self.fix and self.fix.parent:
            self.remove_widget(self.fix)

    def show_square(self, target):
        self.square_color.rgba = TARG_COLOR if target else STD_COLOR
        side = Window.height * SQUARE_REL_SIZE
        self.square_rect.size = (side, side)
        self.square_rect.pos  = (Window.center[0]-side/2, Window.center[1]-side/2)
        self.square_color.a   = 1

    def flash(self, n):
        total=n*2
        def step(k):
            if k>=total:
                self.marker_color.rgba=(0,0,0,1); return
            self.marker_color.rgba=(1,1,1,1) if k%2==0 else (0,0,0,1)
            delay = MARKER_ON_MS if k%2==0 else MARKER_OFF_MS
            Clock.schedule_once(lambda dt: step(k+1), delay)
        step(0)

# ------------- Main App ------------------------------------
class OddballApp(App):
    def build(self):
        if FULLSCREEN: Window.fullscreen=True
        self.sw = StimulusWidget()

        self.t_std  = SoundLoader.load(STD_TONE_FILE)
        self.t_targ = SoundLoader.load(TARG_TONE_FILE)

        n_std=int(N_TRIALS*STD_TO_TARGET_RATIO); n_targ=N_TRIALS-n_std
        self.trials = ([0]*n_std)+([1]*n_targ); random.shuffle(self.trials)

        if LSL_AVAILABLE:
            info=StreamInfo("OddballMarkers","Markers",1,0,"int32","colour_oddball")
            self.outlet=StreamOutlet(info)
        else:
            self.outlet=None

        self.logf=open(LOG_FILENAME,'w',newline='')
        self.csvw=csv.writer(self.logf)
        self.csvw.writerow(["trial","mode","stim","code","unix"])
        self.idx=-1

        # ---- idle screen before task starts ----
        self._show_ready()
        Clock.schedule_once(self._next, PRE_START_DELAY_S)
        return self.sw

    def _show_ready(self):
        msg = Label(text="Get ready…", font_size="40sp", color=(1,1,1,1))
        msg.center=Window.center
        self.sw.add_widget(msg)
        # remove after delay
        Clock.schedule_once(lambda dt: self.sw.remove_widget(msg), PRE_START_DELAY_S)

    # ---------- trial helpers ------------------------------
    def _code(self,s):
        if PARADIGM_MODE==0:return 1+s
        if PARADIGM_MODE==1:return 3 if s else 1
        if PARADIGM_MODE==2:return 12 if s else 11
        if PARADIGM_MODE==3:return 22 if s else 21

    def _next(self,dt):
        self.idx+=1
        if self.idx>=len(self.trials): self._end(); return
        self.sw.show_fix(); Clock.schedule_once(self._stim,FIXATION_DURATION_S)

    def _stim(self,dt):
        s=self.trials[self.idx]
        if PARADIGM_MODE in (0,1,2): self.sw.show_square(bool(s))
        self.sw.flash(2 if s else 1)
        tone=None
        if PARADIGM_MODE==1 and s: tone=self.t_targ
        elif PARADIGM_MODE in (2,3): tone=self.t_targ if s else self.t_std
        if tone: tone.stop(); tone.play()
        code=self._code(s); ts=time.time()
        self.csvw.writerow([self.idx,PARADIGM_MODE,s,code,f"{ts:.6f}"]); self.logf.flush()
        if self.outlet: self.outlet.push_sample([code],ts)
        Clock.schedule_once(self._isi,STIM_DURATION_S)

    def _isi(self,dt):
        self.sw.square_color.a=0
        Clock.schedule_once(self._next, ISI_MEAN_S+random.uniform(-ISI_JITTER_S,ISI_JITTER_S))

    def _end(self):
        self.sw.clear_visual()
        end=Label(text="End of Experiment\nThank you!", font_size="40sp", color=(1,1,1,1)); end.center=Window.center
        self.sw.add_widget(end)
        if self.outlet: self.outlet.push_sample([-1],time.time())
        self.logf.close()

# ---------------- Run -------------------------------------------
if __name__=='__main__':
    OddballApp().run()

