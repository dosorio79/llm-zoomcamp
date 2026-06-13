MODEL_PRICES = {
    # prices are USD per 1M tokens
    "gpt-5.4-mini": {
        "input": 0.75,
        "output": 4.50,
    },
    "gpt-5.4": {
        "input": 2.50,
        "output": 15.00,
    },
    "gpt-5.5": {
        "input": 5.00,
        "output": 30.00,
    },
}


def calculate_openai_price(
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-5.4-mini",
) -> dict:
    """
    Calculate OpenAI API cost for a given model.

    Prices are assumed to be in USD per 1M tokens.
    """

    if model not in MODEL_PRICES:
        available_models = ", ".join(MODEL_PRICES.keys())
        raise ValueError(
            f"Unknown model: {model}. Available models: {available_models}"
        )

    input_price = MODEL_PRICES[model]["input"]
    output_price = MODEL_PRICES[model]["output"]

    input_cost = (input_tokens / 1_000_000) * input_price
    output_cost = (output_tokens / 1_000_000) * output_price
    total_cost = input_cost + output_cost

    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
    }
