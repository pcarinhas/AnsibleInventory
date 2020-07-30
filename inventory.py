"""Class model for Company/Office/Group/Host etc.

Host.configs
-----------------------------------------------------------------------------------
Ansible inventory groups will be specified as follows:

    company_group_host_samba_a
    company_group_host_network_b
    company_group_host_samba_user_[a-z]

 The company_group_host part is there to ensure uniqueness across multiple
 companies and offices.

Ansible Call::

   ansible-playbook -l company_office_group -i script.py

So group names will look like company_office_group in inventory --list
This is sensible since otherwise there will be namespace issues.
-----------------------------------------------------------------------------------
"""

from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint

# NOTE: Make sure to import this base into all modules that need Base
Base = declarative_base()
association_table = Table('association', Base.metadata,
                          Column('host_id', Integer, ForeignKey('host.id')),
                          Column('group_id', Integer, ForeignKey('group.id'))
                          )


class Company(Base):
    """Company class is the lowest level."""

    __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    offices = relationship("Office", back_populates="company")
    groups = relationship("Group", back_populates="company")
    hosts = relationship("Host", back_populates="company")


class Office(Base):
    """All companies have an office location. Each host exists in an office."""

    __tablename__ = 'office'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="offices")
    hosts = relationship("Host", back_populates="office")
    groups = relationship("Group", back_populates="office")
    __table_args__ = (UniqueConstraint('name',
                                       'company_id',
                                       name='_company_office_uc'),
                      )


class Group(Base):
    """
    Group (of Hosts) identfies types of hosts in an office.

    * These should be unique by company_office for example.
    * Don't confuse these groups with the Ansible type groups used for inventory
      specification.
    """

    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    # Company ---------------------------------------------------------
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="groups")
    # Office ----------------------------------------------------------
    office_id = Column(Integer, ForeignKey('office.id'), nullable=False)
    office = relationship("Office", back_populates="groups")
    # Unique ----------------------------------------------------------
    __table_args__ = (UniqueConstraint('name',
                                       'company_id',
                                       'office_id',
                                       name='_company_office_group_uc'),
                      )
    # Group can have multiple hosts -----------------------------------
    hosts = relationship(
        "Host",
        secondary=association_table,
        back_populates="groups")


class Host(Base):
    """Hosts will be uniquely grouped by company_office_group groups."""

    __tablename__ = 'host'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="hosts")
    # Office ----------------------------------------------------------
    office_id = Column(Integer, ForeignKey('office.id'), nullable=False)
    office = relationship("Office", back_populates="hosts")
    # Unique ----------------------------------------------------------
    # Host can be in multiple groups to allow different configuraiton sets
    groups = relationship(
        "Group",
        secondary=association_table,
        back_populates="hosts")
    __table_args__ = (UniqueConstraint('name',
                                       'company_id',
                                       'office_id',
                                       name='_company_office_host_uc'),
                      )

# -----------------------------------------------------------------------------
# Samba
# -----------------------------------------------------------------------------
# Each office will have a unique Samba configuration. As such, we should have a
# per office Samba, which means an extra ForeignKey to office.
# Company -> Office -> Host
# Company -> Group -> Host


class SambaGroup(Base):
    """Samba groups that correspond to various Samba levels of access.

    NOTE: These will actually be correspond to Linux groups.
          Example: users, local, marketing, central_texas, company_wide

    These must get created in the Linux system before users can be assigned
    to them. its critical to ensure that they are consistent.

    * Metadata for these groups must be provided in other classes:

      - SambaUser
      - SambaShare
      - SambaConfig

    """

    __tablename__ = 'samba_group'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    office_id = Column(Integer, ForeignKey('office.id'), nullable=False)
    office = relationship("Office")
    gid = Column(Integer, nullable=False, unique=True)
    # Unique ----------------------------------------------------------
    __table_args__ = (UniqueConstraint('name',
                                       'company_id',
                                       'office_id',
                                       name='_company_sambaGroup_uc'),
                      )


class SambaUser(Base):
    """Class to distinguish user, typically Linux users."""

    __tablename__ = 'samba_user'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    smbpasswd = Column(String, nullable=False)
    uid = Column(Integer, nullable=False, unique=True)
    groups = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    office_id = Column(Integer, ForeignKey('office.id'), nullable=False)
    office = relationship("Office")
    # Unique ----------------------------------------------------------
    __table_args__ = (UniqueConstraint('username',
                                       'company_id',
                                       'office_id',
                                       name='_company_sambaUser_uc'),
                      )


class SambaConfig(Base):
    """Configs for the Samba Server, which is a host."""

    __tablename__ = 'samba_config'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    user = Column(String, nullable=False)
    group = Column(String, nullable=False)
    interfaces = Column(String, nullable=False)
    hosts_allow = Column(String, nullable=False)
    local_master = Column(String, nullable=False)
    preferred_master = Column(String, nullable=False)
    socket_options = Column(String)
    # NOTE: Add/Fix this constraint


class SambaShare(Base):
    """Shares on Samba Server.

    Shares must provide metadata for themselves like:

    -- Required --
    * name
    * label
    * path (share path)

    -- File and Folder Creation  --
    * force_user
    * force_group
    * create_mask
    * force_create_mode
    * directory_mask
    * force_directory_mode

    # Security
    * public
    * browseable
    * valid_users: list of valid users or @groups
    * write_list: list of valid users or @groups

    """

    __tablename__ = 'samba_share'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    name = Column(String, nullable=False, unique=True)
    label = Column(String, nullable=False, unique=True)
    group = Column(String, nullable=False, unique=True)
    path = Column(String, nullable=False, unique=True)

    # TODO: fill in all other params
