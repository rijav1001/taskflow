INITIAL = 1000.0
GAP = 1000.0
REBALANCE_THRESHOLD = 0.0001

def get_initial_order() -> float:
    """Order for the first card in an empty list"""
    return INITIAL

def get_between_order(before: float | None, after: float | None) -> float:
    """
    Calculate order value for a card inserted between two others.
    - before=None means inserted at the beginning
    - after=None means inserted at the end
    """
    if before is None and after is None:
        return INITIAL
    
    if before is None:
        return after - GAP
    
    if after is None:
        return before + GAP
    
    midpoint = (before + after) / 2.0
    if abs(midpoint - before) < REBALANCE_THRESHOLD or abs(after - midpoint) < REBALANCE_THRESHOLD:
        raise ValueError("rebalance_needed")
    
    return midpoint

def rebalance(orders: list[float]) -> list[float]:
    """
    Rebalance all cards when they get too close together.
    Spreads them evenly with GAP spacing
    """
    count = len(orders)
    return [INITIAL + (i * GAP) for i in range(count)]