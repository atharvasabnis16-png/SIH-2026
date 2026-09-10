from sqlalchemy import (
    Column, Integer, String, Boolean, Text,
    ForeignKey, DateTime, func
)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role            = Column(String, nullable=False, default="user")

    # Relationships (back-references from child tables)
    consents   = relationship("Consent",  back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Consent(Base):
    __tablename__ = "consents"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_type    = Column(String, nullable=False)
    allowed      = Column(Boolean, nullable=False, default=False)
    last_updated = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),          # auto-updates on every row change
        nullable=False,
    )

    user = relationship("User", back_populates="consents")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    action    = Column(Text, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),    # auto-set to now on insert
        nullable=False,
    )

    user = relationship("User", back_populates="audit_logs")
