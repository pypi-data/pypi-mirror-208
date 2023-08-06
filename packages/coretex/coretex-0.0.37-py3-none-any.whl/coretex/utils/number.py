from decimal import Decimal, ROUND_HALF_UP


def mathematicalRound(value: float, decimalPlaces: int) -> float:
    """
        Performes mathematical (ROUND_HALF_UP) rounding
        Ex. >= 1.5 will be rounded to 2, < 1.5 will be rounded to 1

        Parameters
        ----------
        value : float
            value to be rounded
        decimalPlaces : int
            amount of decimal places to which the value will be rounded

        Returns
        -------
        float -> the rounded value
    """

    decimal = Decimal(str(value))
    places = Decimal(10) ** -decimalPlaces

    return float(decimal.quantize(places, rounding = ROUND_HALF_UP))
