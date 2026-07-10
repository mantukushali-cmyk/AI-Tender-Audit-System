# 🤖 AI Tender Audit System

An AI-powered Tender Requirement Extraction and Vendor Compliance Verification platform built with **Python**, **Streamlit**, **OCR**, **MongoDB**, and **local LLMs (Ollama)**.

The system extracts mandatory tender requirements from procurement documents, verifies vendor submissions, and provides an interactive compliance dashboard with document evidence and PDF preview.

---
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

# ✨ Features

* 📄 Automatic Tender Document Extraction
* 🔍 OCR Support for Scanned PDFs
* 🤖 AI-assisted Document Requirement Detection
* 📑 Vendor Document Verification
* 📊 Interactive Vendor Compliance Dashboard (AgGrid)
* 📄 PDF Evidence Viewer with Auto Page Navigation
* 🗂 Technical Datasheet Extraction
* 💾 MongoDB Integration
* 📈 Compliance Score Calculation

---

# 🏗 Project Structure

```text
AI-Tender-Audit-System/
│
├── app.py
├── database/
├── modules/
│   ├── tender_extractor.py
│   ├── vendor_processor.py
│   ├── pdf_reader.py
│   ├── document_matcher.py
│   ├── document_aliases.py
│   └── ...
├── uploads/
├── requirements.txt
└── README.md
```

---

# 🛠 Technologies Used

* Python
* Streamlit
* MongoDB
* PyMuPDF (fitz)
* Tesseract OCR
* Pillow
* Pandas
* AgGrid
* Ollama (Gemma 3)

---

# 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/mantukushali-cmyk/AI-Tender-Audit-System.git
cd AI-Tender-Audit-System
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶ Run the Application

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

# 📊 Workflow

1. Upload Tender PDF
2. Extract Required Documents
3. Upload Vendor Documents
4. AI Verification
5. Compliance Matrix Generation
6. PDF Evidence Preview
7. Technical Datasheet Extraction

---

# 📷 Screenshots

## Dashboard

![Dashboard](images/dashboard.png)


---

## Upload Document

![Upload Document](images/upload.png)

---

## 📄 Required Documents Extraction

![Required Documents](images/required_documents.png)

---

## Compliance Matrix

![Compliance Dashboard](images/compliance_dashboard.png)

---

## PDF Evidence Viewer

![PDF Viewer](images/pdf_viewer.png)

---

## Technical Datasheet Extraction

![Technical Datasheet](images/technical_datasheet.png)

# 🚧 Future Enhancements

* AI Tender Requirement Comparison
* Bounding Box Evidence Highlighting
* Excel & PDF Report Export
* Vendor Analytics Dashboard
* Multi-Tender Management
* OCR Performance Optimization

---

# 👨‍💻 Author

**Mantu Kushali**

B.Tech  Computer Science & Engineering

Adamas University

GitHub: https://github.com/mantukushali-cmyk
