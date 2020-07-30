import logging
import unittest
from Manager import Manager
from sqlalchemy import create_engine

LOG = logging.getLogger('Manager')


class TestClasses(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.engine = create_engine('sqlite://', echo=False)
        self.manager = Manager(self.engine)

        self.loadManagerData()

    @classmethod
    def tearDownClass(self):
        pass

    @classmethod
    def loadManagerData(self):
        # Add companies
        self.companies = {}
        acme = self.manager.add_company(company_name='Acme')
        redhat = self.manager.add_company(company_name='RedHat')
        self.companies.update({'acme': acme})
        self.companies.update({'redhat': redhat})

        # Add offices
        self.offices = {}
        austin = self.manager.add_office(office_name='Austin',
                                         company_name=acme.name)
        houston = self.manager.add_office(office_name='Houston',
                                          company_name=acme.name)
        dallas = self.manager.add_office(office_name='Dallas',
                                         company_name=redhat.name)
        self.offices.update({'austin': austin})
        self.offices.update({'houston': houston})
        self.offices.update({'dallas': dallas})

        # Add groups
        self.groups = {}
        it = self.manager.add_group(group_name='IT',
                                    company_name=acme.name,
                                    office_name=austin.name)
        dev = self.manager.add_group(group_name='Dev',
                                     company_name=acme.name,
                                     office_name=austin.name)
        ops = self.manager.add_group(group_name='Ops',
                                     company_name=redhat.name,
                                     office_name=dallas.name)

        self.groups.update({'it': it})
        self.groups.update({'dev': dev})
        self.groups.update({'ops': ops})
        self.austin_groups = [it.name, dev.name]
        self.dallas_groups = [ops.name]

        # Add hosts
        self.hosts = {}
        roadrunner = self.manager.add_host(hostname='roadrunner',
                                           company_name=acme.name,
                                           office_name=austin.name,
                                           group_names=self.austin_groups)
        coyote = self.manager.add_host(hostname='coyote',
                                       company_name=acme.name,
                                       office_name=austin.name,
                                       group_names=self.austin_groups)
        bugs = self.manager.add_host(hostname='bugs',
                                     company_name=redhat.name,
                                     office_name=dallas.name,
                                     group_names=self.dallas_groups)

        self.hosts.update({'roadrunner': roadrunner})
        self.hosts.update({'coyote': coyote})
        self.hosts.update({'bugs': bugs})

    def test_Company(self):

        # Ensure you cant add a company
        testCo = self.manager.add_company(company_name="TestCompany")
        self.assertIsNotNone(testCo)

        # Ensure you can delete a company
        testCo = self.manager.del_company(company_name="TestCompany")
        testCo = self.manager.get_company(company_name="TestCompany")
        self.assertIsNone(testCo)

        # Ensure you can't add same company twice
        testCo = self.manager.add_company(company_name="Acme")
        self.assertIsNone(testCo)

        # Ensure that you can't add a company without Name
        testCo = self.manager.add_company(company_name=None)
        self.assertIsNone(testCo)

    def test_Office(self):

        acme = self.companies.get('acme')

        # Ensure you can add an office
        nowhere = self.manager.add_office(office_name="Nowhere", company_name=acme.name)
        self.assertIsNotNone(nowhere)

        # Ensure you can del an office
        nowhere = self.manager.del_office(office_name="Nowhere", company_name=acme.name)
        nowhere = self.manager.get_office(office_name="Nowhere", company_name=acme.name)
        self.assertIsNone(nowhere)

        # Ensure you can't add same office twice
        nowhere = self.manager.add_office(office_name="Austin", company_name=acme.name)
        self.assertIsNone(nowhere)

        # Ensure you can't add office without valid company
        nowhere = self.manager.add_office(office_name="Somewhere", company_name=None)
        self.assertIsNone(nowhere)

    def test_Group(self):
        LOG.info("Checking Group Methods...")
        acme = self.companies.get('acme')
        austin = self.offices.get('austin')

        # Ensure you can't add same group twice
        it = self.manager.add_group(group_name='IT',
                                    company_name=acme.name,
                                    office_name=austin.name)
        self.assertIsNone(it)

        # Ensure you can't add group without valid company
        it = self.manager.add_group(group_name='IT',
                                    company_name="BogusCompany",
                                    office_name=austin.name)
        self.assertIsNone(it)

        # Ensure you can't add group without a company
        it = self.manager.add_group(group_name='IT',
                                    company_name=None,
                                    office_name=austin.name)
        self.assertIsNone(it)

        # Ensure you can delete group
        it = self.manager.del_group(group_name='IT',
                                    company_name=acme.name,
                                    office_name=austin.name)
        self.assertIsNone(it)

        # Ensure you can add a group
        it = self.manager.add_group(group_name='IT',
                                    company_name=acme.name,
                                    office_name=austin.name)
        self.assertIsNotNone(it)

    def test_Host(self):
        LOG.info("Checking Host Integrity...")
        acme = self.companies.get('acme')
        redhat = self.companies.get('redhat')

        austin = self.offices.get('austin')
        dallas = self.offices.get('dallas')

        # Ensure you can't add same host twice
        duplicate = self.manager.add_host(hostname='bugs',
                                          company_name=redhat.name,
                                          office_name=dallas.name,
                                          group_names=self.dallas_groups)
        self.assertIsNone(duplicate)

        bugs = self.manager.add_host(hostname='bugs',
                                     company_name=acme.name,
                                     office_name=austin.name,
                                     group_names=self.austin_groups)
        self.assertIsNotNone(bugs)

        # Ensure you can't add host with Null office_name
        daffy = self.manager.add_host(hostname='bugs',
                                      company_name=acme.name,
                                      office_name='',
                                      group_names=self.austin_groups)
        self.assertIsNone(daffy)

        # Ensure you can't add host with empty groups
        daffy = self.manager.add_host(hostname='bugs',
                                      company_name=acme.name,
                                      office_name=austin.name,
                                      group_names=[])
        self.assertIsNone(daffy)

        # Ensure you can get host
        host = self.manager.get_host(hostname='roadrunner',
                                     company_name=acme.name,
                                     office_name=austin.name)
        self.assertIsNotNone(host)

        # Ensure you can get hosts
        hosts = self.manager.get_hosts(company_name=acme.name,
                                       office_name=austin.name)
        self.assertIsNotNone(hosts)

        # Ensure you can delete hosts
        host = self.manager.del_host(hostname='roadrunner',
                                     company_name=acme.name,
                                     office_name=austin.name)
        self.assertIsNone(host)

        host = self.manager.get_host(hostname='roadrunner',
                                     company_name=acme.name,
                                     office_name=austin.name)
        self.assertIsNone(host)
