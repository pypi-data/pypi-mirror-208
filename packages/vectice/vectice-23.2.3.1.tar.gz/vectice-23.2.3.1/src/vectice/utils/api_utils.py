INDEX_ORDERED = {"field": "index", "direction": "ASC"}
INDEX_ORDERED_DESC = {"field": "index", "direction": "DESC"}
PAGINATE_OUTPUT = """
            items {{
                {0}
            }}
            page {{
                index
                size
            }}
            total
"""


def get_phase_input(index=1, size=10) -> dict:
    return {"index": index, "size": size}
