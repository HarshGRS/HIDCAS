from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func

# =========================
# 1️⃣ Roles Table
# =========================
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="role")
    role_permissions = relationship("RolePermission", back_populates="role")


# =========================
# 2️⃣ Permissions Table
# =========================
class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    role_permissions = relationship("RolePermission", back_populates="permission")


# =========================
# 3️⃣ Role-Permission Mapping
# =========================
class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    permission_id = Column(Integer, ForeignKey("permissions.id"))

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")


# =========================
# 4️⃣ Users Table 
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"))

    role = relationship("Role", back_populates="users")
    documents = relationship("Document", back_populates="owner")

    def has_permission(self, permission_name: str) -> bool:
        if not self.role or not self.role.role_permissions:
            return False
        for role_permission in self.role.role_permissions:
            if role_permission.permission and role_permission.permission.name == permission_name:
                return True
        return False
    conversations = relationship("Conversation", back_populates="user")


# =========================
# 5️⃣ Documents Table 
# =========================
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)       # in bytes
    file_type = Column(String)        # pdf, jpg, png, doc

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="documents")
    projects = relationship("Project", back_populates="document")
    content = Column(Text, nullable=True)
    conversations = relationship("Conversation", back_populates="document")

# =========================
# 6️⃣ Projects Table 
# =========================
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(Integer, ForeignKey("documents.id"))

    company_name = Column(String)
    project_name = Column(String)
    location = Column(String)
    year = Column(String)
    budget = Column(String)
    loan_amount = Column(String)

    document = relationship("Document", back_populates="projects")


# =========================
# 7️⃣ Conversations Table
# =========================
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="conversations")
    document = relationship("Document", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


# =========================
# 8️⃣ Messages Table
# =========================
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String, nullable=False)  # "user" ya "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")