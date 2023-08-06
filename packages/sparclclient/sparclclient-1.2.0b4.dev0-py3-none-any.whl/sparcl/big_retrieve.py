from sparcl.client import SparclClient

def tt(num=100):
    print(f'Asking for {num:,d} records.')
    client = SparclClient(url='https://sparc1.datalab.noirlab.edu',
                          verbose=True)
    print(f'Client={client}')
    # Client=(sparclclient:1.2.0b3.dev3,
    #   api:8.0,
    #   https://sparc1.datalab.noirlab.edu/sparc,
    #   verbose=True, connect_timeout=1.1, read_timeout=5400)

    print(f'RUN client.find() for up to {num:,d} records.')
    found = client.find(outfields=['id'], limit=num)

    print(f'Found {found.count:,d} records.')
    #! inc = ['id', 'data_release', 'flux', 'wavelength', 'spectype']
    print('RUN client.retrieve()')
    res = client.retrieve(uuid_list=found.ids, limit=num)

    print(f'Retrieved {res.count:,d} records.')
    return found
