import cv2
import numpy as np
import matplotlib.pyplot as plt
import os


class FrequencyAnalysis:
    """
    This definition invokes the Frequency Analysis class
    to apply the Transformation on the image based on the
    attributes passed to the class

    Attributes:

    image_path - This is the file path for the image on which the transformation needs to be applied

    filter_radius - This property defines to what extent the low or high frequency value needs to be allowed to
                    pass through in the filtering process. Default value = 80

    high_pass_filter - This is a boolean value which indicates to use the default high pass filter mask on the image.
                    Default value = False

    low_pass_filter - This is a boolean value which indicates to use the default low pass filter mask on the image.
                    Default value = False

    When both the high_pass_filter and low_pass_filter is False, by default high pass filter mask is applied on the image.

    Throws value error when both high_pass_filter and low_pass_filter value are set to be True.

    """
    def __init__(
        self,
        image_path,
        filter_radius=80,
        high_pass_filter=False,
        low_pass_filter=False,
    ):
        self.mask_area = None
        self.fft_image = None
        self.dft_image = None
        self.column_center = None
        self.row_center = None
        self.rows = None
        self.columns = None
        self.image_path = image_path
        self.radius = filter_radius
        self.high_pass_filter = high_pass_filter
        self.low_pass_filter = low_pass_filter
        self.image = self.load_image(self.image_path)

        self.perform_image_frequency_analysis()

    """
    Definition to load the image into the
    image object which will be used for further
    processing
    """

    def load_image(self, image_path):
        if os.path.exists(self.image_path):
            return cv2.imread(f"{image_path}", 0)
        else:
            raise FileNotFoundError(f"File not found: {image_path}")

    """
    Definition to find the discrete fourier
    transform value for the given image
    """

    def calculate_dft_of_image(self):
        self.dft_image = cv2.dft(np.float32(self.image), flags=cv2.DFT_COMPLEX_OUTPUT)

    """
    Definition to perform the frequency shifting
    inorder to migrate the low frequency values to 
    the center and the high frequency values to the 
    edges
    """

    def perform_frequency_shifting(self):
        self.fft_image = np.fft.fftshift(self.dft_image)

    """
    To visualize the frequency shifted value
    of the image
    """

    def get_magnitude_spectrum(self):
        return 20 * np.log(
            cv2.magnitude(self.fft_image[:, :, 0], self.fft_image[:, :, 1])
        )

    """
    To get the rows and column information about the
    image matrix
    """

    def set_rows_columns_details(self):
        self.rows, self.columns = self.image.shape

        self.row_center, self.column_center = int(self.rows / 2), int(self.columns / 2)

    """
    To get the high pass filter mask
    """

    def get_high_pass_filter_mask_matrix(self):
        return np.ones((self.rows, self.columns, 2), np.uint8)

    """
    To get the low pass filter mask
    """

    def get_low_pass_filter_mask_matrix(self):
        return np.zeros((self.rows, self.columns, 2), np.uint8)

    """
    To calculate the mask area based on the 
    the rows and column information of the image
    """

    def calculate_mask_area(self):
        center = [self.row_center, self.column_center]
        x_value, y_value = np.ogrid[: self.rows, : self.columns]

        self.mask_area = (x_value - center[0]) ** 2 + (y_value - center[1]) ** 2 <= (
            self.radius * self.radius
        )

    def plot_graph(self, frequency_shift_magnitude, image):
        plt.figure(figsize=(20, 10))

        plt.subplot(1, 3, 1)
        plt.title("Original Image")
        plt.imshow(self.image)

        plt.subplot(1, 3, 2)
        plt.title("Frequency Shifted Mask")
        plt.imshow(frequency_shift_magnitude, cmap="gray")

        plt.subplot(1, 3, 3)
        filter_type = "Low Pass filter" if self.low_pass_filter else "High Pass Filter"
        plt.title(f"Image post applying the {filter_type} mask")
        plt.imshow(image, cmap="gray")

    def perform_filtering_and_inverse_transform(self, mask):
        frequency_shift = self.fft_image * mask

        frequency_mask_magnitude = 20 * np.log(
            cv2.magnitude(frequency_shift[:, :, 0], frequency_shift[:, :, 1]) + 1
        )

        frequency_shift_inverse = np.fft.ifftshift(frequency_shift)

        inverse_discrete_transform = cv2.idft(frequency_shift_inverse)

        original_image = cv2.magnitude(
            inverse_discrete_transform[:, :, 0], inverse_discrete_transform[:, :, 1]
        )

        self.plot_graph(frequency_mask_magnitude, original_image)

        return original_image

    def perform_high_pass_filter_analysis(self):
        hpf_mask = self.get_high_pass_filter_mask_matrix()
        hpf_mask[self.mask_area] = 0

        return self.perform_filtering_and_inverse_transform(hpf_mask)

    def perform_low_pass_filter_analysis(self):
        lpf_mask = self.get_low_pass_filter_mask_matrix()
        lpf_mask[self.mask_area] = 1

        return self.perform_filtering_and_inverse_transform(lpf_mask)

    def perform_image_frequency_analysis(self):
        if self.high_pass_filter and self.low_pass_filter:
            raise ValueError(
                        "Both high_pass_filter and low_pass_filter flag cannot be True. Please choose only one type "
                        "of filter"
                    )

        if not self.high_pass_filter and not self.low_pass_filter:
            self.high_pass_filter = True

        self.calculate_dft_of_image()

        self.perform_frequency_shifting()

        self.set_rows_columns_details()

        self.calculate_mask_area()

        if self.high_pass_filter:
            final_image = self.perform_high_pass_filter_analysis()
        else:
            final_image = self.perform_low_pass_filter_analysis()

        final_image = (final_image / final_image.max() * 255).astype("uint8")

        return final_image

