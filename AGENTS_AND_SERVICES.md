# AI Agents and Services in Document Intelligence System

## 📊 System Overview

This project uses a **hybrid architecture** combining:
- **1 AI Agent** (intelligent decision maker)
- **20+ Services** (specialized workers)
- **Orchestration** via Background Processor

---

## 🤖 AI AGENTS (1)

### 1. **DocumentProcessingAgent** 
**File:** `services/document_processing_agent.py`

**Role:** Intelligent decision-making agent that orchestrates the entire document processing pipeline

**Uses:** Google Gemini AI (gemini-3-flash-preview model)

**Capabilities:**
- ✅ Decides which OCR strategy to use (EasyOCR, Gemini OCR, or both)
- ✅ Determines quality assessment strategy
- ✅ Optimizes processing flow based on document characteristics
- ✅ Makes smart decisions about error handling and recovery
- ✅ Learns from processing history (agent memory)

**Decision Types:**
```
- Fast Track OCR: Digital PDFs with clear text → Skip EasyOCR
- Enhanced OCR: Scanned/poor quality → Use both EasyOCR + Gemini
- Quality First: Unknown quality → Assess quality before OCR
```

**Key Methods:**
- `decide_processing_strategy()` - Analyzes file and decides approach
- `analyze_document_quality()` - Smart quality assessment
- `suggest_ocr_strategy()` - Recommends best OCR method

---

## 🔧 CORE SERVICES (20)

### OCR & Text Extraction Services (3)

#### 1. **EasyOCRService**
**File:** `services/easyocr_service.py`

**Purpose:** Primary OCR engine for text extraction from images/PDFs

**Technology:** EasyOCR library

**Features:**
- Extracts text from images and PDFs
- Handles multiple languages
- Works with scanned documents
- Preprocessing pipeline (grayscale, CLAHE, denoise)

---

#### 2. **GeminiDocumentAnalyzer** (AI Service)
**File:** `services/gemini_service.py`

**Purpose:** Advanced AI-powered document analysis and OCR

**Technology:** Google Gemini Vision AI (gemini-3-flash-preview)

**Features:**
- ✅ **Signature Detection** - Detects handwritten signatures, counts them, identifies locations
- ✅ **Enhanced OCR** - Extracts text using vision AI
- ✅ **Document Understanding** - Analyzes document structure and content
- ✅ **Text Merging** - Combines EasyOCR + Gemini text for best results

**Key Methods:**
- `analyze_document()` - Full document analysis (signatures + OCR)
- `merge_ocr_texts()` - Intelligent text combination

---

#### 3. **OCRService**
**File:** `services/ocr_service.py`

**Purpose:** Legacy OCR service wrapper (mostly replaced by EasyOCR)

**Technology:** PaddleOCR

**Status:** Partially deprecated, kept for fallback

---

### Quality Assessment Services (2)

#### 4. **QualityAssessmentService**
**File:** `services/quality_service.py`

**Purpose:** Computer vision-based quality assessment

**Technology:** OpenCV

**Features:**
- ✅ Blur detection (Laplacian variance)
- ✅ Skew detection (angle detection)
- ✅ Brightness assessment
- ✅ Contrast evaluation
- ✅ Overall quality scoring

**Output:** Quality score (0-100), readability status, recommendations

---

#### 5. **ImagePreprocessor**
**File:** `services/image_preprocessor.py`

**Purpose:** Image enhancement before OCR

**Technology:** OpenCV

**Features:**
- Deskewing (rotation correction)
- Denoising
- Contrast enhancement (CLAHE)
- Adaptive thresholding
- Binarization

---

### Document Classification Services (4)

#### 6. **DocumentClassificationService**
**File:** `services/classification_service.py`

**Purpose:** Main classification orchestrator

**Features:**
- Coordinates all classification methods
- Manages fallback strategies
- Returns classification result with confidence

---

#### 7. **SampleBasedClassifier**
**File:** `services/sample_based_classifier.py`

**Purpose:** Embedding-based similarity matching

**Technology:** Sentence embeddings + cosine similarity

**Features:**
- ✅ Compares new docs against stored sample documents
- ✅ Uses text embeddings for semantic similarity
- ✅ Weighted voting across multiple samples
- ✅ High accuracy for well-trained document types

**Methods:**
- Keyword matching (fast, rule-based)
- Embedding similarity (ML-based)
- Gemini Vision fallback (AI-based)

---

#### 8. **EmbeddingService**
**File:** `services/embedding_service.py`

**Purpose:** Generate text embeddings for similarity matching

**Technology:** Sentence-transformers

**Features:**
- Converts text to vector embeddings
- Supports cosine similarity calculation

---

#### 9. **SampleStore**
**File:** `services/sample_store.py`

**Purpose:** Manages sample documents database

**Features:**
- CRUD operations for sample documents
- Stores embeddings
- Retrieves samples by document type

---

### Signature Detection (1)

#### 10. **SignatureDetectionService**
**File:** `services/signature_service.py`

**Purpose:** Wrapper/helper for signature detection

**Technology:** Calls Gemini AI

**Features:**
- Detects signatures via Gemini
- Parses signature metadata
- Validates signature counts

---

### Metadata Extraction Services (2)

#### 11. **MetadataExtractionService**
**File:** `services/metadata_service.py`

**Purpose:** Extract document-specific fields

**Features:**
- Field extraction based on document type
- Regex-based pattern matching
- Structured data parsing

---

#### 12. **EnhancedMetadataExtractor**
**File:** `services/enhanced_metadata_extractor.py`

**Purpose:** Advanced metadata extraction with AI

**Features:**
- Extracts specific fields per document type (8 types)
- Calculates extraction scores
- Returns structured metadata

**Document Types Supported:**
1. Bill of Lading (BOL)
2. Proof of Delivery (POD)
3. Commercial Invoice
4. Packing List
5. Hazmat Document
6. Lumper Receipt
7. Trip Sheet
8. Freight Invoice

---

### Validation Services (2)

#### 13. **RuleValidationEngine**
**File:** `services/rule_validation_engine.py`

**Purpose:** Rule-based document validation

**Features:**
- ✅ General rules (apply to all docs)
- ✅ Document-specific rules
- ✅ Hard failures (blocking)
- ✅ Soft warnings (non-blocking)

**Example Rules:**
- Quality checks (blur, text extraction)
- Signature requirements
- Required field presence
- Data format validation

---

#### 14. **ValidationService**
**File:** `services/validation_service.py`

**Purpose:** Validation orchestrator

**Features:**
- Coordinates rule validation
- Returns structured validation results

---

### Similarity & Display Services (3)

#### 15. **SimilarityMatcher**
**File:** `services/similarity_matcher.py`

**Purpose:** Compares document embeddings

**Features:**
- Cosine similarity calculation
- Aggregates scores across samples
- Weighted scoring

---

#### 16. **DisplayConfig**
**File:** `services/display_config.py`

**Purpose:** Frontend display configuration

**Features:**
- Defines what fields to show per document type
- Provides field labels, icons, order
- Supports dynamic UI rendering

---

#### 17. **DocumentClassifier**
**File:** `services/document_classifier.py`

**Purpose:** Document type classification helper

**Features:**
- Keyword-based classification
- Pattern matching for document types

---

### Background & Storage Services (3)

#### 18. **BackgroundProcessor**
**File:** `services/background_processor.py`

**Purpose:** Main background processing orchestrator

**Features:**
- ✅ Coordinates all processing steps
- ✅ Runs services in sequence
- ✅ **Concurrent processing** for:
  - Document classification
  - Signature detection (for BOL only)
  - Metadata extraction
- ✅ Database updates
- ✅ Error handling and logging

**Processing Flow:**
```
1. Quality Assessment → Stop if < 55%
2. OCR Text Extraction (EasyOCR + Gemini)
3. Concurrent: Classification + Signatures + Metadata
4. Rule Validation
5. Database Update
```

---

#### 19. **ProcessingService**
**File:** `services/processing_service.py`

**Purpose:** Document processing helper

**Features:**
- Orchestrates individual processing steps
- Manages processing logs

---

#### 20. **AzureStorageService**
**File:** `services/azure_storage.py`

**Purpose:** Azure Blob Storage integration

**Features:**
- Upload files to Azure
- Download files from Azure
- Manage blob storage

---

## 🎯 SERVICE INTERACTION MAP

```
┌─────────────────────────────────────────────────────────┐
│                   User Uploads Document                  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              BackgroundProcessor                         │
│            (Main Orchestrator)                           │
└──────────────────────┬──────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
┌──────────────────┐    ┌──────────────────────┐
│ DocumentProcessing│    │ QualityAssessment   │
│ Agent (AI)       │    │ Service              │
│ - Decides strategy│    │ - Checks blur/skew  │
└────────┬──────────┘    └──────────┬───────────┘
         │                          │
         │ Decisions                │ Quality < 55%? → STOP
         │                          │
         ▼                          ▼
┌─────────────────────────────────────────────────────────┐
│              OCR Text Extraction                         │
│  EasyOCRService + GeminiDocumentAnalyzer                │
│  → Merged text result                                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│         CONCURRENT PROCESSING (ThreadPool)               │
│  ┌───────────────┬──────────────────┬─────────────────┐│
│  │Classification │ Signature        │ Metadata        ││
│  │Service        │ Detection        │ Extraction      ││
│  │- Keyword      │ (BOL only)       │ Service         ││
│  │- Embedding    │- Gemini AI       │- Field extract  ││
│  │- Gemini       │                  │                 ││
│  └───────────────┴──────────────────┴─────────────────┘│
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│           RuleValidationEngine                           │
│  - General rules (quality, text, classification)        │
│  - Doc-specific rules (signatures, required fields)     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Database Update                             │
│  - Document metadata                                     │
│  - Validation results                                    │
│  - Processing logs                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🧠 AI vs Traditional Services

### AI-Powered Services (3)
1. **DocumentProcessingAgent** - AI decision making
2. **GeminiDocumentAnalyzer** - Vision AI for OCR + signatures
3. **EmbeddingService** - ML-based semantic similarity

### Traditional Services (17)
- OCR engines (EasyOCR, PaddleOCR)
- Computer vision (OpenCV for quality)
- Rule-based validation
- Database operations
- Storage management

---

## 🚀 Key Service Functions

### Get Service Instances (Singletons)
```python
from services.gemini_service import get_gemini_analyzer
from services.document_processing_agent import get_processing_agent
from services.sample_based_classifier import get_sample_based_classifier
from services.rule_validation_engine import get_validation_engine
from services.enhanced_metadata_extractor import get_enhanced_metadata_extractor

# Usage
gemini = get_gemini_analyzer()
agent = get_processing_agent()
classifier = get_sample_based_classifier()
validator = get_validation_engine()
extractor = get_enhanced_metadata_extractor()
```

---

## 📦 External Dependencies

### AI/ML Libraries:
- `google-genai` - Gemini AI API
- `easyocr` - OCR engine
- `paddleocr` - Alternative OCR (legacy)
- `sentence-transformers` - Text embeddings

### Computer Vision:
- `opencv-python` (cv2) - Image processing
- `Pillow` (PIL) - Image handling
- `numpy` - Array operations

### Backend:
- `FastAPI` - Web framework
- `SQLAlchemy` - Database ORM
- `python-dotenv` - Environment variables
- `PyMuPDF` (fitz) - PDF handling

---

## 🎯 Summary

**Total Components:**
- **1 AI Agent** (DocumentProcessingAgent)
- **20 Services** (mix of AI-powered and traditional)
- **1 Main Orchestrator** (BackgroundProcessor)

**AI Technologies Used:**
- Google Gemini Vision AI (gemini-3-flash-preview)
- EasyOCR
- Sentence Embeddings
- Machine Learning (similarity matching)

**Processing Approach:**
- **Sequential** for OCR and quality
- **Concurrent** for classification, signatures, metadata
- **Rule-based** for validation
- **AI-driven** for decision making

---

**Last Updated:** February 22, 2026  
**Architecture:** Hybrid AI + Traditional Services

