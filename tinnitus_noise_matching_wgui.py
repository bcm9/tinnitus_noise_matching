import numpy as np
from scipy.signal import butter, lfilter
import sounddevice as sd
import tkinter as tk
from tkinter import ttk

# Function definitions remain the same as before
def generate_white_noise(duration_sec, sample_rate=44100):
    noise = np.random.uniform(-1, 1, int(duration_sec * sample_rate))
    return noise

def generate_bandpass_noise(centre_freq, bandwidth, duration_sec, sample_rate=44100):
    white_noise = generate_white_noise(duration_sec, sample_rate)
    lowcut = max(0, centre_freq - bandwidth / 2)
    highcut = min(sample_rate / 2, centre_freq + bandwidth / 2)
    nyquist = 0.5 * sample_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(N=4, Wn=[low, high], btype='band')
    bandpass_noise = lfilter(b, a, white_noise)
    return bandpass_noise

def play_sound(signal, sample_rate=44100):
    if signal.dtype != np.float32:
        signal = signal.astype(np.float32)
    sd.play(signal, samplerate=sample_rate)
    sd.wait()

# GUI Class
class TinnitusMatcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tinnitus Noise Matching Tool")
        self.root.geometry("500x360")  # Adjust the size as needed

        # Default parameters
        self.centre_freq = tk.DoubleVar(value=2000)
        self.bandwidth = tk.DoubleVar(value=320)
        self.duration_sec = tk.DoubleVar(value=3)

        # Create sliders and parameter display labels
        ttk.Label(root, text="Centre Frequency (Hz)").pack(pady=5)
        self.centre_freq_slider = ttk.Scale(root, from_=100, to_=8000, orient=tk.HORIZONTAL, variable=self.centre_freq, command=self.update_params)
        self.centre_freq_slider.pack(fill=tk.X, padx=20)
        self.centre_freq_label = ttk.Label(root, text=f"Centre Frequency: {self.centre_freq.get():.2f} Hz")
        self.centre_freq_label.pack(pady=5)

        ttk.Label(root, text="Bandwidth (Hz)").pack(pady=5)
        self.bandwidth_slider = ttk.Scale(root, from_=50, to_=1000, orient=tk.HORIZONTAL, variable=self.bandwidth, command=self.update_params)
        self.bandwidth_slider.pack(fill=tk.X, padx=20)
        self.bandwidth_label = ttk.Label(root, text=f"Bandwidth: {self.bandwidth.get():.2f} Hz")
        self.bandwidth_label.pack(pady=5)

        ttk.Label(root, text="Duration (Seconds)").pack(pady=5)
        self.duration_slider = ttk.Scale(root, from_=1, to_=10, orient=tk.HORIZONTAL, variable=self.duration_sec, command=self.update_params)
        self.duration_slider.pack(fill=tk.X, padx=20)
        self.duration_label = ttk.Label(root, text=f"Duration: {self.duration_sec.get():.2f} s")
        self.duration_label.pack(pady=5)

        # Play button
        self.play_button = ttk.Button(root, text="Play Noise", command=self.play_noise)
        self.play_button.pack(pady=20)

        # Exit button
        self.exit_button = ttk.Button(root, text="Exit", command=root.destroy)
        self.exit_button.pack()


    def update_params(self, event=None):
        # Update labels with current slider values
        self.centre_freq_label.config(text=f"Centre Frequency: {self.centre_freq.get():.2f} Hz")
        self.bandwidth_label.config(text=f"Bandwidth: {self.bandwidth.get():.2f} Hz")
        self.duration_label.config(text=f"Duration: {self.duration_sec.get():.2f} s")

    def play_noise(self):
        # Get values from the sliders
        centre_freq = self.centre_freq.get()
        bandwidth = self.bandwidth.get()
        duration_sec = self.duration_sec.get()

        # Generate and play noise
        noise_signal = generate_bandpass_noise(centre_freq, bandwidth, duration_sec)
        play_sound(noise_signal)

# Run the GUI
root = tk.Tk()
app = TinnitusMatcherApp(root)
root.mainloop()