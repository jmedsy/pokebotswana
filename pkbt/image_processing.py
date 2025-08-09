from PIL import Image, ImageDraw

def pixel_rgba(path, x, y):
    im = Image.open(path).convert("RGBA")  # ensures 4 channels, sRGB
    return im.getpixel((x, y))             # (R, G, B, A)

def pixel_hex(path, x, y):
    r, g, b, _ = pixel_rgba(path, x, y)
    return f"#{r:02x}{g:02x}{b:02x}"

def save_with_crosshair(src_path, out_path, x, y):
    # Load image
    im = Image.open(src_path).convert("RGBA")

    # Create a drawing context
    draw = ImageDraw.Draw(im)

    neon_green = (57, 255, 20, 255)  # RGBA neon green

    # Vertical line (top to bottom)
    draw.line([(x, 0), (x, im.height - 1)], fill=neon_green, width=1)
    # Horizontal line (left to right)
    draw.line([(0, y), (im.width - 1, y)], fill=neon_green, width=1)

    # Save clone
    im.save(out_path)