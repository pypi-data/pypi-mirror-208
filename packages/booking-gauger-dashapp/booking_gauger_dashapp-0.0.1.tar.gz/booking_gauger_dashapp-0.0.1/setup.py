from setuptools import setup


setup(name='booking_gauger_dashapp',
      version='0.0.1',
      license='MIT',
      author='Agbleze Linus',
      packages=['booking_gauger_dashapp'],
      description='This package is a web application providing a user interface for \
                    making predictions on number of accommodation days that an online visitor \
                    is likely to book. It is intended to be used with the booking_gauger packaging \
                    which provides the machine learning API for the prediction. The application self-contained \
                    as it runs out of the box using the a saved model developed with booking_gauger',
     zip_safe=False
    )