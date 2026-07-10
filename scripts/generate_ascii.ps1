param(
    [string]$Source = "assets/Gus.jpg",
    [string]$Optimized = "assets/Gus-optimized.png",
    [string]$Output = "assets/profile-ascii.txt",
    [int]$Width = 44
)

$ErrorActionPreference = "Stop"

python scripts/optimize_image.py $Source $Optimized
python scripts/image_to_ascii.py $Optimized $Output --width $Width
python scripts/render_ascii_svg.py $Optimized $Output
