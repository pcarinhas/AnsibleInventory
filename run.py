from sqlalchemy import create_engine
from Manager import create_manager


ENGINE = create_engine('sqlite:////tmp/sqlalchemy_example.db', echo=False)
manager = create_manager(ENGINE)
company = manager.get_company('LocoWeed')

manager.add_company('Acme')
company = manager.get_company('Acme')
manager.add_office('Albuequerque', company_name='Acme')
manager.add_office('Austin', company_name='Acme')
manager.add_office('Austin', company_name='Acme')

office = manager.get_office('Albuequerque', company_name='Acme')

manager.add_company('RabbitWorks')
manager.add_office('HoleCity', company_name='RabbitWorks')

office = manager.get_office('Albuequerque', company_name='RabbitWorks')
office = manager.get_office('HoleCity', company_name='RabbitWorks')
offices = manager.get_offices(company_name='RabbitWorks')
manager.list_offices(company_name='Acme')
manager.list_offices()
manager.list_companies()

manager.add_group('miners', company_name='Acme', office_name='Austin')
manager.add_group('accounting', company_name='Acme', office_name='Austin')
manager.add_group('IT', company_name='Acme', office_name='Austin')
group = manager.get_group('miners', company_name='Acme', office_name='Austin')

manager.add_group('IT', company_name='RabbitWorks', office_name='HoleCity')
manager.add_group('rascals', company_name='RabbitWorks', office_name='HoleCity')
groups = manager.get_groups(company_name='RabbitWorks', office_name='HoleCity')
rabbit_groups = [g.name for g in groups]


manager.add_host('bugs', company_name='RabbitWorks', office_name='HoleCity', group_names=rabbit_groups)
manager.add_host('coyote', company_name='RabbitWorks', office_name='HoleCity', group_names=rabbit_groups)
manager.add_host('roadrunner', company_name='RabbitWorks', office_name='HoleCity', group_names=rabbit_groups)

group = manager.get_group('miners', company_name='Acme', office_name='Houston')
groups = manager.get_groups(company_name='Acme', office_name='Austin')
group_names = [g.name for g in groups]

manager.add_host('thor', company_name='Acme', office_name='Austin', group_names=group_names)
host = manager.get_host('thor', company_name='Acme', office_name='Austin')

manager.list_groups()
print '--------------------------------'
manager.list_groups(company_name='Acme', office_name='Austin')
print '--------------------------------'
manager.list_groups(company_name='Acme', office_name='Houston')
manager.dump_hosts_by_group()
