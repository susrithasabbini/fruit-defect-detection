import cv2
import os
import numpy as np
import pandas as pd
from skimage import io, color, img_as_ubyte
from skimage.feature import graycomatrix, graycoprops
from tqdm import tqdm


# Function to calculate GLCM features
def calculate_glcm(image):
    # Convert image to grayscale
    gray_image = color.rgb2gray(image)

    # Convert to uint8 for GLCM computation
    gray_image = img_as_ubyte(gray_image)

    # Define GLCM properties
    distances = [1, 2, 3]  # Distances for co-occurrence matrix
    angles = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]  # Angles for co-occurrence matrix

    # Calculate GLCM
    glcm = graycomatrix(
        gray_image, distances=distances, angles=angles, symmetric=True, normed=True
    )

    # Calculate GLCM properties
    contrast = graycoprops(glcm, "contrast")
    correlation = graycoprops(glcm, "correlation")

    # Return GLCM features as a 1D array
    return np.array(
        [
            contrast.mean(),
            correlation.mean(),
        ]
    )


# Function to calculate average intensity (Gray) features
def calculate_average_color(image):
    # Calculate average intensity
    avg_intensity = np.mean(image, axis=(0, 1))

    return avg_intensity


# Function to load images and extract features
def load_images_and_extract_features(folder):
    features = []  # Features
    labels = []  # Labels
    for class_folder in os.listdir(folder):
        if not os.path.isdir(os.path.join(folder, class_folder)):
            continue  # Skip if not a directory
        for filename in tqdm(os.listdir(os.path.join(folder, class_folder))):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                image = io.imread(os.path.join(folder, class_folder, filename))

                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                _, mango_mask = cv2.threshold(
                    gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )

                # Apply mask to color image
                masked_image = cv2.bitwise_and(image, image, mask=mango_mask)

                cv2.imshow("Masked Image", masked_image)

                glcm_features = calculate_glcm(masked_image)
                color_features = calculate_average_color(masked_image)

                # Combine GLCM and color features
                features.append(np.concatenate((glcm_features, color_features)))

                labels.append(class_folder)  # Use folder name as label

    return features, labels


# Modify the thermal data folder path
thermal_folder = "data/Thermal imaging"

# Load images and extract features for train, val, and test folders
train_features, train_labels = load_images_and_extract_features(
    os.path.join(thermal_folder, "train")
)
val_features, val_labels = load_images_and_extract_features(
    os.path.join(thermal_folder, "val")
)
test_features, test_labels = load_images_and_extract_features(
    os.path.join(thermal_folder, "test")
)

# Create DataFrames for train, val, and test sets
train_df = pd.DataFrame(
    train_features,
    columns=[
        "Contrast",
        "Correlation",
        "Avg_Red",
        "Avg_Green",
        "Avg_Blue",
    ],
)
train_df["Label"] = train_labels

val_df = pd.DataFrame(
    val_features,
    columns=[
        "Contrast",
        "Correlation",
        "Avg_Red",
        "Avg_Green",
        "Avg_Blue",
    ],
)
val_df["Label"] = val_labels

test_df = pd.DataFrame(
    test_features,
    columns=[
        "Contrast",
        "Correlation",
        "Avg_Red",
        "Avg_Green",
        "Avg_Blue",
    ],
)
test_df["Label"] = test_labels

# Save the DataFrames to CSV files
train_csv = "train.csv"
val_csv = "val.csv"
test_csv = "test.csv"

train_df.to_csv(train_csv, index=False)
val_df.to_csv(val_csv, index=False)
test_df.to_csv(test_csv, index=False)

print("Train CSV saved to:", train_csv)
print("Val CSV saved to:", val_csv)
print("Test CSV saved to:", test_csv)
