from countries.IS.document_types.not_doc import NOTDocument
from countries.IS.document_types.rem import REMDocument
from countries.IS.document_types.can_dp import CanDpDocument
from countries.IS.document_types.can_ph_wsv import CanPhWsvDocument
from countries.IS.document_types.can_ph_nsv import CanPhNsvDocument

# Registry of all document types
# Add new document types here as they are built
IS_DOCUMENT_REGISTRY = {
    "NOT": NOTDocument,
    "REM": REMDocument,
    "CAN_DP": CanDpDocument,
    "CAN_PH_WSV": CanPhWsvDocument,
    "CAN_PH_NSV": CanPhNsvDocument,
    # "AL": ALDocument,
}


def get_document_handler(doc_type: str):
    """
    Get the document handler for a given document type.

    Args:
        doc_type: Document type code (e.g., "NOT", "AL").

    Returns:
        Instance of the document handler.

    Raises:
        ValueError: If document type is unknown.
    """
    cls = DOCUMENT_REGISTRY.get(doc_type.upper())
    if not cls:
        available = ", ".join(DOCUMENT_REGISTRY.keys())
        raise ValueError(
            f"Unknown document type: '{doc_type}'. Available types: {available}"
        )
    return cls()
