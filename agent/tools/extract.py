EXTRACTION_TOOL = {
    "name": "extract_product_data",
    "description": "Extract structured product data from raw page text",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "price": {
                "type": "number",
                "description": "Price as float in USD. Use -1 if not found.",
            },
            "rating": {
                "type": "number",
                "description": "Star rating 0-5. Use -1 if not found.",
            },
            "review_count": {
                "type": "integer",
                "description": "Number of reviews. Use -1 if not found.",
            },
            "pros": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Concrete strengths from reviews or product description",
            },
            "cons": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Concrete weaknesses or complaints",
            },
            "extraction_confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
            },
        },
        "required": [
            "title",
            "price",
            "rating",
            "review_count",
            "pros",
            "cons",
            "extraction_confidence",
        ],
    },
}
