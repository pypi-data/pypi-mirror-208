# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from uw_person_client.databases.postgres import Postgres
from sqlalchemy import Table, Column, ForeignKey, TEXT, Integer
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship


class UWPDS(Postgres):

    Base = automap_base()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # only map the database once
        if len(UWPDS.Base.classes) == 0:
            self.initialize_relationships()
        # person classes
        self.Person = UWPDS.Base.classes.person
        # employee classes
        self.Employee = UWPDS.Base.classes.employee
        self.Adviser = UWPDS.Base.classes.adviser
        # student classes
        self.Student = UWPDS.Base.classes.student
        self.Major = UWPDS.Base.classes.major
        self.Sport = UWPDS.Base.classes.sport
        self.StudentToSport = UWPDS.Base.classes.student_to_sport
        self.StudentToAdviser = UWPDS.Base.classes.student_to_adviser
        self.Transcript = UWPDS.Base.classes.transcript
        self.Transfer = UWPDS.Base.classes.transfer
        self.Hold = UWPDS.Base.classes.student_hold
        self.Degree = UWPDS.Base.classes.degree
        self.Term = UWPDS.Base.classes.term

    def initialize_relationships(self):
        student_to_sport = Table(
            'student_to_sport',
            UWPDS.Base.metadata,
            autoload=True,
            autoload_with=self.engine
        )

        student_to_adviser = Table(
            'student_to_adviser',
            UWPDS.Base.metadata,
            autoload=True,
            autoload_with=self.engine
        )

        class Student(UWPDS.Base):
            __tablename__ = "student"
            __table_args__ = {'extend_existing': True}
            sport = relationship("sport",
                                 secondary=student_to_sport,
                                 viewonly=True)
            adviser = relationship("adviser",
                                   secondary=student_to_adviser,
                                   viewonly=True)
            # majors
            major_1_id = Column('major_1_id',
                                ForeignKey('major.id', ondelete="CASCADE"))
            major_1 = relationship("major", foreign_keys=[major_1_id],
                                   viewonly=True)
            major_2_id = Column('major_2_id',
                                ForeignKey('major.id', ondelete="CASCADE"))
            major_2 = relationship("major", foreign_keys=[major_2_id],
                                   viewonly=True)
            major_3_id = Column('major_3_id',
                                ForeignKey('major.id', ondelete="CASCADE"))
            major_3 = relationship("major", foreign_keys=[major_3_id],
                                   viewonly=True)
            # pending majors
            pending_major_1_id = Column(
                'pending_major_1_id',
                ForeignKey('major.id', ondelete="CASCADE"))
            pending_major_1 = \
                relationship("major", foreign_keys=[pending_major_1_id],
                             viewonly=True)
            pending_major_2_id = Column(
                'pending_major_2_id',
                ForeignKey('major.id', ondelete="CASCADE"))
            pending_major_2 = \
                relationship("major", foreign_keys=[pending_major_2_id],
                             viewonly=True)
            pending_major_3_id = Column(
                'pending_major_3_id',
                ForeignKey('major.id', ondelete="CASCADE"))
            pending_major_3 = \
                relationship("major", foreign_keys=[pending_major_3_id],
                             viewonly=True)
            transcript = relationship(
                "Transcript", back_populates="student", uselist=True,
                viewonly=True)
            transfer = relationship(
                "transfer", back_populates="student", uselist=True,
                viewonly=True)
            degree = relationship(
                "degree", back_populates="student", uselist=True,
                viewonly=True)
            student_hold = relationship(
                "student_hold", back_populates="student", uselist=True,
                order_by="student_hold.seq", viewonly=True)
            academic_term_id = Column(
                'academic_term_id', ForeignKey('term.id', ondelete="CASCADE"))
            academic_term = \
                relationship("term", foreign_keys=[academic_term_id],
                             viewonly=True)

        class Employee(UWPDS.Base):
            __tablename__ = "employee"
            __table_args__ = {'extend_existing': True}
            adviser = relationship(
                "adviser", back_populates="employee", uselist=False,
                viewonly=True)

        class Transcript(UWPDS.Base):
            __tablename__ = "transcript"
            __table_args__ = {'extend_existing': True}
            tran_term_id = Column('tran_term_id',
                                  ForeignKey('term.id', ondelete="CASCADE"))
            tran_term = relationship("term",
                                     foreign_keys=[tran_term_id],
                                     viewonly=True)
            leave_ends_term_id = Column('leave_ends_term_id',
                                        ForeignKey('term.id',
                                                   ondelete="CASCADE"))
            leave_ends_term = relationship("term",
                                           foreign_keys=[leave_ends_term_id],
                                           viewonly=True)

        UWPDS.Base.prepare(self.engine, reflect=True)
        UWPDS.Base.classes.student = Student
        UWPDS.Base.classes.employee = Employee
        UWPDS.Base.classes.transcript = Transcript
        UWPDS.Base.classes.student_to_sport = student_to_sport
        UWPDS.Base.classes.student_to_adviser = student_to_adviser
