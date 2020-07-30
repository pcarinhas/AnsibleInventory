"""Manager class for Inventory tansactions."""

import logging
import os
from sqlalchemy.orm import sessionmaker

from inventory import (Base,
                       Company,
                       Office,
                       Group,
                       Host,
                       )

from pprint import pprint as pp
LOG = logging.getLogger('Manager')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)15s() ] %(message)s"
logging.basicConfig(format=FORMAT)
LOG.setLevel(level=os.environ.get("LOGLEVEL", "INFO"))


def create_manager(engine):
    """Return a Manager object."""
    return Manager(engine)


class Manager():
    """Manager class for inventory transaction with sqlalchemy."""

    def __init__(self, engine):
        """Initialize the Session object."""
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine)

    def __exit__(self):
        """Ensure self.session is closed upon exit."""
        if self.session:
            self.session.close()

    def dump_hosts_by_group(self):
        """Dump all the information required in JSON format."""
        group_hosts = {}
        for company in self.session.query(Company):
            for office in company.offices:
                for group in office.groups:
                    group_name = '{}_{}_{}'.format(company.name,
                                                   office.name,
                                                   group.name)
                    _hosts = []
                    for host in group.hosts:
                        _hosts.append(host.name)
                    group_hosts[group_name] = _hosts
                    pp(group_hosts)

    def add_company(self, company_name=None):
        company = self.session.query(Company).filter(Company.name==company_name)
        if company.one_or_none():
            LOG.error("Company exists: %s", company_name)
            return

        try:
            company = Company(name=company_name)
            self.session.add(company)
            self.session.commit()

        except Exception as ex:
            self.session.rollback()
            LOG.error("Problem adding company: %s: %s", company_name, ex)

        else:
            return company

    def del_company(self, company_name=None):
        company = self.session.query(Company).filter(Company.name==company_name).one_or_none()
        if not company:
            LOG.error("Company doesnt exists: %s", company_name)
            return

        try:
            self.session.delete(company)
            self.session.commit()

        except Exception as ex:
            self.session.rollback()
            LOG.error("Problem adding company: %s: %s", company_name, ex)

    def list_companies(self):
        companies = self.session.query(Company)
        # self.session.commit()
        if not companies:
            LOG.info("No companies found!")
        for company in companies.all():
            print(company.name)

    def get_company(self, company_name):
        company = self.session.query(Company).filter(Company.name==company_name)
        if not company.one_or_none():
            LOG.info("No such company '%s'", company_name)
            return
        return company.one_or_none()

    def add_office(self, office_name=None, company_name=None):
        if not office_name and not company_name:
            LOG.error("Missing required office_name/company_name")
            return
        company = self.get_company(company_name)
        if not company:
            LOG.error("Company does not Exists: %s", company_name)
            return

        for office in company.offices:
            if office.name == office_name:
                LOG.error("Office already exists: %s", office_name)
                return

        try:
            office = Office(name=office_name, company=company)
            self.session.add(office)
            self.session.commit()

        except Exception as ex:
            LOG.error("Problem adding office: %s: %s", office_name, ex)
            self.session.rollback()

        else:
            return office

    def del_office(self, office_name=None, company_name=None):
        if not office_name or not company_name:
            LOG.error("You must supply office_name and company_name")
            return

        query = self.session.query(Office).filter(Office.name==office_name,
                                                  Company.name==company_name)
        office = query.one_or_none()
        if not office:
            LOG.error("Office doesnt exists: %s", office_name)
            return

        try:
            self.session.delete(office)
            self.session.commit()

        except Exception as ex:
            self.session.rollback()
            LOG.error("Problem deleting company: %s: %s", company_name, ex)

    def get_office(self, office_name=None, company_name=None):
        if not office_name or not company_name:
            LOG.error("You must supply office_name and company_name")
            return

        company = self.get_company(company_name)
        if not company:
            LOG.error("Company does not Exists: %s", company_name)
            return

        office = self.session.query(Office).filter(Office.company==company,
                                                   Office.name==office_name)
        return office.one_or_none()

    def get_offices(self, company_name=None):
        if not company_name:
            LOG.error("You must company_name")
            return

        company = self.get_company(company_name)
        if not company:
            LOG.error("Company does not Exists: %s", company_name)
            return

        return company.offices

    def list_offices(self, company_name='all'):
        if not company_name:
            LOG.error("You must supply company_name")
            return

        if company_name == 'all':
            for office in self.session.query(Office).all():
                print('Company: {:15} => Office: {:10}'.
                      format(office.company.name, office.name))
            return

        company = self.get_company(company_name)
        if not company:
            LOG.error("Company does not Exists: %s", company_name)
            return

        for office in company.offices:
            print('Office in company {} => {}'
                  .format(company_name, office.name))

    def add_group(self, group_name=None, company_name=None, office_name=None):
        # Add a group to company.office
        company = self.get_company(company_name)
        if not company:
            LOG.error("Company does not Exists: %s", company_name)
            return

        office = self.get_office(office_name, company_name=company_name)
        if not office:
            LOG.error("Missing office: %s", office_name)
            return

        for group in company.groups:
            if group.name == group_name:
                LOG.error("Group already exists: %s", group_name)
                return

        try:
            group = Group(name=group_name, company=company, office=office)
            self.session.add(group)
            self.session.commit()

        except Exception as ex:
            self.session.rollback()
            LOG.error("Problem adding group: %s: %s", group_name, ex)

        else:
            return group

    def del_group(self, group_name=None, company_name=None, office_name=None):
        if not office_name or not company_name:
            LOG.error("You must supply office_name and company_name")
            return

        query = self.session.query(Group).filter(Group.name==group_name,
                                                 Office.name==office_name,
                                                 Company.name==company_name)
        group = query.one_or_none()
        if not group:
            LOG.error("Group doesnt exists: %s", group_name)
            return

        try:
            self.session.delete(group)
            self.session.commit()

        except Exception as ex:
            self.session.rollback()
            LOG.error("Problem deleting group: %s: %s", group_name, ex)

    def get_group(self, group_name, company_name=None, office_name=None):
        if not group_name or not company_name:
            LOG.error("You must supply group_name and company_name")
            return

        company = self.get_company(company_name)
        if not company:
            LOG.error("Company does not Exists: %s", company_name)
            return

        office = self.get_office(office_name, company_name=company_name)
        if not office:
            LOG.error("Missing office: %s", office_name)
            return

        for group in company.groups:
            if group.name == group_name:
                return group

    def get_groups(self, company_name=None, office_name=None):
        company = self.get_company(company_name)
        if not company:
            LOG.error("Company does not Exists: %s", company_name)
            return

        office = self.get_office(office_name, company_name=company_name)
        if not office:
            LOG.error("Missing office: %s", office_name)
            return

        return company.groups

    def list_groups(self, company_name='all', office_name='all'):
        if not company_name:
            LOG.error("You must supply company_name")
            return

        if company_name == 'all':
            for group in self.session.query(Group).all():
                print('Company: {:15} : Office: {:10} => Group: {:10}'
                      .format(group.company.name,
                              group.office.name,
                              group.name))
            return

        company = self.get_company(company_name)
        if not company:
            LOG.error("Company does not Exists: %s", company_name)
            return

        office = self.get_office(office_name, company_name=company_name)
        if not office:
            LOG.error("Office does not Exists: %s", office_name)
            return

        for group in office.groups:
            print('Company: {:15} : Office: {:10} => Group: {:10}'
                  .format(group.company.name,
                          group.office.name,
                          group.name))

    def get_hosts(self, company_name=None, office_name=None):
        if not company_name:
            LOG.error("You must supply company_name")
            return

        company = self.get_company(company_name)
        if not company:
            LOG.error("Missing company: %s", company_name)
            return

        office = self.get_office(office_name, company_name=company_name)
        if not office:
            LOG.error("Missing office: %s", office_name)
            return

        return office.hosts

    def get_host(self, hostname, company_name=None, office_name=None):
        for host in self.get_hosts(company_name=company_name, office_name=office_name):
            if host.name == hostname:
                return host

    def add_host(self, hostname=None, company_name=None, office_name=None, group_names=None):
        # Test for existence of company, office, groups
        if not company_name:
            LOG("You must supply company_name")
            return

        company = self.get_company(company_name)
        if not company:
            LOG.error("Missing company: %s", company_name)
            return

        office = self.get_office(office_name, company_name=company_name)
        if not office:
            LOG.error("Missing office: %s", office_name)
            return

        if not group_names:
            LOG.error("Missing group_names!")
            return

        if self.get_host(hostname, company_name=company_name, office_name=office_name):
            LOG.error("Host already exists: %s", hostname)
            return

        # Ensure the group_names are correct
        groups = []
        for grp in office.groups:
            if grp.name in group_names:
                groups.append(grp)
            else:
                LOG.error("Missing group: %s", grp.name)
                return

        try:
            # We've identified company, office, groups: We can attempt to add host.
            host = Host(name=hostname, company=company, office=office, groups=groups)
            self.session.add(host)
            self.session.commit()

        except Exception as ex:
            self.session.rollback()
            LOG.error("Problem adding host: %s", ex)

        else:
            return host

    def del_host(self, hostname=None, company_name=None, office_name=None):
        if not office_name or not company_name:
            LOG.error("You must supply office_name and company_name")
            return

        query = self.session.query(Host).filter(Host.name==hostname,
                                                Office.name==office_name,
                                                Company.name==company_name)
        host = query.one_or_none()
        if not host:
            LOG.error("Host doesnt exists: %s", hostname)
            return

        try:
            self.session.delete(host)
            self.session.commit()

        except Exception as ex:
            self.session.rollback()
            LOG.error("Problem deleting host: %s: %s", hostname, ex)
