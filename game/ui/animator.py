# game/ui/animator.py

def lerp(a, b, t):
    """Smoothly moves a toward b by factor t (0.0 - 1.0)"""
    return a + (b - a) * t

def lerp_color(a, b, t):
    """Smoothly blends two RGB colors"""
    return (
        int(lerp(a[0], b[0], t)),
        int(lerp(a[1], b[1], t)),
        int(lerp(a[2], b[2], t)),
    )

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def ease_out(t):
    """Starts fast, slows down — good for elements sliding in"""
    return 1 - (1 - t) ** 2

def ease_in(t):
    """Starts slow, speeds up — good for elements sliding out"""
    return t ** 2

def ease_in_out(t):
    """Slow start, fast middle, slow end — good for pans"""
    return t * t * (3 - 2 * t)