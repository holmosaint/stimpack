import numpy as np

def gabor_filter(size_x, size_y, wavelength, orientation, sigma_x, sigma_y):
    x = np.linspace(-1, 1, size_x)
    y = np.linspace(-1, 1, size_y)
    X, Y = np.meshgrid(x, y)

    # Rotation
    theta = np.deg2rad(orientation)
    X_theta = X * np.cos(theta) + Y * np.sin(theta)
    Y_theta = -X * np.sin(theta) + Y * np.cos(theta)

    # Gabor filter
    gb = np.exp(-0.5 * (X_theta**2 / sigma_x**2 + Y_theta**2 / sigma_y**2)) * np.cos(2 * np.pi * X_theta / wavelength)
    gb = 1 - gb  # Invert to make the center black
    return gb

def gaussian_mask(size_x, size_y, sigma):
    x = np.linspace(-1, 1, size_x)
    y = np.linspace(-1, 1, size_y)
    X, Y = np.meshgrid(x, y)
    mask = np.exp(-0.5 * (X**2 + Y**2) / sigma**2)
    return mask

def generate_gabor_filters(size_x=100, size_y=100, wavelength=0.75, orientation=0, sigma_x=10, sigma_y=10, sigma_mask=0.75):
    gabor = gabor_filter(size_x, size_y, wavelength, orientation, sigma_x, sigma_y)
    mask = gaussian_mask(size_x, size_y, sigma_mask)
    gabor *= mask
    return gabor

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    wavelengths = [0.75]
    orientations = [0, 90]
    sigma_x = 10
    sigma_y = 10
    sigma_mask = 0.75
    size_x = 150
    size_y = 100

    fig, axes = plt.subplots(len(wavelengths), len(orientations), figsize=(12, 8))
    if len(wavelengths) == 1:
        axes = np.array([axes])
    if len(orientations) == 1:
        axes = np.array([[ax] for ax in axes])
        
    for i, wavelength in enumerate(wavelengths):
        for j, orientation in enumerate(orientations):
            gabor = generate_gabor_filters(size_x, size_y, wavelength, orientation, sigma_x, sigma_y, sigma_mask)
            ax = axes[i, j]
            ax.imshow(gabor, cmap='gray')
            ax.set_title(f"λ={wavelength}, θ={orientation}°")
            ax.axis('off')
    plt.show()