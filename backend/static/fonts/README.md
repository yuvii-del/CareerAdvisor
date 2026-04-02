# Vijaya Font for Tamil PDF Generation

## Purpose
The Vijaya font is required for proper Tamil Unicode rendering in PDF reports. Without this font, Tamil text may not display correctly in downloaded PDFs.

## Installation

### Windows (Most Common)
Vijaya font typically comes pre-installed with Windows. Check these locations:
- `C:\Windows\Fonts\Vijaya.ttf`
- `C:\Windows\Fonts\vijaya.ttf`

If not found, you can download it from:
1. Microsoft's official font repository
2. Tamil Murasu website
3. Any free Tamil font collection

### Manual Installation for This Project
1. Download `Vijaya.ttf`
2. Place it in this directory: `backend/static/fonts/Vijaya.ttf`
3. The PDF generator will automatically detect and use it

### Linux/Mac
Download and install Vijaya font:
```bash
# Create local fonts directory
mkdir -p ~/.local/share/fonts

# Copy Vijaya.ttf to fonts directory
cp Vijaya.ttf ~/.local/share/fonts/

# Update font cache
fc-cache -fv
```

Then copy the font to `backend/static/fonts/Vijaya.ttf` for the application to use.

## Verification
After installation, when generating a Tamil career report PDF:
- The PDF should render Tamil text clearly
- All Unicode characters should display properly
- Text should be readable across all devices

## Fallback Behavior
If Vijaya font is not found:
- PDF generation will still work
- Tamil text may not render correctly
- A warning message will appear in the PDF

## Alternative Fonts
If Vijaya is not available, these Tamil fonts also work well:
- Latha (comes with Windows)
- Bamini
- AnjaliOldLipi
- Noto Sans Tamil (Google Fonts)

To use an alternative, place it in the fonts directory and update the font registration code in `advisor/views.py`.
