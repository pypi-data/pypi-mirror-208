from os import path
import pkg_resources

# List of compatible firmware builds
compat_fw = 576
cli_ver_major = 2
cli_ver_minor = 0
cli_ver_patch = 0

# Official release name
distribution = pkg_resources.get_distribution("moku")
release = distribution.version
location = path.join(distribution.location, "moku")
