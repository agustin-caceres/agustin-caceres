param(
    [string]$Source = "assets/cerati-2.jpeg",
    [string]$Optimized = "assets/cerati-2-optimized.png",
    [string]$Output = "assets/profile-ascii.txt",
    [int]$Width = 44
)

$ErrorActionPreference = "Stop"

python scripts/optimize_image.py $Source $Optimized
python scripts/image_to_ascii.py $Optimized $Output --width $Width
python scripts/build_profile_svg.py $Optimized $Output
