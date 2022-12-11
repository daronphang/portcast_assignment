import unittest
from portcast_app import create_app

# To change accordingly when running in dev/prod
app = create_app('DEFAULT')


@app.cli.command()
def testing():
    tests = unittest.TestLoader().discover('tests')    # start directory
    unittest.TextTestRunner(verbosity=2).run(tests)