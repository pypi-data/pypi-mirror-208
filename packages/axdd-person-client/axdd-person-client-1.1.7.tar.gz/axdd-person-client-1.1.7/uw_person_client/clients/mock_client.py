# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


import json
import glob
import os
from uw_person_client.clients import AbstractUWPersonClient
from uw_person_client.components import Person
from uw_person_client.exceptions import PersonNotFoundException


class MockedUWPersonClient(AbstractUWPersonClient):
    paths = []

    @classmethod
    def register_mock_path(self, path):
        if path not in MockedUWPersonClient.paths:
            MockedUWPersonClient.paths.append(path)

    def get_registered_paths(self):
        return MockedUWPersonClient.paths

    def _get_mock_paths(self):
        default_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../fixtures/'))
        return self.get_registered_paths() + [default_path]

    def _read_person_file(self, search_value):
        """Return first matching mocked person record
        """
        for path in self._get_mock_paths():
            files = glob.glob(os.path.join(path, search_value), recursive=True)
            try:
                return self._load_person_from_file(files[0])
            except IndexError:
                pass

        raise PersonNotFoundException()

    def _read_person_files(self, search_value):
        """Return all matching mocked person records
        First matched uwnetid in record wins
        """
        persons = {}
        for path in self._get_mock_paths():
            for file_name in glob.glob(
                    os.path.join(path, search_value), recursive=True):
                person = self._load_person_from_file(file_name)
                if person.uwnetid not in persons:
                    persons[person.uwnetid] = person

        return list(persons.values())

    def _load_person_from_file(files, filename):
        return Person().from_dict(json.load(open(filename)))

    def _paginate(self, values, page=None, page_size=None):
        if page is not None and page_size is not None:
            offset = (page - 1) * page_size
            values = values[offset:offset+page_size]
        return values

    def get_person_by_uwnetid(self, uwnetid):
        return self._read_person_file(f'**/*{uwnetid}*.json')

    def get_person_by_uwregid(self, uwregid):
        return self._read_person_file(f'**/*{uwregid}*.json')

    def get_person_by_student_number(self, student_number):
        return self._read_person_file(f'**/*{student_number}*.json')

    def get_person_by_system_key(self, system_key, **kwargs):
        return self._read_person_file(f'**/*{system_key}*.json')

    def get_persons(self, page=None, page_size=None):
        return self._paginate(
            self._read_person_files('**/**.json'),
            page=page,
            page_size=page_size)

    def get_registered_students(self, page=None, page_size=None):
        persons = self._read_person_files('**/students/**.json')
        registered_persons = [person for person in persons if
                              person.student.enroll_status_code == '12']
        return self._paginate(
            registered_persons,
            page=page,
            page_size=page_size)

    def get_active_students(self, page=None, page_size=None):
        return self._paginate(
            self._read_person_files('**/students/**.json'),
            page=page,
            page_size=page_size)

    def get_active_employees(self, page=None, page_size=None):
        return self._paginate(
            self._read_person_files('**/employees/**/*.json'),
            page=page,
            page_size=page_size)

    def get_advisers(self, advising_program=None):
        advisers = self._read_person_files('**/employees/advisers/*.json')
        if advising_program:
            filtered_advisers = []
            for person in advisers:
                if (person.employee.adviser.advising_program ==
                        advising_program):
                    filtered_advisers.append(person)
            return filtered_advisers
        else:
            return advisers

    def get_persons_by_adviser_netid(self, uwnetid):
        students = self.get_active_students()
        persons = []
        for person in students:
            for adviser in person.student.advisers:
                if adviser.uwnetid == uwnetid:
                    persons.append(person)
                    break
        return persons

    def get_persons_by_adviser_regid(self, uwregid):
        students = self.get_active_students()
        persons = []
        for person in students:
            for adviser in person.student.advisers:
                if adviser.uwregid == uwregid:
                    persons.append(person)
                    break
        return persons
