import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
import sounddevice as sd
from scipy.signal import butter, lfilter

########################################################################################################
# Generate white noise
########################################################################################################
def generate_white_noise(duration_sec, sample_rate=44100):
    """
    Generate a white noise signal.
    
    Parameters:
    duration_sec (float): Duration of the noise in seconds
    sample_rate (int): Sampling rate (e.g., 44100 samples per second)
    
    Returns:
    np.array: The generated white noise signal
    """
    # Generate white noise: random values between -1 and 1
    noise = np.random.uniform(-1, 1, int(duration_sec * sample_rate))
    return noise

########################################################################################################
# Generate band-pass noise (noise band) with given bandwidth and centre frequency
########################################################################################################
def generate_bandpass_noise(centre_freq, bandwidth, duration_sec, sample_rate=44100):
    """
    Generate a band-pass noise signal (noise within a specific frequency band).
    
    Parameters:
    centre_freq (float): Centre frequency of the noise band (in Hz)
    bandwidth (float): The bandwidth of the noise (in Hz)
    duration_sec (float): Duration of the noise in seconds
    sample_rate (int): Sampling rate (e.g., 44100 samples per second)
    
    Returns:
    np.array: The generated band-pass noise signal
    """
    # Generate white noise first
    white_noise = generate_white_noise(duration_sec, sample_rate)
    
    # Define the low and high cut-off frequencies for the band-pass filter
    lowcut = max(0, centre_freq - bandwidth / 2)
    highcut = min(sample_rate / 2, centre_freq + bandwidth / 2)
    
    # Use a Butterworth band-pass filter
    nyquist = 0.5 * sample_rate  # Nyquist frequency
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(N=4, Wn=[low, high], btype='band')
    
    # Apply the filter to the white noise
    bandpass_noise = lfilter(b, a, white_noise)
    
    return bandpass_noise

########################################################################################################
# Play audio signal directly in Python
########################################################################################################
def play_sound(signal, sample_rate=44100):
    """
    Play the given audio signal using sounddevice.
    
    Parameters:
    signal (np.array): The audio signal to play
    sample_rate (int): The sample rate of the audio (default is 44100 Hz)
    """
    # Ensure that the signal is in a floating-point format (if not already)
    if signal.dtype != np.float32:
        signal = signal.astype(np.float32)
    
    # Play the signal
    sd.play(signal, samplerate=sample_rate)
    
    # Wait until the sound finishes playing
    sd.wait()

########################################################################################################
# Listener tinnitus matching
########################################################################################################
def tinnitus_matching():
    """
    Interactive tinnitus matching process where the listener adjusts the centre frequency and bandwidth
    to match their tinnitus sound.
    """
    sample_rate = 44100  # sampling rate
    duration_sec = 3  # second of noise to play
    
    # Initial parameters for centre frequency and bandwidth
    centre_freq = 2000
    bandwidth = 320
    
    print("Starting tinnitus matching.")
    # print(f"Initial centre frequency: {centre_freq} Hz, bandwidth: {bandwidth} Hz.")
    
    octave_factor = 2 ** (1/3)
     
    while True:
        # Generate the band-pass noise with current parameters
        noise_signal = generate_bandpass_noise(centre_freq, bandwidth, duration_sec, sample_rate)
        
        # Play the generated noise
        play_sound(noise_signal, sample_rate)
        
        # Get listener feedback
        print("\nAdjust the sound to match your tinnitus:")
        print("[1] Increase centre frequency")
        print("[2] Decrease centre frequency")
        print("[3] Increase bandwidth")
        print("[4] Decrease bandwidth")
        print("[5] Increase duration")
        print("[6] Decrease duration")
        print("[7] Play sound again")
        print("[0] Exit and save matched parameters")
        
        user_input = input("Enter your choice: ")
        
        if user_input == '1':
            centre_freq *= octave_factor   # Increase centre frequency
        elif user_input == '2':
            centre_freq /= octave_factor  # Decrease centre frequency
        elif user_input == '3':
            bandwidth += 50  # Increase bandwidth
        elif user_input == '4':
            bandwidth -= 50  # Decrease bandwidth
        elif user_input == '5':
            duration_sec += 1  # Increase duration
        elif user_input == '6':
            duration_sec -= 1  # Decrease duration  
        elif user_input == '7':
            continue  # Play sound again
        elif user_input == '0':
            break
        else:
            print("Invalid input, please try again.")
    
    return centre_freq, bandwidth, sample_rate, duration_sec

# Start the tinnitus matching process
matched_freq, matched_bandwidth, sample_rate, duration_sec = tinnitus_matching()

print(f"Matched tinnitus parameters: Centre frequency = {matched_freq} Hz, Bandwidth = {matched_bandwidth} Hz, Duration: {duration_sec} s.")

matched_noise = generate_bandpass_noise(matched_freq, matched_bandwidth, duration_sec)

########################################################################################################
# Plot signals
########################################################################################################
plt.rcParams['font.family'] = 'Calibri'

# Time array for plotting
time = np.linspace(0, duration_sec, int(sample_rate * duration_sec))

# Function to compute FFT and frequency axis
def compute_fft(signal, sample_rate):
    fft_result = np.fft.fft(signal)
    fft_freq = np.fft.fftfreq(len(signal), 1 / sample_rate)
    return fft_freq[:len(fft_result)//2], np.abs(fft_result[:len(fft_result)//2])

# Compute FFT for the band-pass noise signal
fft_freq_bandpass, fft_bandpass = compute_fft(matched_noise, sample_rate)

# Create a 2x1 plot (time-domain and frequency-domain)
fig, axs = plt.subplots(2, 1, figsize=(10, 9))

# Plot noise in the frequency domain
axs[0].plot(fft_freq_bandpass, fft_bandpass, color='orange')
axs[0].set_title('Matched Tinnitus Noise', fontsize=18, fontweight='bold')
axs[0].set_xlabel('Frequency (Hz)', fontsize=16)
axs[0].set_ylabel('Magnitude', fontsize=16)
axs[0].set_xlim([0, matched_freq*2])
axs[0].grid(True, linestyle='--', alpha=0.3)

# Plot noise in the time domain
axs[1].plot(time, matched_noise, color='orange')
axs[1].set_title('', fontsize=18, fontweight='bold')
axs[1].set_xlabel('Time (s)', fontsize=16)
axs[1].set_ylabel('Amplitude', fontsize=16)
axs[1].grid(True, linestyle='--', alpha=0.3)

# Adjust layout
plt.tight_layout()
folder = 'C:/Users/bc22/OneDrive/Documents/code/tinnitus_sound_generator/'
plt.savefig(folder+'matched_tinnitus_noise.png', dpi=300, bbox_inches='tight')
plt.show()