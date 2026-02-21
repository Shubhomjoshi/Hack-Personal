"""
Database models (SQLAlchemy ORM models)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database import Base


class User(Base):
    """
    User model - Authentication and user management
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    documents = relationship("Document", back_populates="uploaded_by_user")


class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    BILL_OF_LADING = "Bill of Lading"
    PROOF_OF_DELIVERY = "Proof of Delivery"
    PACKING_LIST = "Packing List"
    COMMERCIAL_INVOICE = "Commercial Invoice"
    HAZMAT_DOCUMENT = "Hazmat Document"
    LUMPER_RECEIPT = "Lumper Receipt"
    TRIP_SHEET = "Trip Sheet"
    FREIGHT_INVOICE = "Freight Invoice"
    UNKNOWN = "Unknown"


class ReadabilityStatus(str, enum.Enum):
    """Document readability status"""
    CLEAR = "Clear"
    PARTIALLY_CLEAR = "Partially Clear"
    UNREADABLE = "Unreadable"


class ValidationStatus(str, enum.Enum):
    """Document validation status"""
    PASS = "Pass"
    FAIL = "Fail"
    NEEDS_REVIEW = "Needs Review"
    PENDING = "Pending"


class Document(Base):
    """
    Document model - Stores uploaded documents
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(50), nullable=True)  # PDF, JPEG, PNG

    # Classification
    document_type = Column(SQLEnum(DocumentType), default=DocumentType.UNKNOWN)
    classification_confidence = Column(Float, nullable=True)

    # Quality Assessment
    readability_status = Column(SQLEnum(ReadabilityStatus), nullable=True)
    quality_score = Column(Float, nullable=True)  # 0-100
    is_blurry = Column(Boolean, default=False)
    is_skewed = Column(Boolean, default=False)

    # Signature Detection
    signature_count = Column(Integer, default=0)
    has_signature = Column(Boolean, default=False)

    # Metadata
    order_number = Column(String(255), nullable=True)
    invoice_number = Column(String(255), nullable=True)
    document_date = Column(String(100), nullable=True)
    extracted_metadata = Column(JSON, nullable=True)  # Stores client_name and other metadata

    # Validation
    validation_status = Column(SQLEnum(ValidationStatus), default=ValidationStatus.PENDING)
    validation_result = Column(JSON, nullable=True)  # Stores validation details

    # Processing
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)
    ocr_text = Column(Text, nullable=True)

    # User relation
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    customer_id = Column(Integer, nullable=True)  # For customer-specific rules
    client_name = Column(String(255), nullable=True)  # New column for client name

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    uploaded_by_user = relationship("User", back_populates="documents")
    validation_rules_applied = relationship("DocumentValidation", back_populates="document")


class ValidationRule(Base):
    """
    Validation Rule model - Customer-specific validation rules
    """
    __tablename__ = "validation_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(255), nullable=False)
    rule_description = Column(Text, nullable=True)
    document_type = Column(SQLEnum(DocumentType), nullable=False)

    # Rule conditions
    requires_signature = Column(Boolean, default=False)
    minimum_signatures = Column(Integer, default=0)
    requires_order_number = Column(Boolean, default=False)

    # Custom rule JSON for complex validations
    custom_rule = Column(JSON, nullable=True)

    # Customer association
    customer_id = Column(Integer, nullable=True)  # NULL = global rule
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DocumentValidation(Base):
    """
    Document Validation Result - Stores validation results
    """
    __tablename__ = "document_validations"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    validation_rule_id = Column(Integer, ForeignKey("validation_rules.id"), nullable=False)

    passed = Column(Boolean, nullable=False)
    failure_reason = Column(Text, nullable=True)
    validation_details = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="validation_rules_applied")
    rule = relationship("ValidationRule")


class ProcessingLog(Base):
    """
    Processing Log - Tracks document processing steps
    """
    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    step_name = Column(String(255), nullable=False)  # OCR, Classification, Quality, etc.
    status = Column(String(50), nullable=False)  # SUCCESS, FAILED, SKIPPED
    execution_time = Column(Float, nullable=True)  # in seconds
    details = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DocTypeSample(Base):
    """
    Document Type Sample - Stores sample documents for similarity matching
    Admin uploads 3-5 samples per document type for training
    """
    __tablename__ = "doc_type_samples"

    id = Column(Integer, primary_key=True, index=True)
    doc_type = Column(SQLEnum(DocumentType), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    extracted_text = Column(Text, nullable=True)
    embedding = Column(JSON, nullable=True)  # Stores text embedding as JSON array

    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True, index=True)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    uploaded_by_user = relationship("User")


class ClassificationResult(Base):
    """
    Classification Result - Tracks classification history and corrections
    Used for feedback loop and accuracy tracking
    """
    __tablename__ = "classification_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)

    # Prediction results
    predicted_type = Column(SQLEnum(DocumentType), nullable=True)
    confidence = Column(Float, nullable=True)
    method = Column(String(100), nullable=True)  # keyword/embedding/gemini/multi_signal_vote

    # Sample matching details (if embedding was used)
    matched_sample_id = Column(Integer, ForeignKey("doc_type_samples.id"), nullable=True)
    similarity_score = Column(Float, nullable=True)

    # Feedback and correction
    is_correct = Column(Boolean, default=None, nullable=True)  # NULL = not reviewed
    corrected_type = Column(SQLEnum(DocumentType), nullable=True)
    corrected_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    corrected_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document")
    matched_sample = relationship("DocTypeSample")
    corrected_by_user = relationship("User")


