import setuptools
from src import __version__

try:
	from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

	class bdist_wheel(_bdist_wheel):
		def finalize_options(self):
			_bdist_wheel.finalize_options(self)
			self.root_is_pure = False
except ImportError:
	bdist_wheel = None  # type: ignore

with open("README.md", "r") as fh:
	long_description = fh.read()

with open("requirements.txt") as rq:
	required = rq.read().splitlines()

setuptools.setup(
	name="weesocket",
	version=__version__,
	author="Patrik Katrenak",
	author_email="patrik@katryapps.com",
	description="Tiny socket wrapper",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://gitlab.com/katry/weesocket",

	package_dir={"weesocket": "src"},
	include_package_data=True,
	install_requires=required,

	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
		"Operating System :: OS Independent",
		"Natural Language :: English",
	],
	cmdclass={"bdist_wheel": bdist_wheel},
	platforms=["any"],
	python_requires=">=3.10",
)
