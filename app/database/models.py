from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey


class Base(DeclarativeBase):
    pass


class UserBase(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    is_private = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False, nullable=False)

    thoughts = relationship(
        'ThoughtBase', 
        back_populates='author'
    )
    email_tokens = relationship(
        "EmailTokenBase",
        back_populates="user"
    )


class ThoughtBase(Base):
    __tablename__ = 'thoughts'

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_public = Column(Boolean)

    author = relationship('UserBase', back_populates='thoughts')


class RefreshTokenBase(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)


class EmailTokenBase(Base):
    __tablename__ = 'email_tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, nullable=False, index=True)
    purpose = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False)
    user = relationship(
        "UserBase",
        back_populates="email_tokens"
    )
