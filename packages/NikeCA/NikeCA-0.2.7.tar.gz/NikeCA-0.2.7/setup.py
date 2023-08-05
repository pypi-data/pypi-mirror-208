from setuptools import setup

with open("README.md", "r") as fh:
	long_description = fh.read()


setup(
	name='NikeCA',
	version='0.2.7',
	description='Standardize and Automate processes',
	py_modules=[
		"__init__",
		"_BuildSearchQuery",
		"_GitHub",
		"_SearchFiles",
		"_SnowflakeData",
		"_SnowflakeDependencies",
		"_SnowflakePull",
		"_QA",
		"Dashboards/__init__",
		"Dashboards/Dashboards",
		"Dashboards/InclusionExclusion/InclusionExclusion",
		"Dashboards/InclusionExclusion/__init__",
		"Dashboards/IMP/IMP",
		"Dashboards/IMP/__init__",
		"Dashboards/Telemetry/ProductUsage",
		"Dashboards/Telemetry/Telemetry",
		"Dashboards/Telemetry/__init__",
		"NikeCA",
		"NikeSF",
		"NikeQA"
	],
	package_dir={'': 'src'},
	classifiers=[
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.11",
		"License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
		"Operating System :: OS Independent",
	],
	long_description=long_description,
	long_description_content_type="text/markdown",
	install_requires=[
		"wheel",
		"asn1crypto==1.5.1",
		"certifi==2022.12.7",
		"cffi==1.15.1",
		"charset-normalizer==2.1.1",
		"cryptography==39.0.1",
		"databricks==0.2",
		"databricks-sql==1.0.0",
		"databricks-sql-connector==2.2.1",
		"filelock==3.9.0",
		"gitdb==4.0.10",
		"github3.py==3.2.0",
		"GitPython==3.1.31",
		"greenlet==2.0.2",
		"httpx==0.23.3",
		"idna==3.4",
		"jupyter-contrib-core==0.4.2",
		"jupyter-contrib-nbextensions==0.7.0",
		"jupyter-events==0.6.3",
		"jupyter-highlight-selected-word==0.2.0",
		"jupyter-nbextensions-configurator==0.6.1",
		"jupyter-ydoc==0.2.2",
		"jupyter_client==8.0.3",
		"jupyter_core==5.2.0",
		"jupyter_server==2.3.0",
		"jupyter_server_fileid==0.8.0",
		"jupyter_server_terminals==0.4.4",
		"jupyter_server_ydoc==0.6.1",
		"jupyterlab==3.6.1",
		"jupyterlab-pygments==0.2.2",
		"jupyterlab_server==2.19.0",
		"links-from-link-header==0.1.0",
		"lz4==4.3.2",
		"numpy==1.23.4",
		"oauthlib==3.2.2",
		"oscrypto==1.3.0",
		"pandas==1.5.3",
		"polars==0.17.9",
		"pyarrow==10.0.1",
		"pycparser==2.21",
		"pycryptodomex==3.17",
		"PyGithub==1.58.0",
		"PyJWT==2.6.0",
		"pyOpenSSL==23.0.0",
		"pyspark==3.3.2",
		"pystache==0.6.0",
		"python-dateutil==2.8.2",
		"pytz==2022.7.1",
		"requests==2.28.2",
		"six==1.16.0",
		"smmap==5.0.0",
		"snowflake-connector-python==3.0.0",
		"snowflake-sqlalchemy==1.4.6",
		"SQLAlchemy==1.4.46",
		"thrift==0.16.0",
		"typing_extensions==4.5.0",
		"urllib3==1.26.14",
		"xcrun==0.4",
		"configparser~=5.3.0",
	],
)
