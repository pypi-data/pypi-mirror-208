<br>
<p align="center"><img width="400" alt="Logo" src="https://raw.githubusercontent.com/CorentinMre/FreeMobileConso/main/images/logoV2.png"></a></p>

<br/>


<h2 style="font-family: sans-serif; font-weight: normal;" align="center">An API for get<strong> Free mobile </strong>Consommation</h2>


<br/>


[![pypi version](https://img.shields.io/pypi/v/FreeMobileConso.svg)](https://pypi.org/project/FreeMobileConso/)
[![python version](https://img.shields.io/pypi/pyversions/FreeMobileConso.svg)](https://pypi.org/project/FreeMobileConso/)
[![license](https://img.shields.io/pypi/l/FreeMobileConso.svg)](https://pypi.org/project/FreeMobileConso/)

## Description
A python API for get your consommation of your Free mobile account


## Dependencies

- requests
- bs4

## Usage


- `pip3 install FreeMobileConso`

Here is an example script:

```python

import FreeMobileConso


client = FreeMobileConso.Client(
                        "<identifiant>",
                        "<password>"
                        )


conso = client.consommation()

################################################################################

print("Acount name: " + conso.nameAcount)
print("Identifier: " + conso.identifier)
print("Number: " + conso.number)
print("Total excluding package: " + conso.totalExcludingPackage)

################################################################################
print("\n\n\nLocal: ")

print("Internet consumption in my country: " + conso.local.internet.conso)
print("Internet plan mobile in my country: " + conso.local.internet.total)
print("Internet Remaining plan in my country: " + conso.local.internet.remaining)
print("Excluding package in my country (Internet): " + conso.local.internet.excludingPackage)
print("Carbon footprint in my country: " + conso.local.internet.carbonFootprint)

print("Call consumption in my country: " + conso.local.call.conso)
print("Call plan mobile in my country: " + conso.local.call.total)
print("Call plan in my country: " + conso.local.call.callToMyCountry)
print("Call plan International: " + conso.local.call.callToInternational)
print("Excluding package in my country (Call): " + conso.local.call.excludingPackage)

print("SMS consumption in my country: " + conso.local.sms.conso)
print("SMS plan mobile in my country: " + conso.local.sms.total)
print("Max nb os SMS in my plan in my country: " + conso.local.sms.maxNbSMS)
print("Nb of SMS in my country: " + conso.local.sms.nbSMS)
print("Excluding package in my country (SMS): " + conso.local.sms.excludingPackage)

print("MMS consumption in my country: " + conso.local.mms.conso)
print("MMS plan mobile in my country: " + conso.local.mms.total)
print("Max nb os MMS in my plan in my country: " + conso.local.mms.maxNbMMS)
print("Nb of MMS in my country: " + conso.local.mms.nbMMS)
print("Excluding package in my country (MMS): " + conso.local.mms.excludingPackage)

################################################################################
print("\n\n\nRoaming: ")

print("Internet consumption not in my country: " + conso.roaming.internet.conso)
print("Internet plan mobile not in my country: " + conso.roaming.internet.total)
print("Internet Remaining plan not in my country: " + conso.roaming.internet.remaining)
print("Excluding package not in my country (Internet): " + conso.roaming.internet.excludingPackage)

print("Call consumption not in my country: " + conso.roaming.call.conso)
print("Call plan mobile not in my country: " + conso.roaming.call.total)
print("Call plan in my not country: " + conso.roaming.call.callToMyCountry)
print("Call plan International: " + conso.roaming.call.callToInternational)
print("Excluding package not in my country (Call): " + conso.roaming.call.excludingPackage)

print("SMS consumption not in my country: " + conso.roaming.sms.conso)
print("SMS plan mobile not in my country: " + conso.roaming.sms.total)
print("Max nb os SMS not in my plan in my country: " + conso.roaming.sms.maxNbSMS)
print("Nb of SMS not in my country: " + conso.roaming.sms.nbSMS)
print("Excluding package not in my country (SMS): " + conso.roaming.sms.excludingPackage)

print("MMS consumption not in my country: " + conso.roaming.mms.conso)
print("MMS plan mobile not in my country: " + conso.roaming.mms.total)
print("Max nb os MMS not in my plan in my country: " + conso.roaming.mms.maxNbMMS)
print("Nb of MMS not in my country: " + conso.roaming.mms.nbMMS)
print("Excluding package not in my country (MMS): " + conso.roaming.mms.excludingPackage)

```


## LICENSE

Copyright (c) 2022 CorentinMre

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
