import logging
import unittest
from inventory import (Base,
                       Company,
                       Office,
                       Group,
                       Host)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

LOG = logging.getLogger('Manager')


class TestClasses(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.engine = create_engine('sqlite://', echo=False)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)
        # NOTE: Fix this by putting all permanent DB objects into db here.
        #       Remove the same from test_* methods.
        self.loadClassData()

    @classmethod
    def tearDownClass(self):
        if self.session:
            self.session.close()

    @classmethod
    def loadClassData(self):
        LOG.info("Testing Class Structure")

        # Add companies
        self.companies = {}
        acme = Company(name='Acme')
        redhat = Company(name='Redhat')
        try:
            self.session.add(redhat)
            self.session.add(acme)
            self.session.commit()
        except Exception as ex:
            LOG.debug("Unexpected Company error: %s", ex)
            self.session.rollback()
        else:
            self.companies.update({'acme': acme})
            self.companies.update({'redhat': redhat})

        # Add offices
        self.offices = {}
        austin = Office(name='Austin', company=acme)
        houston = Office(name='Houston', company=acme)
        dallas = Office(name='Dallas', company=redhat)
        try:
            self.session.add(austin)
            self.session.add(houston)
            self.session.add(dallas)
            self.session.commit()
        except Exception as ex:
            LOG.info("Unexpected Office error: %s", ex)
            self.session.rollback()
        else:
            self.offices.update({'austin': austin})
            self.offices.update({'houston': houston})
            self.offices.update({'dallas': dallas})

        # Add groups
        self.groups = {}
        it = Group(name='IT', company=acme, office=austin)
        dev = Group(name='Dev', company=acme, office=austin)
        ops = Group(name='Ops', company=redhat, office=dallas)
        try:
            self.session.add(it)
            self.session.add(dev)
            self.session.add(ops)
            self.session.commit()
        except Exception as ex:
            LOG.error("Unexpected group error: %s", ex)
            self.session.rollback()
        else:
            self.groups.update({'it': it})
            self.groups.update({'dev': dev})
            self.groups.update({'ops': ops})
            self.austin_groups = [it, dev]
            self.dallas_groups = [ops]

        # Add hosts
        self.hosts = {}
        roadrunner = Host(name='roadrunner',
                          company=acme,
                          office=austin,
                          groups=self.austin_groups)
        coyote = Host(name='coyote',
                      company=acme,
                      office=austin,
                      groups=self.austin_groups)
        bogart = Host(name='bogart',
                      company=redhat,
                      office=dallas,
                      groups=self.dallas_groups)
        try:
            self.session.add(roadrunner)
            self.session.add(coyote)
            self.session.add(bogart)
            self.session.commit()
        except Exception as ex:
            LOG.error("Unexpected host error: %s", ex)
            self.session.rollback()
        else:
            self.hosts.update({'roadrunner': roadrunner})
            self.hosts.update({'coyote': coyote})
            self.hosts.update({'bogart': bogart})

    def test_Company(self):

        # Ensure you cant add same company twice
        company2 = Company(name='Acme')
        self.session.add(company2)
        try:
            self.session.commit()
        except Exception as ex:
            LOG.info("Company: Rollback expected commit")
            self.session.rollback()
            self.assertIsNotNone(ex)
            self.assertEquals(ex.__class__, IntegrityError)

        # Ensure that you can't add a company without Name
        company3 = Company(name=None)
        try:
            self.session.add(company3)
            self.session.commit()
        except Exception as ex:
            LOG.info("Company: Rollback expected commit")
            self.session.rollback()
            self.assertEquals(ex.__class__, IntegrityError)
        else:
            self.assertTrue(False)

    def test_Office(self):
        LOG.info("Checking Office Integrity...")
        acme = self.companies.get('acme')

        # Ensure you can't add same office twice
        office3 = Office(name='Austin', company=acme)
        try:
            self.session.add(office3)
            self.session.commit()
        except Exception as ex:
            LOG.info("Office: Rollback of expected commit!")
            self.session.rollback()
            self.assertIsNotNone(ex)
            self.assertEquals(ex.__class__, IntegrityError)
        else:
            # Fail the test because it didn't catch
            self.assertFalse(True)

        # Ensure you can't add office without valid company
        office4 = Office(name='Austin', company=None)
        try:
            self.session.add(office4)
            self.session.commit()
        except Exception as ex:
            self.session.rollback()
            self.assertIsNotNone(ex)
            self.assertEquals(ex.__class__, IntegrityError)
        else:
            self.assertFalse(True)

    def test_Group(self):
        LOG.info("Checking Group Integrity...")
        acme = self.companies.get('acme')
        redhat = self.companies.get('redhat')

        # Ensure you can't add same group twice
        group1 = Group(name='IT', company=acme)
        group2 = Group(name='IT', company=redhat)
        try:
            self.session.add(group1)
            self.session.add(group2)
            self.session.commit()
        except Exception as ex:
            LOG.info("Group: Rollback of expected commit!")
            self.session.rollback()
            self.assertIsNotNone(ex)
            self.assertEquals(ex.__class__, IntegrityError)
        else:
            # Fail the test
            self.assertFalse(True)

        # Ensure you can't add group without valid company
        group4 = Group(name='musicians', company=None)
        try:
            self.session.add(group4)
            self.session.commit()
        except Exception as ex:
            self.session.rollback()
            self.assertIsNotNone(ex)
            self.assertEquals(ex.__class__, IntegrityError)
        else:
            # Fail the test
            self.assertFalse(True)

    def test_Host(self):
        LOG.info("Checking Host Integrity...")
        acme = self.companies.get('acme')

        austin = self.offices.get('austin')
        houston = self.offices.get('houston')

        # Ensure you can't add same host twice
        roadrunner = Host(name='roadrunner',
                          company=acme,
                          office=austin,
                          groups=self.austin_groups)
        try:
            self.session.add(roadrunner)
            self.session.commit()
        except Exception as ex:
            LOG.info("Host: Rollback of expected commit!")
            self.session.rollback()
            self.assertIsNotNone(ex)
            self.assertEquals(ex.__class__, IntegrityError)
        else:
            # Fail the test
            self.assertFalse(True)

        # Ensure you can't add host with Nulls
        try:
            ghost = Host(name='ghost',
                         company=acme,
                         office=houston,
                         groups=None)
            self.session.add(ghost)
            self.session.commit()
        except Exception as ex:
            LOG.info("Host: Rollback of empty groups!")
            self.session.rollback()
            self.assertIsNotNone(ex)
            self.assertEquals(ex.__class__, TypeError)
        else:
            # Fail the test
            self.assertFalse(True)
