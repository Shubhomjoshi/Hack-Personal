"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import re


# ============= Enums =============

class DocumentTypeEnum(str, Enum):
    BILL_OF_LADING = "Bill of Lading"
    PROOF_OF_DELIVERY = "Proof of Delivery"
    PACKING_LIST = "Packing List"
    COMMERCIAL_INVOICE = "Commercial Invoice"
    HAZMAT_DOCUMENT = "Hazmat Document"
    LUMPER_RECEIPT = "Lumper Receipt"
    TRIP_SHEET = "Trip Sheet"
    FREIGHT_INVOICE = "Freight Invoice"
    UNKNOWN = "Unknown"


class ReadabilityStatusEnum(str, Enum):
    CLEAR = "Clear"
    PARTIALLY_CLEAR = "Partially Clear"
    UNREADABLE = "Unreadable"


class ValidationStatusEnum(str, Enum):
    PASS = "Pass"
    FAIL = "Fail"
    NEEDS_REVIEW = "Needs Review"
    PENDING = "Pending"


# ============= Authentication Schemas =============

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str


class UserRegister(UserBase):
    """Schema for user registration"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Password must be at least 8 characters and contain uppercase, lowercase, number, and special character"
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password strength:
        - At least 8 characters
        - Maximum 72 characters (bcrypt limitation)
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one digit
        - Contains at least one special character
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if len(v) > 72:
            raise ValueError('Password must not exceed 72 characters')

        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', v):
            raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>_-+=[]\\\/~`)')

        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class Token(BaseModel):
    """JWT Token response with user details"""
    access_token: str
    token_type: str = "bearer"
    # User details
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
    user_id: Optional[int] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============= Document Schemas =============

class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    document_id: int
    filename: str
    file_size: int
    message: str
    web_status: Optional[str] = "Sent to Imaging"
    mob_status: Optional[str] = "Uploaded Successfully - Verification Pending"
    processing_started: bool = True


class DocumentClassification(BaseModel):
    """Document classification result"""
    document_type: DocumentTypeEnum
    confidence: float = Field(..., ge=0.0, le=1.0)


class QualityAssessment(BaseModel):
    """Document quality assessment result"""
    readability_status: ReadabilityStatusEnum
    quality_score: float = Field(..., ge=0.0, le=100.0)
    is_blurry: bool
    is_skewed: bool
    recommendation: str  # "Accept" or "Re-upload"


class SignatureDetection(BaseModel):
    """Signature detection result"""
    signature_count: int
    has_signature: bool
    confidence: Optional[float] = None


class MetadataExtraction(BaseModel):
    """Extracted metadata from document"""
    order_number: Optional[str] = None
    invoice_number: Optional[str] = None
    document_date: Optional[str] = None
    client_name: Optional[str] = None  # Stored in extracted_metadata JSON
    other_fields: Optional[Dict[str, Any]] = None


class DocumentValidationResult(BaseModel):
    """Document validation result"""
    validation_status: ValidationStatusEnum
    passed_rules: List[str] = []
    failed_rules: List[str] = []
    failure_reasons: List[str] = []


class DocumentProcessingResult(BaseModel):
    """Complete document processing result"""
    document_id: int
    filename: str
    classification: DocumentClassification
    quality_assessment: QualityAssessment
    signature_detection: SignatureDetection
    metadata: MetadataExtraction
    validation: DocumentValidationResult
    processing_time: float

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: int
    filename: str
    original_filename: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None

    # Classification
    document_type: DocumentTypeEnum
    classification_confidence: Optional[float] = None

    # Quality
    readability_status: Optional[ReadabilityStatusEnum] = None
    quality_score: Optional[float] = None
    is_blurry: bool = False
    is_skewed: bool = False

    # Signature
    signature_count: int = 0
    has_signature: bool = False

    # Metadata
    order_number: Optional[str] = None
    invoice_number: Optional[str] = None
    document_date: Optional[str] = None
    client_name: Optional[str] = None  # Client/company name extracted from document
    extracted_metadata: Optional[Dict[str, Any]] = None  # Contains additional metadata

    # Validation
    validation_status: ValidationStatusEnum

    # Processing
    is_processed: bool
    processing_error: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """Response for document list"""
    total: int
    documents: List[DocumentResponse]


# ============= Validation Rule Schemas =============

class ValidationRuleBase(BaseModel):
    """Base validation rule schema"""
    rule_name: str
    rule_description: Optional[str] = None
    document_type: DocumentTypeEnum
    requires_signature: bool = False
    minimum_signatures: int = 0
    requires_order_number: bool = False
    customer_id: Optional[int] = None


class ValidationRuleCreate(ValidationRuleBase):
    """Schema for creating validation rule"""
    custom_rule: Optional[Dict[str, Any]] = None


class ValidationRuleUpdate(BaseModel):
    """Schema for updating validation rule"""
    rule_name: Optional[str] = None
    rule_description: Optional[str] = None
    requires_signature: Optional[bool] = None
    minimum_signatures: Optional[int] = None
    requires_order_number: Optional[bool] = None
    is_active: Optional[bool] = None
    custom_rule: Optional[Dict[str, Any]] = None


class ValidationRuleResponse(ValidationRuleBase):
    """Schema for validation rule response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============= Processing Log Schemas =============

class ProcessingStepLog(BaseModel):
    """Processing step log"""
    step_name: str
    status: str
    execution_time: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


# ============= Analytics Schemas =============

class DocumentStatistics(BaseModel):
    """Document processing statistics"""
    total_documents: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    average_quality_score: float
    total_with_signatures: int
    validation_pass_rate: float


# ============= Generic Response Schemas =============

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
    field: Optional[str] = None

