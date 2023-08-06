try:
    from rich import print

    def log(*args, **kwargs):
        print("[green][MyStrom][/green] -", *args, **kwargs)
except ImportError:
    print("[INFO] Couldn't import rich!")

    def log(*args, **kwargs):
        print("[MyStrom] -", *args, **kwargs)