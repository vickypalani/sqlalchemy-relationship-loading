"""Relationship techniques in SQLAlchemy."""

import asyncio
import os
from typing import List

from dotenv import load_dotenv
from sqlalchemy import ForeignKey, select, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    selectinload,
    joinedload,
    raiseload,
)

load_dotenv()

DB_ENGINE = os.getenv("DB_ASYNC")


engine: AsyncEngine = create_async_engine(DB_ENGINE, echo=True)

async_session: AsyncSession = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all the ORM models."""


class PirateCrew(Base):
    """Contains the details of a pirate crew"""

    __tablename__ = "pirate_crew"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    ship_name: Mapped[str]
    members: Mapped[List["Pirate"]] = relationship(
        back_populates="pirate_crew", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return the representation of the object."""
        return f"{self.__class__.name}({self.name})"


class Pirate(Base):
    """Contains the details of a pirate."""

    __tablename__ = "pirates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    role: Mapped[str]
    devil_fruit_user: Mapped[bool]
    pirate_crew_id = mapped_column(ForeignKey("pirate_crew.id"))
    pirate_crew: Mapped["PirateCrew"] = relationship(back_populates="members")

    def __repr__(self) -> str:
        """Return the representation of the object."""
        return f"{self.__class__.name}({self.name})"


async def create_tables():
    """Method to create all the tables."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def db_seeder():
    """Seeder to seed the PirateCrew and Pirate tables."""
    async with async_session() as session:
        mugiwara = PirateCrew(name="Straw Hats", ship_name="Thousand Sunny")
        mugiwara_members = [
            Pirate(
                name="Monkey D Luffy",
                role="Captain",
                devil_fruit_user=True,
                pirate_crew=mugiwara,
            ),
            Pirate(
                name="Roronoa zoro",
                role="First Mate",
                devil_fruit_user=False,
                pirate_crew=mugiwara,
            ),
            Pirate(
                name="Nami",
                role="Navigator",
                devil_fruit_user=False,
                pirate_crew=mugiwara,
            ),
        ]
        session.add(mugiwara)
        session.add_all(mugiwara_members)
        await session.commit()

        # Let's ensure that the data has been seeded successfuly, by quering the PirateCrew
        pirate_crew = (await session.execute(select(PirateCrew))).all()
        pirates = (await session.execute(select(Pirate))).all()
        print(pirate_crew)
        print(pirates)


async def async_main():
    """Async main method."""
    # async with async_session() as session:
    #     await session.execute(text("SELECT 'HELLO WORLD'"))
    create_tables_task = asyncio.create_task(create_tables())
    await create_tables_task
    db_seeder_task = asyncio.create_task(db_seeder())
    await db_seeder_task


# async def run_queries():
#     """Execute the queries."""
#     async with async_session() as session:
#         pirate_crew = (await session.execute(select(PirateCrew))).all()[0][0]
#         print(pirate_crew)

#         # Now lets try to access the members of the pirate crew (members is a related object)
#         members = pirate_crew.members
#         print(members)


# async def run_queries():
#     """Execute the queries."""
#     async with async_session() as session:
#         pirate_crew = (
#             await session.execute(
#                 select(PirateCrew).options(selectinload(PirateCrew.members))
#             )
#         ).all()[0][0]
#         print(pirate_crew)


# async def run_queries():
#     """Execute the queries."""
#     async with async_session() as session:
#         pirate_crew = (
#             await session.execute(
#                 select(PirateCrew).options(joinedload(PirateCrew.members))
#             )
#         ).unique().all()[0][0]
#         print(pirate_crew)


async def run_queries():
    """Execute the queries."""
    async with async_session() as session:
        pirate_crew = (await session.execute(select(PirateCrew))).all()[0][0]
        members = pirate_crew.members
        print(pirate_crew)


if __name__ == "__main__":
    # asyncio.run(async_main())
    asyncio.run(run_queries())
