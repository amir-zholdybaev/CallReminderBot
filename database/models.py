from sqlalchemy import create_engine, Column, Integer, String, Date, Text, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# from create_bot import POSTGRES_USER_PASSWORD

# engine = create_engine(f'postgresql://unit:{POSTGRES_USER_PASSWORD}@localhost:5433/app_db')
engine = create_engine('sqlite:///app.db')

Base = declarative_base()


class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    region = Column(String(250), nullable=False)
    passport_photo = Column(String(250))
    departure_date = Column(Date)
    notes = Column(Text)
    call_date = Column(Date, nullable=False)
    is_departed = Column(Boolean, default=False)
    was_dialed = Column(Boolean, default=False)
    past_trip_dates = relationship("PastTripDate", back_populates="person")
    phone_numbers = relationship("PhoneNumber", back_populates="person")
    __table_args__ = (
        Index('idx_id_persons', 'id'),
        Index('idx_call_date_was_dialed', 'call_date', 'was_dialed'),
        Index('idx_departure_date_is_departed', 'departure_date', 'is_departed')
    )


class PastTripDate(Base):
    __tablename__ = 'past_trip_dates'
    id = Column(Integer, primary_key=True)
    trip_date = Column(Date, nullable=False)
    person_id = Column(Integer, ForeignKey('persons.id', ondelete='CASCADE'), nullable=False)
    person = relationship("Person", back_populates="past_trip_dates", cascade="all, delete")
    __table_args__ = (
        Index('idx_person_id_past_trip_dates', 'person_id'),
    )


class PhoneNumber(Base):
    __tablename__ = 'phone_numbers'
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(250), nullable=False)
    person_id = Column(Integer, ForeignKey('persons.id', ondelete='CASCADE'), nullable=False)
    person = relationship("Person", back_populates="phone_numbers", cascade="all, delete")
    __table_args__ = (
        Index('idx_person_id_phone_numbers', 'person_id'),
    )


def main():
    pass


if __name__ == '__main__':
    main()
