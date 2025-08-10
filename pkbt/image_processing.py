from PIL import Image, ImageDraw

def pixel_rgb(path, x, y):
    im = Image.open(path).convert("RGB")  # 3 channels, no alpha
    return im.getpixel((x, y))            # Normal: (x, y)

def pixel_hex(path, x, y):
    r, g, b = pixel_rgb(path, x, y)
    return f"#{r:02x}{g:02x}{b:02x}"

def save_with_crosshair(src_path, out_path, x, y):
    # Load image as RGB
    im = Image.open(src_path).convert("RGB")

    # Create a drawing context
    draw = ImageDraw.Draw(im)

    neon_green = (57, 255, 20)  # RGB neon green, no alpha

    # Vertical line (top to bottom) - x controls horizontal position
    draw.line([(x, 0), (x, im.height - 1)], fill=neon_green, width=1)
    # Horizontal line (left to right) - y controls vertical position  
    draw.line([(0, y), (im.width - 1, y)], fill=neon_green, width=1)

    # Save clone
    im.save(out_path)