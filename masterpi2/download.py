import kagglehub

# Download latest version
path = kagglehub.dataset_download("stanfordu/street-view-house-numbers")

print("Path to dataset files:", path)