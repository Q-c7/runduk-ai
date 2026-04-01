"""
Font patch module to try to enable Liberation Sans in tkinter
"""
import tkinter as tk
import tkinter.font as tkFont


def patch_fonts():
    """
    Try to patch tkinter to use Liberation Sans instead of system defaults
    """
    try:
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()
        
        # Try to modify the default fonts
        default_font = tkFont.nametofont("TkDefaultFont")
        text_font = tkFont.nametofont("TkTextFont")
        
        # Configure default fonts to use Liberation Sans
        try:
            default_font.configure(family="Liberation Sans", size=12)
            text_font.configure(family="Liberation Sans", size=12)
        except:
            # If Liberation Sans doesn't work, fall back to gothic
            default_font.configure(family="Helvetica", size=12)
            text_font.configure(family="Helvetica", size=12)
        
        print(f"Default font patched to: {default_font.actual()}")
        print(f"Text font patched to: {text_font.actual()}")
        
        root.destroy()
        return True
    except Exception as e:
        print(f"Font patching failed: {e}")
        return False


if __name__ == "__main__":
    patch_fonts()

