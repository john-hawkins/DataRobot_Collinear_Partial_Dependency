
Collinear Feature Partial Dependency
=====================================

```
STATUS: First Functional Version

TODO: Extend collinear function support beyond difference
```

This project demonstrates a method for generating partial dependency analysis when your 
data contains fields that are perfectly collinear. In other words they have been derived
from each other. 

This initial implementation will deal with difference fields only.
For example, your data contains your product price, a competing products price and the
difference between these prices.

The idea is to conduct the partial dependence in such a way that the relationship is conserved
yet you are still able to understand how much the difference itself is driving the performance
of the model.


## Dependencies
 
You will need a DataRobot account and access to a dedicated prediction server.

You will need the python batch scoring script (used to score the variations efficiently).

```
pip install -U datarobot_batch_scoring
```

You will also need a bunch of python libraries, including the DataRobot API

```
pip install numpy
pip install pandas
pip install datarobot
```

You will need create the [CONFIG](config.yml.example) file and fill in the required details from the deployed model.

We provide an example you can copy and then modify:

```
cp config.yml.example config.yml
vi config.yml
```

## About

The core functions that create the partial dependencies are found 
inside the file [PartialDependency.py](src/PartialDependency.py) 

These functions are used by the example script and the web application example.

## Caveats

Currently the implementation only works for difference fields and requires that the data contain
both the two original fields, and that all three are used by the DataRobot model.

## Usage

### Scripts

The script [Example.py](Example.py) Shows you how to create the partial dependency in a standalone python script.

This script will generate a plot like the one below.
 
![Product price difference partial dependency](scripts/Example.png "Product price difference partial dependency" )


### Application

The file [app.py](app.py) and the contents of the [templates](templates) directory is a python flask 
web application you can use to generate partial dependency plots for an uploaded data set.

It will store the plots generated in the folder [static](static) so that they do not need to be re-generated.

An example of the reuslts page is show below:

![Product price difference partial dependency](statis/screen_shot.png "Product price difference partial dependency" )


To run:

```
python app.py
```

Then follow the prompts.

