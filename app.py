# app.py
import time as tm


from paddle import div
import streamlit as st
import pandas as pd
import os
import json

from modules.document_aliases import normalize_document_name
from modules.vendor_processor import process_vendor
from modules.pdf_reader import extract_pdf_pages
from modules.tender_extractor import extract_requirements
from streamlit_pdf_viewer import pdf_viewer

from database.mongodb import (
    save_tender,
    save_vendor,
    save_evaluation_result,
    get_all_results
)

# 1. Page Config
st.set_page_config(
    page_title="AI Tender Audit System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>

.stApp{
    background:#0B1220;
}

/* Sidebar */

section[data-testid="stSidebar"]{
    background:#111827;
    border-right:1px solid #1F2937;
}

/* Main */

.main-block{
    padding-top:15px;
}

/* Header */

.dashboard-header{
    background:linear-gradient(135deg,#1E3A8A,#2563EB);
    padding:28px;
    border-radius:16px;
    color:white;
    margin-bottom:25px;
    box-shadow:0 10px 35px rgba(0,0,0,.35);
}

/* Cards */

.card{

    background:linear-gradient(180deg,#1A2235,#111827);

    border:1px solid #2B3445;

    border-radius:18px;

    padding:25px;

    min-height:135px;

    transition:.3s;

    box-shadow:0 8px 18px rgba(0,0,0,.35);

}

.card:hover{

    transform:translateY(-6px);

    border:1px solid #3B82F6;

    box-shadow:0 15px 30px rgba(37,99,235,.25);

}

/* Metric */

.metric{

    font-size:34px;

    font-weight:700;

    color:#60A5FA;

    margin-bottom:10px;

}

.metric-title{

    color:#9CA3AF;

    font-size:15px;

}
            
/* Streamlit widget labels */
div[data-testid="stWidgetLabel"] label,
div[data-testid="stWidgetLabel"] p {
    color: #E5E7EB !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

/* Number input label */
div[data-testid="stNumberInput"] label {
    color: #E5E7EB !important;
}

/* File uploader label */
div[data-testid="stFileUploader"] label {
    color: #E5E7EB !important;
}
/* All markdown headings */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
}

/* Buttons */

.stButton>button{

    width:100%;
    height:52px;

    background:#2563EB;

    color:white;

    border:none;

    border-radius:12px;

    font-weight:600;

}

.stButton>button:hover{

    background:#3B82F6;

}

/* Upload */

[data-testid="stFileUploader"]{

    background:#161B22;

    border-radius:15px;

    border:2px dashed #3B82F6;

    padding:20px;

}

/* Success */

.success{

background:#052E16;

padding:10px;

border-radius:10px;

}

/* Warning */

.warning{

background:#3B1D00;

padding:10px;

border-radius:10px;

}
.status-card{
    background:#161B22;
    border-left:5px solid #22C55E;
    padding:18px;
    border-radius:12px;
    margin:12px 0;
    color:white;
    box-shadow:0 6px 15px rgba(0,0,0,.25);
}

.info-card{
    background:#161B22;
    border-left:5px solid #3B82F6;
    padding:18px;
    border-radius:12px;
    margin:12px 0;
    color:white;
}

.warning-card{
    background:#161B22;
    border-left:5px solid #F59E0B;
    padding:18px;
    border-radius:12px;
    margin:12px 0;
    color:white;
}

.error-card{
    background:#161B22;
    border-left:5px solid #EF4444;
    padding:18px;
    border-radius:12px;
    margin:12px 0;
    color:white;
}
.doc-card{

    background:#161B22;

    border:1px solid #2D3748;

    border-radius:18px;

    padding:20px;

    margin-bottom:18px;

    transition:.3s;

    box-shadow:0 8px 18px rgba(0,0,0,.30);

}

.doc-card:hover{

    transform:translateY(-4px);

    border:1px solid #3B82F6;

}

.doc-title{

    color:white;

    font-size:19px;

    font-weight:700;

    margin-bottom:12px;

}

.doc-category{

    color:#60A5FA;

    font-size:14px;

    margin-bottom:8px;

}

.progress-bar{

    background:#1F2937;

    border-radius:8px;

    height:10px;

    overflow:hidden;

}

.progress-fill{

    background:#3B82F6;

    height:10px;

}

.doc-pages{

    color:#9CA3AF;

    font-size:13px;

    margin-top:10px;

}
.table-card{

    background:#161B22;

    border-radius:18px;

    padding:20px;

    border:1px solid #2D3748;

    margin-top:25px;

}

.table-title{

    color:white;

    font-size:24px;

    font-weight:700;

    margin-bottom:18px;

}

.status-ok{

    background:#16A34A;

    color:white;

    padding:6px 12px;

    border-radius:20px;

    font-size:13px;

    font-weight:600;

}

.status-no{

    background:#DC2626;

    color:white;

    padding:6px 12px;

    border-radius:20px;

    font-size:13px;

    font-weight:600;

}

.page-pill{

    background:#2563EB;

    color:white;

    padding:4px 10px;

    border-radius:15px;

    font-size:12px;

}

</style>
 """, unsafe_allow_html=True)
st.markdown("""
    <div class="dashboard-header">

    <h1>🤖 AI Tender Audit System</h1>

    <h4>
    Intelligent Tender Requirement Extraction &
    Vendor Compliance Verification
    </h4>

    <p>
    OCR • LLM • MongoDB • AI Document Verification
    </p>

    </div>
  
""", unsafe_allow_html=True)

# Initialize persistent session state variables
if "required_documents" not in st.session_state:
    st.session_state["required_documents"] = []
if "processed_tender_name" not in st.session_state:
    st.session_state["processed_tender_name"] = None
if "tender_extraction_done" not in st.session_state:
    st.session_state["tender_extraction_done"] = False
if "last_results" not in st.session_state:
    st.session_state["last_results"] = {}
if "matrix_table_rows" not in st.session_state:
    st.session_state["matrix_table_rows"] = []
if "active_doc_keys" not in st.session_state:
    st.session_state["active_doc_keys"] = []
if "preview" not in st.session_state:
    st.session_state["preview"] = None
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
vendor_count = len(st.session_state.get("matrix_table_rows", []))

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="metric">📄 {len(st.session_state["required_documents"])}</div>
        <div class="metric-title">Required Documents</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="metric">👥 {vendor_count}</div>
        <div class="metric-title">Vendors</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <div class="metric">🤖 AI</div>
        <div class="metric-title">Extraction Ready</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="card">
        <div class="metric">🗄 MongoDB</div>
        <div class="metric-title">Connected</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Tender Upload Section
# -----------------------------
st.markdown("## 📄 Upload Tender PDF")
tender_file = st.file_uploader("Tender PDF", type=["pdf"])

if tender_file:
    tender_folder = os.path.join("uploads", "tender")
    os.makedirs(tender_folder, exist_ok=True)
    tender_path = os.path.join(tender_folder, tender_file.name)

    if st.session_state["processed_tender_name"] != tender_file.name:
        st.session_state["tender_extraction_done"] = False
        st.session_state["required_documents"] = []
        st.session_state["processed_tender_name"] = tender_file.name
        st.session_state["last_results"] = {}
        st.session_state["matrix_table_rows"] = []
        st.session_state["active_doc_keys"] = []
        st.session_state["preview"] = None

    if not st.session_state["tender_extraction_done"]:
        with open(tender_path, "wb") as f:
            f.write(tender_file.getbuffer())

        st.markdown("""
            <div class="status-card">

            <h4>✅ Tender Uploaded Successfully</h4>

            Tender document is ready for AI analysis.

            </div>
            """, unsafe_allow_html=True)

        # Extract full layout data. Let tender_extractor execute scoring heuristics.
        pages = extract_pdf_pages(tender_path)
        
        status = st.empty()
        progress = st.progress(0)

        status.markdown("### 📖 Reading Tender PDF...")
        progress.progress(15)

        status.markdown("### 🔍 Running OCR Engine...")
        progress.progress(35)

        status.markdown("### 🤖 AI Extracting Requirements...")
        progress.progress(60)

        # Actual extraction (logic unchanged)
        requirements_json = extract_requirements(pages)

        status.markdown("### ✅ AI Verification Completed")
        tm.sleep(0.5)

        progress.empty()
        status.empty()

        all_docs_dict = {}
        if isinstance(requirements_json, dict):
            # Parse documents according to our new data layout signature
            for doc in requirements_json.get("required_documents", []):
                doc_key = doc.get("key")
                if not doc_key:
                    continue
                    
                all_docs_dict[doc_key.lower()] = {
                    "key": doc_key,
                    "category": doc.get("category", "Other"),
                    "confidence": doc.get("confidence_score", 100),
                    "pages": doc.get("pages", [])
                }   

        required_documents = list(all_docs_dict.values())
        st.session_state["required_documents"] = required_documents
        st.session_state["tender_extraction_done"] = True

        save_tender(
            tender_name=tender_file.name,
            requirements={"required_documents": required_documents}
        )

    st.subheader("📄 Required Documents")

    if st.session_state["required_documents"]:

        pill_html = ""

        cols = st.columns(3)

        for i, doc in enumerate(st.session_state["required_documents"]):

            confidence = doc.get("confidence", 0)
            pages = ", ".join(map(str, doc.get("pages", [])))

            with cols[i % 3]:

                st.markdown(f"""
                <div class="doc-card">

                <div class="doc-title">
                📄 {doc['key']}
                </div>

                <div class="doc-category">
                {doc.get('category','Other')}
                </div>

                <div class="progress-bar">
                    <div class="progress-fill"
                        style="width:{confidence}%;">
                    </div>
                </div>

                <br>

                <b>{confidence}% Confidence</b>

                <div class="doc-pages">

                Pages: {pages if pages else "-"}

                </div>

                </div>
                """, unsafe_allow_html=True)

        st.markdown(pill_html, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="warning-card">

        <h4>⚠ Warning</h4>

        No mandatory documents extracted.

        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Vendor Upload Section
# -----------------------------
st.write("---")
st.subheader("👥 Vendor Document Upload")

vendors_data = []

num_vendors = st.number_input(
    "Number of Vendors to Audit",
    min_value=1,
    max_value=10,
    value=1
)

for i in range(int(num_vendors)):

    st.markdown(f"### 🏢 Vendor {i+1}")

    col1, col2 = st.columns([1,2])

    with col1:
        st.markdown(
            "<p style='color:white;font-size:16px;font-weight:600;'>🏢 Vendor Name</p>",
            unsafe_allow_html=True
        )

        v_name = st.text_input(
            "Vendor Name",
            key=f"vname_{i}",
            label_visibility="collapsed",
            placeholder="Enter vendor company name"
        ).strip()

    with col2:
        v_files = st.file_uploader(
            "Upload Vendor PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            key=f"vfiles_{i}"
        )

    if v_name and v_files:
        vendors_data.append({
            "name": v_name,
            "files": v_files
        })
    st.session_state["vendor_count"] = len(vendors_data)
# -----------------------------
# Process Vendor Evaluation Execution Loop
# -----------------------------
if st.button("🚀 Run Bulk Compliance Audit", type="primary"):
    if not tender_file:
        st.error("❌ Please upload the Tender PDF first at the top of the page.")
    elif len(vendors_data) == 0:
        st.markdown(f"""
        <div class="error-card">

        <h4>❌ Error</h4>

        Please make sure to fill out at least one Vendor Name and upload its corresponding PDFs.

        </div>
        """, unsafe_allow_html=True)
    else:
        required_documents = st.session_state.get("required_documents", [])
        
        if not required_documents:
            st.error("Tender requirements missing. Please re-upload or check your tender file extraction.")
        else:
            table_rows = []
            compiled_results = {}
            required_doc_keys = [doc["key"] for doc in required_documents]

            for vendor in vendors_data:
                current_name = vendor["name"]
                current_files = vendor["files"]
                
                vendor_folder = os.path.join("uploads", "vendors", current_name)
                os.makedirs(vendor_folder, exist_ok=True)

                for file in current_files:
                    save_path = os.path.join(vendor_folder, file.name)
                    with open(save_path, "wb") as f:
                        f.write(file.getbuffer())

                save_vendor(
                    vendor_name=current_name,
                    tender_name=tender_file.name,
                    pdf_path=vendor_folder
                )

                with st.spinner(f"Analyzing {len(current_files)} files for {current_name}..."):
                    result = process_vendor(vendor_folder, required_doc_keys)

                # Normalize all extracted document names
                normalized_result = {}

                for k, v in result.items():
                    std = normalize_document_name(k)
                    if std:
                        normalized_result[std] = v
                    else:
                        normalized_result[k] = v

                result = normalized_result

                # Debug
                print(f"\n===== {current_name} =====")
                print("Result Keys:")
                for k in result.keys():
                    print(k)

                compiled_results[current_name] = result

                vendor_row = {
                    "Vendor": current_name
                }

                # Safe evaluation rendering
                for doc_key in required_doc_keys:
                    info = result.get(doc_key)

                    if info and info.get("status") in ["Present", "verified"]:
                        page_num = info.get('page', 1)
                        vendor_row[doc_key] = f"Given (P{page_num})"
                    elif info and info.get("status") == "unreadable":
                        vendor_row[doc_key] = "⚠️ Unreadable"
                    else:
                        vendor_row[doc_key] = "❌ Missing"

                total = len(required_doc_keys)
                present = sum(
                    1 for info in result.values()
                    if info.get("status") in ["Present", "verified"]
                )
                score = round((present / total) * 100, 2) if total > 0 else 0

                vendor_row["Compliance Score"] = f"{score}%"
                table_rows.append(vendor_row)

                save_evaluation_result(
                    vendor_name=current_name,
                    tender_name=tender_file.name,
                    status="Completed",
                    score=score,
                    document_results=result
                )
            
            st.session_state["last_results"] = compiled_results
            st.session_state["matrix_table_rows"] = table_rows
            st.session_state["active_doc_keys"] = required_doc_keys
            st.session_state["preview"] = None  
            st.balloons()
vendor_count = len(st.session_state["matrix_table_rows"])
doc_count = len(st.session_state["active_doc_keys"])

avg_score = 0
if vendor_count:
    scores = []
    for r in st.session_state["matrix_table_rows"]:
        score = str(r["Compliance Score"]).replace("%","")
        try:
            scores.append(float(score))
        except:
            pass

    if scores:
        avg_score = round(sum(scores)/len(scores),1)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">👥 Vendors</div>
        <div class="metric">{vendor_count}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">📄 Required Documents</div>
        <div class="metric">{doc_count}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">✅ Avg Compliance</div>
        <div class="metric">{avg_score}%</div>
    </div>
    """, unsafe_allow_html=True)
# -----------------------------
# Render AI Vendor Compliance Dashboard (AgGrid)
# -----------------------------

from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd


if st.session_state["matrix_table_rows"]:

    st.write("---")

    st.markdown("""
    <div class="table-card">
        <div class="table-title">
        📊 AI Vendor Compliance Dashboard
        </div>
    </div>
    """, unsafe_allow_html=True)


    df = pd.DataFrame(
        st.session_state["matrix_table_rows"]
    )


    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode="single", use_checkbox=True)


    # Default settings
    gb.configure_default_column(
        resizable=True,
        sortable=True,
        filter=True,
        wrapText=True,
        autoHeight=True,
        minWidth=180
    )


    # Document columns width
    for col in st.session_state["active_doc_keys"]:
        gb.configure_column(
            col,
            width=250,
            minWidth=250,
            wrapText=True
        )


    # Vendor column
    gb.configure_column(
        "Vendor",
        width=180,
        minWidth=180
    )


    # Score column
    gb.configure_column(
        "Compliance Score",
        width=150,
        minWidth=150
    )


    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        height=550,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        theme="streamlit"
    )
    # -----------------------------
    # Row Selection Preview
    # -----------------------------
    selected = grid.get("selected_rows")

    # FIX: Use .empty to check if a DataFrame has rows instead of "if selected:"
    if selected is not None and not selected.empty:
        # Convert the first selected row into a dictionary or Series to get the Vendor name Safely
        first_row = selected.iloc[0]
        st.session_state["selected_vendor"] = first_row["Vendor"]
    
    # Process the active selected vendor if one exists in state
    if "selected_vendor" in st.session_state and st.session_state["selected_vendor"]:
        selected_vendor = st.session_state["selected_vendor"]

        st.success(f"Selected Vendor: {selected_vendor}")
        st.markdown("---")
        st.subheader("📂 Available Evidence")

        vendor_data = st.session_state["last_results"].get(selected_vendor, {})

        for doc, info in vendor_data.items():
            if not info.get("page"):
                continue

            c1, c2, c3 = st.columns([5, 1, 1])
            with c1:
                st.markdown(f"""
                    <div style="color: #FFFFFF; font-size: 16px; margin-bottom: 4px;">
                        📄 <strong style="color: #60A5FA;">{doc}</strong>
                    </div>
                    <div style="color: #9CA3AF; font-size: 14px;">
                        Page <span style="color: #FFFFFF; font-weight: bold;">{info['page']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            with c2:
                st.success("Found")
            with c3:
                if st.button("🔍 Open", key=f"btn_open_{selected_vendor}_{doc}"):
                    st.session_state["preview"] = {
                        "vendor": selected_vendor,
                        "doc": doc,
                        "file": info["file"],
                        "page": info["page"]
                    }
                    st.rerun()

# -----------------------------
# Dynamic Session State File Inspector Viewport
# -----------------------------
if st.session_state.get("preview") is not None:
    preview = st.session_state["preview"]
    target_vendor = preview["vendor"]
    target_doc = preview["doc"]
    target_file = preview["file"]
    target_page = int(preview["page"])  # Ensure integer type
    
    st.write("---")
    st.subheader(f"🔍 Document Target Evidence Viewport: {target_doc}")
    
    resolved_pdf_path = os.path.join("uploads", "vendors", target_vendor, target_file)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        # FIX: Explicit white and bright blue styling for column 1 metrics
        st.markdown(f"""
        <div style="margin-bottom: 15px;">
            <div style="color: #9CA3AF; font-size: 14px; font-weight: 500;">Selected Vendor</div>
            <div style="color: #FFFFFF; font-size: 24px; font-weight: 700; margin-top: 2px;">{target_vendor}</div>
        </div>
        <div style="margin-bottom: 15px;">
            <div style="color: #9CA3AF; font-size: 14px; font-weight: 500;">Target Document Source</div>
            <div style="color: #60A5FA; font-size: 16px; font-weight: 600; word-break: break-all; margin-top: 2px;">{target_file}</div>
        </div>
        <div style="margin-bottom: 20px;">
            <div style="color: #9CA3AF; font-size: 14px; font-weight: 500;">Verified Target Page</div>
            <div style="color: #FFFFFF; font-size: 20px; font-weight: 700; margin-top: 2px;">Page {target_page}</div>
        </div>
        """, unsafe_allow_html=True)
        
        info = st.session_state["last_results"][target_vendor][target_doc]
        if "snippet" in info:
            st.warning(f"📌 **Target Evidence on Page {target_page}:**\n\n\"{info['snippet']}\"")
        
        if st.button("❌ Close Preview", key="btn_close_preview"):
            st.session_state["preview"] = None
            st.rerun()

    with col2:
        if os.path.exists(resolved_pdf_path):
            with open(resolved_pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()

            st.download_button(
                label=f"⬇️ Download {target_file}",
                data=pdf_bytes,
                file_name=target_file,
                mime="application/pdf"
            )

            # FIX: High visibility info banner text
            st.markdown(f"""
            <div style="background: #1E293B; border-left: 4px solid #3B82F6; padding: 12px; border-radius: 6px; margin-bottom: 15px; color: #60A5FA;">
                📜 Full PDF loaded. Highlighting evidence page: <strong>Page {target_page}</strong>
            </div>
            """, unsafe_allow_html=True)

            # -----------------------------
            # Target Page Highlight Box
            # -----------------------------
            # FIX: Switched from <h4> to <span> with inline text color to bypass the global white !important rule
            st.markdown(
                f"""
                <div style="
                    border: 2px solid #22c55e;
                    border-radius: 12px;
                    padding: 14px;
                    margin-bottom: 15px;
                    background: #f0fdf4;
                ">
                <span style="color: #166534 !important; font-weight: 700; font-size: 18px; display: block;">
                🎯 Evidence Located - Page {target_page}
                </span>
                </div>
                """,
                unsafe_allow_html=True
            )

            # -----------------------------
            # Full PDF Viewer (Target Page Level Highlight Only)
            # -----------------------------
            # Injecting CSS to target ONLY the active page div inside the viewer
            st.markdown(f"""
                <style>
                /* Remove any previous block level borders if they persist */
                div[data-testid="stVerticalBlock"] > div:has(embed[type="application/pdf"]),
                div[data-testid="stVerticalBlock"] > div:has(iframe) {{
                    border: none !important;
                    box-shadow: none !important;
                    padding: 0 !important;
                }}
                
                /* Target only the specific active canvas page node */
                div.pdf-viewer-container div.pdf-page-container:nth-child({target_page}),
                div[id^="pdf-viewer"] canvas:nth-of-type({target_page}),
                .pdf-viewer-page:nth-of-type({target_page}) {{
                    border: 4px solid #22c55e !important;
                    border-radius: 8px !important;
                    box-shadow: 0 0 20px rgba(34, 197, 94, 0.4) !important;
                    position: relative !important;
                }}

                /* Render a page counter badge inside the viewport stream */
                .pdf-page-indicator-badge {{
                    background: #22c55e;
                    color: #FFFFFF;
                    font-weight: 700;
                    font-size: 13px;
                    padding: 4px 12px;
                    border-radius: 20px;
                    margin-bottom: 8px;
                    display: inline-block;
                }}
                </style>
                
                <div class="pdf-page-indicator-badge">🖥️ Displaying Document Focus: Page {target_page}</div>
            """, unsafe_allow_html=True)

            pdf_viewer(
                input=pdf_bytes,
                width="100%",
                height=700,
                scroll_to_page=target_page,
                scroll_behavior="smooth"
            )
        else:
            st.error(f"Could not locate PDF: {resolved_pdf_path}")