import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)


class Base(DeclarativeBase):
    metadata = meta


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str]
    last_name: Mapped[str]
    is_deleted: Mapped[bool]


class Review(Base):
    __tablename__ = "review"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    content: Mapped[str]
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("book.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))


class Author(Base):
    __tablename__ = "author"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship()


class BookAuthor(Base):
    __tablename__ = "book__author"

    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("book.id"), primary_key=True)
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("author.id"),
        primary_key=True,
    )


class Book(Base):
    __tablename__ = "book"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    authors: Mapped[list[Author]] = relationship(secondary=BookAuthor.__table__)
    reviews: Mapped[list[Review]] = relationship()
    created_at: Mapped[datetime]


class Contract(Base):
    __tablename__ = "contract"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime]


class Job(Base):
    __tablename__ = "job"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    is_urgent: Mapped[bool]


class ContractJob(Base):
    __tablename__ = "contract_job"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job.id"),
        primary_key=True,
    )
    contract_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contract.id"),
        primary_key=True,
    )
