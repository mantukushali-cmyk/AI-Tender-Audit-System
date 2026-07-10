import os

from modules.pdf_reader import extract_pdf_pages
from modules.make_model_extractor import extract_make_model
from modules.technical_spec_extractor import extract_specifications


def process_datasheet(pdf_path):
    """
    Extract Make, Model and Technical Specifications
    from a vendor technical datasheet.
    """

    processed_pages = extract_pdf_pages(pdf_path)

    # -----------------------------
    # Make & Model
    # -----------------------------
    make_model = extract_make_model(processed_pages)

    # -----------------------------
    # Specifications
    # -----------------------------
    specifications = []

    for page in processed_pages:

        specs = extract_specifications(
            page["text"]
        )

        specifications.extend(specs)

    # -----------------------------
    # Remove duplicate specifications
    # -----------------------------
    unique_specs = {}

    for spec in specifications:

        key = (
            spec["parameter"],
            spec["value"],
            spec["unit"]
        )

        unique_specs[key] = spec

    specifications = list(unique_specs.values())

    # -----------------------------
    # Convert to dictionary
    # -----------------------------
    technical_data = {}

    for spec in specifications:

        value = spec["value"]

        if spec["unit"]:
            value = f"{value} {spec['unit']}"

        technical_data[spec["parameter"]] = value

    return {

        "make": make_model["make"],

        "model": make_model["model"],

        "page": make_model["page"],

        "confidence": make_model["confidence"],

        "technical_specifications": technical_data
    }