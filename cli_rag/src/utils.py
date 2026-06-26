from decimal import Decimal
from typing import Any
from typing import TypedDict


class ModelPrice(TypedDict):
    input: Decimal
    output: Decimal


MODEL_PRICES: dict[str, ModelPrice] = {
    # Standard short-context prices in USD per 1M tokens.
    # Source: https://developers.openai.com/api/docs/pricing
    "gpt-5.4-nano": {
        "input": Decimal("0.20"),
        "output": Decimal("1.25"),
    },
    "gpt-5.4-mini": {
        "input": Decimal("0.75"),
        "output": Decimal("4.50"),
    },
    "gpt-5.4": {
        "input": Decimal("2.50"),
        "output": Decimal("15.00"),
    },
    "gpt-5.4-pro": {
        "input": Decimal("30.00"),
        "output": Decimal("180.00"),
    },
    "gpt-5.5": {
        "input": Decimal("5.00"),
        "output": Decimal("30.00"),
    },
    "gpt-5.5-pro": {
        "input": Decimal("30.00"),
        "output": Decimal("180.00"),
    },
}


def calculate_openai_price(
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-5.4-mini",
    model_prices: dict[str, ModelPrice] | None = None,
    input_price: Decimal | float | int | str | None = None,
    output_price: Decimal | float | int | str | None = None,
) -> dict[str, Any]:
    """
    Calculate OpenAI API cost for a model.

    Prices are USD per 1M tokens. Pass either a model price table or direct
    input/output prices to override the defaults.
    """
    prices = model_prices or MODEL_PRICES

    if input_price is None or output_price is None:
        if model not in prices:
            available_models = ", ".join(prices.keys())
            raise ValueError(
                f"Unknown model: {model}. Available models: {available_models}"
            )

        input_price = prices[model]["input"]
        output_price = prices[model]["output"]

    input_price_decimal = Decimal(str(input_price))
    output_price_decimal = Decimal(str(output_price))

    input_cost = (Decimal(input_tokens) / Decimal("1000000")) * input_price_decimal
    output_cost = (Decimal(output_tokens) / Decimal("1000000")) * output_price_decimal
    total_cost = input_cost + output_cost

    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_price": input_price_decimal,
        "output_price": output_price_decimal,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
    }
