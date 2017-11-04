import os
# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))
import sys
sys.path.insert(0, "/home/ec2-user/bin/hitch_backend")
from webhandler import app as application
