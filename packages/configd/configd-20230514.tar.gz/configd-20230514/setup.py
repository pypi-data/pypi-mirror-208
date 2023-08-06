import time
from distutils.core import setup

setup(
  name = 'configd',
  module = ['configd'],
  version = time.strftime('%Y%m%d'),
  description = 'Strongly consistent store for small amount of config data - GET/PUT over HTTPS.',
  long_description = 'Uses Paxos for strong consistency, fault tolerance, high availability, and mTLS for write authentication.',
  author = 'Bhupendra Singh',
  author_email = 'bhsingh@gmail.com',
  url = 'https://github.com/magicray/configd'
)
