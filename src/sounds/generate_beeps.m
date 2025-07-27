% ------------------------------------------------------------
% Generate and save oddball tones
% ------------------------------------------------------------
fs         = 44100;      % Sample rate (Hz) – safe for most devices
dur_s      = 0.100;      % Tone length (s)  – 100 ms
ramp_ms    = 5;          % Cos² ramp length (ms)
freqs      = [500 1000]; % [standard, target] frequencies (Hz)
filenames  = ["500Hz.wav","1000Hz.wav"];

t          = (0:1/fs:dur_s-1/fs).';       % column-vector time axis
ramp_len   = round(ramp_ms/1000*fs);      % samples in each ramp
envelope   = ones(size(t));               % start flat

% Raised-cosine ramp (half-cycle cosine^2)
r          = linspace(0,pi/2,ramp_len).';
cos2_ramp  = sin(r).^2;

envelope(1:ramp_len)               = cos2_ramp;             % fade-in
envelope(end-ramp_len+1:end)       = flipud(cos2_ramp);     % fade-out

for k = 1:2
    y = envelope .* sin(2*pi*freqs(k)*t);                   % tone
    y = y / max(abs(y));                                    % normalise
    audiowrite(filenames(k), y, fs, 'BitsPerSample', 16);   % save
    fprintf('Saved %s (%g Hz)\n', filenames(k), freqs(k));
end
