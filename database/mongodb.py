from pymongo import MongoClient
from datetime import datetime

# ==========================
# MongoDB Connection
# ==========================

client = MongoClient(
    "mongodb://127.0.0.1:27017/",
    serverSelectionTimeoutMS=5000
)

# Test Connection
try:
    client.admin.command("ping")
    print("✅ MongoDB Connected Successfully")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")

db = client["tender_audit_db"]

# Collections
tenders_collection = db["tenders"]
vendors_collection = db["vendors"]
results_collection = db["evaluation_results"]


# ==========================
# Tender Operations
# ==========================

def save_tender(tender_name, requirements):
    """
    Save a tender and its required documents.
    """

    data = {
        "tender_name": tender_name,
        "requirements": requirements,
        "created_at": datetime.utcnow()
    }

    result = tenders_collection.insert_one(data)

    return result.inserted_id


def get_tender(tender_name):
    """
    Get a tender by name.
    """

    return tenders_collection.find_one(
        {"tender_name": tender_name},
        {"_id": 0}
    )


def get_all_tenders():
    """
    Return all tenders.
    """

    return list(
        tenders_collection.find({}, {"_id": 0})
    )


# ==========================
# Vendor Operations
# ==========================

def save_vendor(
    vendor_name,
    tender_name,
    pdf_path
):
    """
    Save vendor information.
    """

    data = {
        "vendor_name": vendor_name,
        "tender_name": tender_name,
        "pdf_path": pdf_path,
        "created_at": datetime.utcnow()
    }

    result = vendors_collection.insert_one(data)

    return result.inserted_id


def get_vendor(vendor_name):
    """
    Get vendor details.
    """

    return vendors_collection.find_one(
        {"vendor_name": vendor_name},
        {"_id": 0}
    )


def get_all_vendors():
    """
    Return all vendors.
    """

    return list(
        vendors_collection.find({}, {"_id": 0})
    )


# ==========================
# Evaluation Results
# ==========================

def save_evaluation_result(
    vendor_name,
    tender_name,
    status,
    score,
    document_results
):
    """
    Save evaluation results.
    """

    data = {
        "vendor_name": vendor_name,
        "tender_name": tender_name,
        "status": status,
        "score": score,
        "document_results": document_results,
        "created_at": datetime.utcnow()
    }

    result = results_collection.insert_one(data)

    return result.inserted_id


def get_vendor_result(vendor_name):
    """
    Get evaluation result of a vendor.
    """

    return results_collection.find_one(
        {"vendor_name": vendor_name},
        {"_id": 0}
    )


def get_all_results():
    """
    Return all evaluation results.
    """

    return list(
        results_collection.find({}, {"_id": 0})
    )


# ==========================
# Delete Operations
# ==========================

def delete_vendor(vendor_name):
    """
    Delete vendor and its evaluation results.
    """

    vendors_collection.delete_one(
        {"vendor_name": vendor_name}
    )

    results_collection.delete_many(
        {"vendor_name": vendor_name}
    )


def delete_tender(tender_name):
    """
    Delete tender, vendors and evaluation results.
    """

    tenders_collection.delete_one(
        {"tender_name": tender_name}
    )

    vendors_collection.delete_many(
        {"tender_name": tender_name}
    )

    results_collection.delete_many(
        {"tender_name": tender_name}
    )