<a name="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]







<!-- About -->
<div align="center">

<h3 align="center">Python Linqex</h3>

<p align="center">

The linq module in C# has been adapted for python with some modifications.

<a href="https://github.com/TahsinCr/python-linqex/blob/master/CHANGELOG.md">Changelog</a>
 · 
<a href="https://github.com/TahsinCr/python-linqex/issues">Report Bug</a>
 · 
<a href="https://github.com/TahsinCr/python-linqex/issues">Request Feature</a>
 
</p>

</div>



<!-- ABOUT THE PROJECT -->

##  About The Project

Provides simple to use LINQ features to Python 3.x.



###  Built With

* [![Python][Python]][Python-url]

<br>


<!-- GETTING STARTED -->

##  Getting Started

To get a local copy up and running follow these simple example steps.

###  Prerequisites

Does not require any prerequisites

###  Installation

1. Clone the repo
```sh
git clone https://github.com/TahsinCr/python-linqex.git
```

2. Install PIP packages
```sh
pip install linqex
```


<br>



<!-- USAGE EXAMPLES -->

##  Usage

Let's have different customers. Let's choose the male ones among these customers. For this:
```python
from linqex.linq import Enumerable
customersList = [
    {'name' : 'Jonh', 'age' : 25, 'gender': 'male'},
    {'name' : 'Emma', 'age' : 44, 'gender': 'female'},
    {'name' : 'Steve', 'age' : 17, 'gender': 'male'}
]

customersEnumerable = Enumerable(customersList)

# to select only male ones:
customersMaleEnumerable = customersEnumerable.Where(lambda key, value: value['gender'] == 'male')

for customer in customersMaleEnumerable.ToList:
    print(customer)

```
Output
```
{'name' : 'Jonh', 'age' : 25, 'gender': 'male'}
{'name' : 'Steve', 'age' : 17, 'gender': 'male'}
```

<br>

Let's develop the example we wrote above a bit further:
```python
from typing import Literal
from linqex.linq import Enumerable

MALE = "MALE"
FEMALE = "FEMALE"

class Customer:
    def __init__(self, id:int, name:str, age:int, gender:Literal["MALE","FEMALE"]):
        self.id = id
        self.name = name
        self.age = age
        self.gender = gender


customerList = [
    Customer(1, "Ava", 32, MALE),
    Customer(2, "Alex", 19, MALE),
    Customer(3, "Amelia", 22, FEMALE),
    Customer(4, "Arnold", 43, MALE),
    Customer(5, "Eric", 55, MALE),
    Customer(6, "Lily", 12, FEMALE),
    Customer(7, "Jessia", 32, MALE),
    Customer(8, "William", 19, MALE),
    Customer(9, "Emily", 22, FEMALE),
    Customer(10, "Mateo", 43, MALE),
    Customer(11, "Antony", 55, MALE),
    Customer(12, "Mia", 12, FEMALE)
]

customerEnumerable = Enumerable.List(customerList)

# to select only male ones:
customersMaleEnumerable = customerEnumerable.Where(lambda customer: customer.gender == MALE)

for customer in customersMaleEnumerable.ToList:
    print(customer.__dict__)

```
Output
```
{'id': 1, 'name': 'Ava', 'age': 32, 'gender': 'MALE'}
{'id': 2, 'name': 'Alex', 'age': 19, 'gender': 'MALE'}
{'id': 4, 'name': 'Arnold', 'age': 43, 'gender': 'MALE'}
{'id': 5, 'name': 'Eric', 'age': 55, 'gender': 'MALE'}
{'id': 7, 'name': 'Jessia', 'age': 32, 'gender': 'MALE'}
{'id': 8, 'name': 'William', 'age': 19, 'gender': 'MALE'}
{'id': 10, 'name': 'Mateo', 'age': 43, 'gender': 'MALE'}
{'id': 11, 'name': 'Antony', 'age': 55, 'gender': 'MALE'}
```

_For more examples, please refer to the [Documentation](https://github.com/TahsinCr/python-linqex/wiki)_




<!-- LICENSE -->

##  License

Distributed under the MIT License. See `LICENSE.txt` for more information.


<br>





<!-- CONTACT -->

##  Contact

Tahsin Çirkin - [@TahsinCrs](https://twitter.com/TahsinCrs) - TahsinCr@outlook.com

Project Link: [https://github.com/TahsinCr/python-linqex](https://github.com/TahsinCr/python-linqex)








<!-- LINKS & IMAGES URL -->

[contributors-shield]: https://img.shields.io/github/contributors/TahsinCr/python-linqex.svg?style=for-the-badge

[contributors-url]: https://github.com/TahsinCr/python-linqex/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/TahsinCr/python-linqex.svg?style=for-the-badge

[forks-url]: https://github.com/TahsinCr/python-linqex/network/members

[stars-shield]: https://img.shields.io/github/stars/TahsinCr/python-linqex.svg?style=for-the-badge

[stars-url]: https://github.com/TahsinCr/python-linqex/stargazers

[issues-shield]: https://img.shields.io/github/issues/TahsinCr/python-linqex.svg?style=for-the-badge

[issues-url]: https://github.com/TahsinCr/python-linqex/issues

[license-shield]: https://img.shields.io/github/license/TahsinCr/python-linqex.svg?style=for-the-badge

[license-url]: https://img.shields.io/github/forks/TahsinCr/python-linqex?style=flat-square

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555

[linkedin-url]: https://linkedin.com/in/TahsinCr

[Python]: https://img.shields.io/pypi/pyversions/linqex?style=flat-square

[Python-url]: https://pypi.org/project/linqex