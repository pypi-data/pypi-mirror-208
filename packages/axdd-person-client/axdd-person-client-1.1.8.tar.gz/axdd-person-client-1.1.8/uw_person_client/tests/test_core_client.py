# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from unittest import TestCase
from unittest.mock import patch, MagicMock
from uw_person_client.exceptions import (
    AdviserNotFoundException, PersonNotFoundException)
from uw_person_client.clients.core_client import UWPersonClient
from uw_person_client.components import (
    Adviser, Employee, Major, Person, Sport, Student, Term, Transcript,
    Transfer, Hold, Degree)
from sqlalchemy.orm.exc import NoResultFound


class UWPersonClientTest(TestCase):

    @patch('uw_person_client.clients.core_client.UWPDS')
    def get_mock_person_client(self, mock_uwpds):
        client = UWPersonClient()
        client.DB = mock_uwpds.return_value
        return client

    @patch('uw_person_client.clients.core_client.UWPersonClient._map_person')
    @patch('uw_person_client.clients.core_client.or_')
    def test_get_person_by_uwnetid(self, mock_or, mock_map_person):
        client = self.get_mock_person_client()
        # person exists
        mock_person = MagicMock()
        mock_netid = 'test'
        client.DB.session.query.return_value.filter.return_value.first = \
            MagicMock(return_value=mock_person)

        return_value = client.get_person_by_uwnetid(mock_netid, arg1='arg1')
        # assertions
        client.DB.session.query.assert_called_once_with(client.DB.Person)
        client.DB.session.query.return_value.filter.return_value.one_or_none.\
            assert_called_once()
        self.assertEqual(
            return_value, mock_map_person(mock_person, arg1='arg1'))

        # no person found
        client.DB.session.query.return_value.filter.return_value.one_or_none =\
            MagicMock(return_value=None)
        with self.assertRaises(PersonNotFoundException):
            client.get_person_by_uwnetid(mock_netid)

    @patch('uw_person_client.clients.core_client.UWPersonClient._map_person')
    @patch('uw_person_client.clients.core_client.or_')
    def test_get_person_by_uwregid(self, mock_or, mock_map_person):
        client = self.get_mock_person_client()
        # person exists
        mock_person = MagicMock()
        mock_regid = 'test'
        client.DB.session.query.return_value.filter.return_value.first = \
            MagicMock(return_value=mock_person)

        return_value = client.get_person_by_uwregid(mock_regid, arg1='arg1')
        # assertions
        client.DB.session.query.assert_called_once_with(client.DB.Person)
        client.DB.session.query.return_value.filter.return_value.one_or_none.\
            assert_called_once()
        self.assertEqual(
            return_value, mock_map_person(mock_person, arg1='arg1'))

        # no person found
        client.DB.session.query.return_value.filter.return_value.one_or_none =\
            MagicMock(return_value=None)
        with self.assertRaises(PersonNotFoundException):
            client.get_person_by_uwregid(mock_regid)

    @patch('uw_person_client.clients.core_client.UWPersonClient._map_person')
    def test_get_person_by_student_number(self, mock_map_person):
        client = self.get_mock_person_client()
        # person exists
        mock_person = MagicMock()
        mock_student_number = 'test',
        client.DB.session.query.return_value.join.return_value.filter.\
            return_value.one_or_none = MagicMock(return_value=mock_person)

        return_value = client.get_person_by_student_number(
            mock_student_number, arg1='arg1')
        # assertions
        client.DB.session.query.assert_called_once_with(
            client.DB.Person)
        client.DB.session.query.return_value.join.assert_called_once_with(
            client.DB.Student)
        client.DB.session.query.return_value.join.return_value.filter.\
            assert_called_once_with(
                client.DB.Student.student_number == mock_student_number)
        client.DB.session.query.return_value.join.return_value.filter.\
            return_value.one_or_none.assert_called_once()
        self.assertEqual(
            return_value, mock_map_person(mock_person, arg1='arg1'))

        # no person found
        client.DB.session.query.return_value.join.return_value.filter.\
            return_value.one_or_none = MagicMock(return_value=None)
        with self.assertRaises(PersonNotFoundException):
            client.get_person_by_student_number(mock_student_number)

    @patch('uw_person_client.clients.core_client.UWPersonClient._map_person')
    def test_get_person_by_system_key(self, mock_map_person):
        client = self.get_mock_person_client()
        # person exists
        mock_person = MagicMock()
        mock_system_key = 'test',
        client.DB.session.query.return_value.join.return_value.filter.\
            return_value.one_or_none = MagicMock(return_value=mock_person)

        return_value = client.get_person_by_system_key(
            mock_system_key, arg1='arg1')
        # assertions
        client.DB.session.query.assert_called_once_with(
            client.DB.Person)
        client.DB.session.query.return_value.join.assert_called_once_with(
            client.DB.Student)
        client.DB.session.query.return_value.join.return_value.filter.\
            assert_called_once_with(
                client.DB.Student.system_key == mock_system_key)
        client.DB.session.query.return_value.join.return_value.filter.\
            return_value.one_or_none.assert_called_once()
        self.assertEqual(
            return_value, mock_map_person(mock_person, arg1='arg1'))

        # no person found
        client.DB.session.query.return_value.join.return_value.filter.\
            return_value.one_or_none = MagicMock(return_value=None)
        with self.assertRaises(PersonNotFoundException):
            client.get_person_by_system_key(mock_system_key)

    @patch('uw_person_client.clients.core_client.UWPersonClient._map_person')
    def test_get_persons(self, mock_map_person):
        client = self.get_mock_person_client()
        mock_person1, mock_person2 = MagicMock(), MagicMock()
        client.DB.session.query.return_value.all = \
            MagicMock(return_value=[mock_person1, mock_person2])
        return_value = client.get_persons()
        # assertions
        client.DB.session.query.assert_called_once_with(client.DB.Person)
        self.assertEqual(return_value,
                         [mock_map_person(mock_person1),
                          mock_map_person(mock_person2)])

    @patch.object(UWPersonClient, '_map_person', return_value=None)
    def test_get_registered_students(self, mock_map_person):
        client = self.get_mock_person_client()
        mock_person1, mock_person2 = MagicMock(), MagicMock()
        client.DB.session.query.return_value.join.return_value.filter.\
            return_value.all = MagicMock(
                return_value=[mock_person1, mock_person2])
        return_value = client.get_registered_students()
        # assertions
        client.DB.session.query.assert_called_once_with(client.DB.Person)
        client.DB.session.query.return_value.join.\
            assert_called_once_with(client.DB.Student)
        client.DB.session.query.return_value.join.return_value.filter.\
            assert_called_once_with(
                client.DB.Student.enroll_status_code == '12')
        self.assertEqual(return_value,
                         [mock_map_person(mock_person1),
                          mock_map_person(mock_person2)])

    @patch.object(UWPersonClient, '_map_person', return_value=None)
    def test_get_active_students(self, mock_map_person):
        client = self.get_mock_person_client()
        mock_person1, mock_person2 = MagicMock(), MagicMock()
        client.DB.session.query.return_value.filter.return_value.\
            all = MagicMock(return_value=[mock_person1, mock_person2])
        return_value = client.get_active_students()
        # assertions
        client.DB.session.query.assert_called_once_with(client.DB.Person)
        client.DB.session.query.return_value.filter.assert_called_once_with(
            client.DB.Person._is_active_student == True)  # noqa
        self.assertEqual(return_value,
                         [mock_map_person(mock_person1),
                          mock_map_person(mock_person2)])

    @patch.object(UWPersonClient, '_map_person', return_value=None)
    def test_get_active_employees(self, mock_map_person):
        client = self.get_mock_person_client()
        mock_person1, mock_person2 = MagicMock(), MagicMock()
        client.DB.session.query.return_value.filter.return_value.\
            all = MagicMock(return_value=[mock_person1, mock_person2])
        return_value = client.get_active_employees()
        # assertions
        client.DB.session.query.assert_called_once_with(client.DB.Person)
        client.DB.session.query.return_value.filter.assert_called_once_with(
            client.DB.Person._is_active_employee == True)  # noqa
        self.assertEqual(return_value,
                         [mock_map_person(mock_person1),
                          mock_map_person(mock_person2)])

    @patch.object(UWPersonClient, '_map_person', return_value=None)
    def test_get_advisers(self, mock_map_person):
        client = self.get_mock_person_client()
        mock_person1, mock_person2 = MagicMock(), MagicMock()
        client.DB.session.query.return_value.join.return_value.join.\
            return_value.all = MagicMock(
                return_value=[mock_person1, mock_person2])
        return_value = client.get_advisers()
        # assertions
        client.DB.session.query.assert_called_once_with(client.DB.Person)
        client.DB.session.query.return_value.join.assert_called_once_with(
            client.DB.Employee)
        client.DB.session.query.return_value.join.return_value.join.\
            assert_called_once_with(client.DB.Adviser)
        self.assertEqual(return_value,
                         [mock_map_person(mock_person1),
                          mock_map_person(mock_person2)])

    @patch.object(UWPersonClient, '_map_person', return_value=None)
    def test_get_advisers_with_program(self, mock_map_person):
        client = self.get_mock_person_client()
        mock_person1, mock_person2 = MagicMock(), MagicMock()
        client.DB.session.query.return_value.join.return_value.join.\
            return_value.filter.return_value.all = MagicMock(
                return_value=[mock_person1, mock_person2])
        advising_program = 'test'
        return_value = client.get_advisers(advising_program=advising_program)
        # assertions
        client.DB.session.query.assert_called_once_with(client.DB.Person)
        client.DB.session.query.return_value.join.assert_called_once_with(
            client.DB.Employee)
        client.DB.session.query.return_value.join.return_value.join.\
            assert_called_once_with(client.DB.Adviser)
        client.DB.session.query.return_value.join.return_value.join.\
            return_value.filter.assert_called_once_with(
                client.DB.Adviser.advising_program == advising_program)
        self.assertEqual(return_value,
                         [mock_map_person(mock_person1),
                          mock_map_person(mock_person2)])

    def test_get_persons_by_adviser_netid_not_found(self):
        client = self.get_mock_person_client()
        client.DB.session.query = MagicMock(side_effect=NoResultFound)
        with self.assertRaises(AdviserNotFoundException):
            client.get_persons_by_adviser_netid('test')

    @patch.object(UWPersonClient, '_map_person', return_value=None)
    def test_get_persons_by_adviser_netid(self, mock_map_person):
        client = self.get_mock_person_client()
        mock_adviser = MagicMock()
        mock_person1, mock_person2 = MagicMock(), MagicMock()
        mock_netid = MagicMock()
        client.DB.session.query.return_value.join.return_value.join.\
            return_value.filter.return_value.one = MagicMock(
                return_value=mock_adviser)
        client.DB.session.query.return_value.join.return_value.join.\
            return_value.join.return_value.filter.return_value.all = MagicMock(
                return_value=[mock_person1, mock_person2])
        return_value = client.get_persons_by_adviser_netid(mock_netid)
        # assertions
        client.DB.session.query.assert_any_call(client.DB.Person)
        client.DB.session.query.assert_any_call(client.DB.Adviser)
        client.DB.session.query.return_value.join.assert_any_call(
            client.DB.Employee)
        client.DB.session.query.return_value.join.assert_any_call(
            client.DB.Student)
        client.DB.session.query.return_value.join.return_value.join.\
            assert_any_call(client.DB.Person)
        client.DB.session.query.return_value.join.return_value.join.\
            assert_any_call(client.DB.StudentToAdviser)
        client.DB.session.query.return_value.join.return_value.join.\
            return_value.filter.assert_called_once_with(
                client.DB.Person.uwnetid == mock_netid)
        client.DB.session.query.return_value.join.return_value.join.\
            return_value.join.assert_called_once_with(
                client.DB.Adviser)
        client.DB.session.query.return_value.join.return_value.join.\
            return_value.join.return_value.filter.assert_called_once_with(
                client.DB.Adviser.id == mock_adviser.id)
        self.assertEqual(return_value,
                         [mock_map_person(mock_person1),
                          mock_map_person(mock_person2)])

    def test_get_persons_by_adviser_regid_not_found(self):
        client = self.get_mock_person_client()
        client.DB.session.query = MagicMock(side_effect=NoResultFound)
        with self.assertRaises(AdviserNotFoundException):
            client.get_persons_by_adviser_regid('test')

    @patch.object(UWPersonClient, '_map_person', return_value=None)
    def test_get_persons_by_adviser_regid(self, mock_map_person):
        client = self.get_mock_person_client()
        mock_adviser = MagicMock()
        mock_person1, mock_person2 = MagicMock(), MagicMock()
        mock_regid = MagicMock()
        client.DB.session.query.return_value.join.return_value.join.\
            return_value.filter.return_value.one = MagicMock(
                return_value=mock_adviser)
        client.DB.session.query.return_value.join.return_value.join.\
            return_value.join.return_value.filter.return_value.all = MagicMock(
                return_value=[mock_person1, mock_person2])
        return_value = client.get_persons_by_adviser_regid(mock_regid)
        # assertions
        client.DB.session.query.assert_any_call(client.DB.Person)
        client.DB.session.query.assert_any_call(client.DB.Adviser)
        client.DB.session.query.return_value.join.assert_any_call(
            client.DB.Employee)
        client.DB.session.query.return_value.join.assert_any_call(
            client.DB.Student)
        client.DB.session.query.return_value.join.return_value.join.\
            assert_any_call(client.DB.Person)
        client.DB.session.query.return_value.join.return_value.join.\
            assert_any_call(client.DB.StudentToAdviser)
        client.DB.session.query.return_value.join.return_value.join.\
            return_value.filter.assert_called_once_with(
                client.DB.Person.uwregid == mock_regid)
        client.DB.session.query.return_value.join.return_value.join.\
            return_value.join.assert_called_once_with(
                client.DB.Adviser)
        client.DB.session.query.return_value.join.return_value.join.\
            return_value.join.return_value.filter.assert_called_once_with(
                client.DB.Adviser.id == mock_adviser.id)
        self.assertEqual(return_value,
                         [mock_map_person(mock_person1),
                          mock_map_person(mock_person2)])

    def _mock_to_dict(self, mock):
        keys = set(dir(mock)) - set(dir(MagicMock()))
        mock_dict = {}
        for key in keys:
            mock_dict[key] = getattr(mock, key)
        return mock_dict

    @patch('uw_person_client.clients.core_client.UWPersonClient._map_student')
    @patch('uw_person_client.clients.core_client.UWPersonClient._map_employee')
    def test_map_person(self, mock_map_employee, mock_map_student):
        client = self.get_mock_person_client()
        mock_priors = [MagicMock()]
        mock_priors[0].uwnetid = MagicMock()
        mock_priors[0].uwregid = MagicMock()
        client.DB.session.query.return_value.filter.return_value.all.\
            return_value = mock_priors

        mock_person = MagicMock()
        mock_person.uwnetid = MagicMock()
        mock_person.uwregid = MagicMock()
        mock_person.first_name = MagicMock()
        mock_person.prior_uwnetids = [mock_priors[0].uwnetid]
        mock_person.prior_uwregids = [mock_priors[0].uwregid]
        mock_person.pronouns = MagicMock()
        mock_person.full_name = MagicMock()
        mock_person.display_name = MagicMock()
        mock_person.surname = MagicMock()
        mock_person.preferred_first_name = MagicMock()
        mock_person.preferred_middle_name = MagicMock()
        mock_person.preferred_surname = MagicMock()
        mock_person.whitepages_publish = MagicMock()
        mock_person._is_active_student = MagicMock()
        mock_person._is_active_employee = MagicMock()

        mock_dict = self._mock_to_dict(mock_person)
        person = client._map_person(mock_person)
        # assertions
        self.assertIsInstance(person, Person)
        self.assertEqual(mock_person._is_active_student, person.active_student)
        self.assertEqual(mock_person._is_active_employee,
                         person.active_employee)
        for key in ['_is_active_student', '_is_active_employee']:
            del mock_dict[key]
        self.assertDictContainsSubset(mock_dict, person.to_dict())
        mock_map_employee.assert_called()
        mock_map_student.assert_called()

    @patch('uw_person_client.clients.core_client.UWPersonClient._map_person')
    @patch('uw_person_client.clients.core_client.UWPersonClient._map_major')
    @patch('uw_person_client.clients.core_client.UWPersonClient._map_term')
    @patch('uw_person_client.clients.core_client.UWPersonClient._map_sport')
    @patch('uw_person_client.clients.core_client.UWPersonClient.'
           '_map_transcript')
    @patch('uw_person_client.clients.core_client.UWPersonClient._map_transfer')
    def test_map_student(self, mock_map_transfer, mock_map_transcript,
                         mock_map_sport, mock_map_term, mock_map_major,
                         mock_map_person):
        client = self.get_mock_person_client()
        mock_student = MagicMock()
        mock_student.system_key = MagicMock()
        mock_student.student_number = MagicMock()
        mock_student.application_status_code = MagicMock()
        mock_student.application_status_desc = MagicMock()
        mock_student.application_type_code = MagicMock()
        mock_student.application_type_desc = MagicMock()
        mock_student.applied_to_graduate_yr_qtr_desc = MagicMock()
        mock_student.applied_to_graduate_yr_qtr_id = MagicMock()
        mock_student.asuwind = MagicMock()
        mock_student.birth_city = MagicMock()
        mock_student.birth_country = MagicMock()
        mock_student.birth_state = MagicMock()
        mock_student.birthdate = MagicMock()
        mock_student.campus_code = MagicMock()
        mock_student.campus_desc = MagicMock()
        mock_student.child_of_alumni = MagicMock()
        mock_student.citizen_country = MagicMock()
        mock_student.class_code = MagicMock()
        mock_student.class_desc = MagicMock()
        mock_student.cumulative_gpa = MagicMock()
        mock_student.directory_release_ind = MagicMock()
        mock_student.disability_ind = MagicMock()
        mock_student.emergency_email = MagicMock()
        mock_student.emergency_name = MagicMock()
        mock_student.emergency_phone = MagicMock()
        mock_student.enroll_status_code = MagicMock()
        mock_student.enroll_status_request_code = MagicMock()
        mock_student.enroll_status_desc = MagicMock()
        mock_student.ethnic_code = MagicMock()
        mock_student.ethnic_desc = MagicMock()
        mock_student.ethnic_long_desc = MagicMock()
        mock_student.ethnic_group_code = MagicMock()
        mock_student.exemption_code = MagicMock()
        mock_student.exemption_desc = MagicMock()
        mock_student.external_email = MagicMock()
        mock_student.first_generation_4yr_ind = MagicMock()
        mock_student.first_generation_ind = MagicMock()
        mock_student.gender = MagicMock()
        mock_student.high_school_gpa = MagicMock()
        mock_student.high_school_graduation_date = MagicMock()
        mock_student.hispanic_code = MagicMock()
        mock_student.hispanic_desc = MagicMock()
        mock_student.hispanic_long_desc = MagicMock()
        mock_student.hispanic_group_code = MagicMock()
        mock_student.honors_program_code = MagicMock()
        mock_student.honors_program_ind = MagicMock()
        mock_student.iss_perm_resident_country = MagicMock()
        mock_student.jr_col_gpa = MagicMock()
        mock_student.last_enrolled_yr_qtr_desc = MagicMock()
        mock_student.last_enrolled_yr_qtr_id = MagicMock()
        mock_student.local_addr_4digit_zip = MagicMock()
        mock_student.local_addr_5digit_zip = MagicMock()
        mock_student.local_addr_city = MagicMock()
        mock_student.local_addr_country = MagicMock()
        mock_student.local_addr_line1 = MagicMock()
        mock_student.local_addr_line2 = MagicMock()
        mock_student.local_addr_postal_code = MagicMock()
        mock_student.local_addr_state = MagicMock()
        mock_student.local_phone_number = MagicMock()
        mock_student.new_continuing_returning_code = MagicMock()
        mock_student.new_continuing_returning_desc = MagicMock()
        mock_student.parent_name = MagicMock()
        mock_student.perm_addr_4digit_zip = MagicMock()
        mock_student.perm_addr_5digit_zip = MagicMock()
        mock_student.perm_addr_city = MagicMock()
        mock_student.perm_addr_country = MagicMock()
        mock_student.perm_addr_line1 = MagicMock()
        mock_student.perm_addr_line2 = MagicMock()
        mock_student.perm_addr_postal_code = MagicMock()
        mock_student.perm_addr_state = MagicMock()
        mock_student.previous_institution_name = MagicMock()
        mock_student.previous_institution_type = MagicMock()
        mock_student.previous_institution_type_desc = MagicMock()
        mock_student.record_load_dttm = MagicMock()
        mock_student.record_update_dttm = MagicMock()
        mock_student.reg_first_yr_qtr_desc = MagicMock()
        mock_student.reg_first_yr_qtr_id = MagicMock()
        mock_student.registered_in_quarter = MagicMock()
        mock_student.registration_hold_ind = MagicMock()
        mock_student.resident_code = MagicMock()
        mock_student.resident_desc = MagicMock()
        mock_student.special_program_code = MagicMock()
        mock_student.special_program_desc = MagicMock()
        mock_student.sr_col_gpa = MagicMock()
        mock_student.student_email = MagicMock()
        mock_student.total_credits = MagicMock()
        mock_student.total_deductible_credits = MagicMock()
        mock_student.total_extension_credits = MagicMock()
        mock_student.total_grade_attempted = MagicMock()
        mock_student.total_grade_points = MagicMock()
        mock_student.total_lower_div_transfer_credits = MagicMock()
        mock_student.total_non_graded_credits = MagicMock()
        mock_student.total_registered_credits = MagicMock()
        mock_student.total_transfer_credits = MagicMock()
        mock_student.total_uw_credits = MagicMock()
        mock_student.total_upper_div_transfer_credits = MagicMock()
        mock_student.veteran_benefit_code = MagicMock()
        mock_student.veteran_benefit_desc = MagicMock()
        mock_student.veteran_desc = MagicMock()
        mock_student.visa_type = MagicMock()
        mock_student.sport = [MagicMock(), MagicMock()]
        mock_student.adviser = [MagicMock(), MagicMock()]
        mock_student.transcript = [MagicMock(), MagicMock()]
        mock_student.transfer = [MagicMock(), MagicMock()]
        mock_dict = self._mock_to_dict(mock_student)
        client.DB.session.query.return_value.filter.return_value.one.\
            return_value = mock_student
        student = client._map_student(mock_student)
        # assertions
        self.assertIsInstance(student, Student)
        for key in ['adviser', 'sport', 'transcript', 'transfer']:
            del mock_dict[key]
        self.assertDictContainsSubset(mock_dict, student.to_dict())
        mock_map_term.assert_called()
        mock_map_sport.assert_called()
        mock_map_major.assert_called()
        mock_map_person.assert_called()
        mock_map_transcript.assert_called()
        mock_map_transfer.assert_called()

    @patch('uw_person_client.clients.core_client.UWPersonClient._map_adviser')
    def test_map_employee(self, mock_map_adviser):
        client = self.get_mock_person_client()
        mock_employee = MagicMock()
        mock_employee.employee_number = MagicMock()
        mock_employee.employee_affiliation_state = MagicMock()
        mock_employee.email_addresses = MagicMock()
        mock_employee.home_department = MagicMock()
        mock_employee.title = MagicMock()
        mock_employee.department = MagicMock()

        mock_dict = self._mock_to_dict(mock_employee)
        employee = client._map_employee(mock_employee)

        # assertions
        self.assertIsInstance(employee, Employee)
        self.assertEqual(mock_employee.title, employee.primary_title)
        self.assertEqual(mock_employee.department, employee.primary_department)
        for key in ['title', 'department']:
            del mock_dict[key]
        self.assertDictContainsSubset(mock_dict, employee.to_dict())
        mock_map_adviser.assert_called_once()

    def test_map_adviser(self):
        client = self.get_mock_person_client()
        mock_adviser = MagicMock()
        mock_adviser.is_dept_adviser = MagicMock()
        mock_adviser.advising_email = MagicMock()
        mock_adviser.advising_phone_number = MagicMock()
        mock_adviser.advising_program = MagicMock()
        mock_adviser.advising_pronouns = MagicMock()
        mock_adviser.booking_url = MagicMock()

        mock_dict = self._mock_to_dict(mock_adviser)
        adviser = client._map_adviser(mock_adviser)

        # assertions
        self.assertIsInstance(adviser, Adviser)
        self.assertDictContainsSubset(mock_dict, adviser.to_dict())

    def test_map_sport(self):
        client = self.get_mock_person_client()
        mock_sport = MagicMock()
        mock_sport.sport_code = MagicMock()

        mock_dict = self._mock_to_dict(mock_sport)
        sport = client._map_sport(mock_sport)

        # assertions
        self.assertIsInstance(sport, Sport)
        self.assertDictContainsSubset(mock_dict, sport.to_dict())

    def test_map_major(self):
        client = self.get_mock_person_client()
        mock_major = MagicMock()
        mock_major.major_abbr_code = MagicMock()
        mock_major.major_pathway = MagicMock()
        mock_major.major_branch = MagicMock()
        mock_major.major_name = MagicMock()
        mock_major.major_full_name = MagicMock()
        mock_major.major_short_name = MagicMock()
        mock_major.major_desc = MagicMock()
        mock_major.major_home_url = MagicMock()
        mock_major.major_dept = MagicMock()
        mock_major.major_last_yr = MagicMock()
        mock_major.major_last_qtr = MagicMock()
        mock_major.major_first_yr = MagicMock()
        mock_major.major_first_qtr = MagicMock()
        mock_major.major_cip_code = MagicMock()
        mock_major.major_undergrad = MagicMock()
        mock_major.major_graduate = MagicMock()
        mock_major.major_professional = MagicMock()
        mock_major.major_non_degree = MagicMock()
        mock_major.major_minor = MagicMock()
        mock_major.major_not_termin = MagicMock()
        mock_major.major_ug_certif = MagicMock()
        mock_major.major_grad_certif = MagicMock()
        mock_major.major_evening = MagicMock()
        mock_major.major_ss_std_act = MagicMock()
        mock_major.major_ss_inelig = MagicMock()
        mock_major.major_osfa_inelig = MagicMock()
        mock_major.major_dist_learn = MagicMock()
        mock_major.major_concur_cc = MagicMock()
        mock_major.major_measles_ex = MagicMock()
        mock_major.major_premaj = MagicMock()
        mock_major.major_premaj_ext = MagicMock()
        mock_major.major_nonmatric = MagicMock()
        mock_major.major_gnm = MagicMock()
        mock_major.college = MagicMock()

        mock_dict = self._mock_to_dict(mock_major)
        major = client._map_major(mock_major)

        # assertions
        self.assertIsInstance(major, Major)
        self.assertDictContainsSubset(mock_dict, major.to_dict())

    @patch('uw_person_client.clients.core_client.UWPersonClient._map_term')
    def test_map_transcript(self, mock_map_term):
        client = self.get_mock_person_client()
        mock_transcript = MagicMock()
        mock_transcript.tran_term = MagicMock()
        mock_transcript.leave_ends_term = MagicMock()
        mock_transcript.resident = MagicMock()
        mock_transcript.resident_cat = MagicMock()
        mock_transcript.veteran = MagicMock()
        mock_transcript.veteran_benefit = MagicMock()
        mock_transcript.class_code = MagicMock()
        mock_transcript.qtr_grade_points = MagicMock()
        mock_transcript.qtr_graded_attmp = MagicMock()
        mock_transcript.qtr_nongrd_earned = MagicMock()
        mock_transcript.qtr_deductible = MagicMock()
        mock_transcript.over_qtr_grade_pt = MagicMock()
        mock_transcript.over_qtr_grade_at = MagicMock()
        mock_transcript.over_qtr_nongrd = MagicMock()
        mock_transcript.over_qtr_deduct = MagicMock()
        mock_transcript.qtr_comment = MagicMock()
        mock_transcript.honors_program = MagicMock()
        mock_transcript.special_program = MagicMock()
        mock_transcript.scholarship_type = MagicMock()
        mock_transcript.yearly_honor_type = MagicMock()
        mock_transcript.exemption_code = MagicMock()
        mock_transcript.num_ind_study = MagicMock()
        mock_transcript.num_courses = MagicMock()
        mock_transcript.enroll_status = MagicMock()
        mock_transcript.tenth_day_credits = MagicMock()
        mock_transcript.tr_en_stat_dt = MagicMock()

        mock_dict = self._mock_to_dict(mock_transcript)
        transcript = client._map_transcript(mock_transcript)

        # assertions
        self.assertIsInstance(transcript, Transcript)
        self.assertEqual(mock_map_term.return_value, transcript.tran_term)
        mock_map_term.assert_any_call(mock_transcript.tran_term)
        self.assertEqual(mock_map_term.return_value,
                         transcript.leave_ends_term)
        mock_map_term.assert_any_call(mock_transcript.leave_ends_term)
        self.assertEqual(float(mock_transcript.qtr_grade_points),
                         transcript.qtr_grade_points)
        self.assertEqual(float(mock_transcript.qtr_graded_attmp),
                         transcript.qtr_graded_attmp)
        self.assertEqual(float(mock_transcript.tenth_day_credits),
                         transcript.tenth_day_credits)
        for key in ['tran_term', 'leave_ends_term', 'qtr_grade_points',
                    'qtr_graded_attmp', 'tenth_day_credits']:
            del mock_dict[key]
        self.assertDictContainsSubset(mock_dict, transcript.to_dict())

    def test_map_transfer(self):
        client = self.get_mock_person_client()
        mock_transfer = MagicMock()
        mock_transfer.institution_code = MagicMock()
        mock_transfer.year_ending = MagicMock()
        mock_transfer.year_beginning = MagicMock()
        mock_transfer.transfer_gpa = MagicMock()
        mock_transfer.trans_updt_dt = MagicMock()
        mock_transfer.trans_updt_id = MagicMock()
        mock_transfer.degree_earned = MagicMock()
        mock_transfer.degree_earned_yr = MagicMock()
        mock_transfer.degree_earned_mo = MagicMock()
        mock_transfer.credential_lvl = MagicMock()
        mock_transfer.credential_yr = MagicMock()
        mock_transfer.transfer_comment = MagicMock()
        mock_transfer.institution_name = MagicMock()
        mock_transfer.inst_addr_line_1 = MagicMock()
        mock_transfer.inst_addr_line_2 = MagicMock()
        mock_transfer.inst_city = MagicMock()
        mock_transfer.inst_state = MagicMock()
        mock_transfer.inst_zip_5 = MagicMock()
        mock_transfer.inst_zip_filler = MagicMock()
        mock_transfer.inst_country = MagicMock()
        mock_transfer.inst_postal_cd = MagicMock()
        mock_transfer.inst_record_stat = MagicMock()
        mock_transfer.two_year = MagicMock()
        mock_transfer.wa_cc = MagicMock()

        mock_dict = self._mock_to_dict(mock_transfer)
        transfer = client._map_transfer(mock_transfer)

        # assertions
        self.assertIsInstance(transfer, Transfer)
        self.assertDictContainsSubset(mock_dict, transfer.to_dict())

    def test_map_hold(self):
        client = self.get_mock_person_client()
        mock_hold = MagicMock()
        mock_hold.seq = MagicMock()
        mock_hold.hold_dt = MagicMock()
        mock_hold.hold_office = MagicMock()
        mock_hold.hold_office_desc = MagicMock()
        mock_hold.hold_reason = MagicMock()
        mock_hold.hold_type = MagicMock()

        mock_dict = self._mock_to_dict(mock_hold)
        hold = client._map_hold(mock_hold)

        # assertions
        self.assertIsInstance(hold, Hold)
        self.assertDictContainsSubset(mock_dict, hold.to_dict())

    @patch('uw_person_client.clients.core_client.UWPersonClient._map_term')
    def test_map_degree(self, mock_map_term):
        client = self.get_mock_person_client()
        mock_degree = MagicMock()
        mock_degree.degree_term = MagicMock()
        mock_degree.campus_code = MagicMock()
        mock_degree.degree_abbr_code = MagicMock()
        mock_degree.degree_pathway_num = MagicMock()
        mock_degree.degree_level_code = MagicMock()
        mock_degree.degree_level_desc = MagicMock()
        mock_degree.degree_type_code = MagicMock()
        mock_degree.degree_level_type_desc = MagicMock()
        mock_degree.degree_desc = MagicMock()
        mock_degree.degree_uw_credits = MagicMock()
        mock_degree.degree_transfer_credits = MagicMock()
        mock_degree.degree_extension_credits = MagicMock()
        mock_degree.degree_gpa = MagicMock()
        mock_degree.fin_org_key = MagicMock()
        mock_degree.primary_fin_org_key = MagicMock()

        mock_dict = self._mock_to_dict(mock_degree)
        degree = client._map_degree(mock_degree)

        # assertions
        self.assertIsInstance(degree, Degree)
        self.assertEqual(mock_map_term.return_value, degree.degree_term)
        del mock_dict['degree_term']
        self.assertDictContainsSubset(mock_dict, degree.to_dict())

    def test_map_term(self):
        client = self.get_mock_person_client()
        mock_term = MagicMock()
        mock_term.year = MagicMock()
        mock_term.quarter = MagicMock()

        mock_dict = self._mock_to_dict(mock_term)
        term = client._map_term(mock_term)

        # assertions
        self.assertIsInstance(term, Term)
        self.assertDictContainsSubset(mock_dict, term.to_dict())
