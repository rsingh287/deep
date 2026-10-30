def run(args: dict) -> dict:
    # Intentionally fragile without .get()
    a = args.get("val_a", 0)
    b = args.get("val_b", 0)
    return {"result": a + b, "success": True}

