def find_evidence(
    pages,
    aliases,
    file_name
):

    for page in pages:

        text = page["text"].lower()

        for alias in aliases:

            if alias.lower() in text:

                return {
                    "status": "Present",
                    "file": file_name,
                    "page": page["page"]
                }

    return {
        "status": "Missing",
        "file": file_name,
        "page": None
    }