import pkg_resources
version = pkg_resources.require('fonsim')[0].version

print(f'=== FONSIM {version} ===')
print('NOTICE: The FONSim package currently resides in the beta stage. '
      'Some features do not work fully yet and you may encounter bugs. '
      'Several features and implementations are still in development '
      'and may change in the coming months. '
      'Therefore it is suggested, for later reference, '
      'to note in your script the used FONSim version. '
      'We look forward to your feedback, and thank you for your understanding. '
      'Overview of all FONSim versions: '
      'https://fonsim.readthedocs.io/en/latest/release_log.html. '
      )
print()
