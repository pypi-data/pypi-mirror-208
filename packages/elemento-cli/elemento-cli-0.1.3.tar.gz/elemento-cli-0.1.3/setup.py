# #******************************************************************************#
# # Copyright(c) 2019-2023, Elemento srl, All rights reserved                    #
# # Author: Elemento srl                                                         #
# # Contributors are mentioned in the code where appropriate.                    #
# # Permission to use and modify this software and its documentation strictly    #
# # for personal purposes is hereby granted without fee,                         #
# # provided that the above copyright notice appears in all copies               #
# # and that both the copyright notice and this permission notice appear in the  #
# # supporting documentation.                                                    #
# # Modifications to this work are allowed for personal use.                     #
# # Such modifications have to be licensed under a                               #
# # Creative Commons BY-NC-ND 4.0 International License available at             #
# # http://creativecommons.org/licenses/by-nc-nd/4.0/ and have to be made        #
# # available to the Elemento user community                                     #
# # through the original distribution channels.                                  #
# # The authors make no claims about the suitability                             #
# # of this software for any purpose.                                            #
# # It is provided "as is" without express or implied warranty.                  #
# #******************************************************************************#
#
# #------------------------------------------------------------------------------#
# #elemento-monorepo-server                                                      #
# #Authors:                                                                      #
# #- Gabriele Gaetano Fronze' (gfronze at elemento.cloud)                        #
# #- Filippo Valle (fvalle at elemento.cloud)                                    #
# #------------------------------------------------------------------------------#
#

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="elemento-cli",
    version="0.1.3",
    author="Elemento",
    author_email="hello@elemento.cloud",
    description="CLI for Elemento",
    license="GPL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://elemento.cloud",
    packages=setuptools.find_packages(),
    include_package_data=True,
    scripts=['elemento.py', 'elemento', "headers.py", "betterprinttable.py"],
    package_data={
        ".":["headers.py"],
        "ecd":["*"],
        "common": ["*"],
        "handlers": ["*.py"]},
    install_requires = ["argparse", 
        "argcomplete", 
        "tabulate", 
        "si_prefix",
        "jsonpickle",
        "requests",
        "pwinput",
        "urllib3==1.26.6"],
    python_requires='>=3.9',
)
