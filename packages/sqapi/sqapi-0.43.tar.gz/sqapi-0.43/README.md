# SQAPI

`sqapi` is a python package that simplifies interactions with the 
[SQUIDLE+ API](https://squidle.org/api/help?template=api_help_page.html).
It can be used to integrate automated labelling from machine learning algorithms and plenty other cool things.

### Installation
To install the `sqapi` module, you can use `pip`
```shell
pip install sqapi 
```

### What is this?
The `sqapi` module helps to build the `HTTP` requests that are sent to the [SQUIDLE+](squidle.org) `API`. These are 
`GET`, `POST`, `PATCH` or `DELETE` requests. Setting `verbosity=2` on the `sqapi` module will print the `HTTP` 
requests that are being made.

`sqapi` takes care of authentication, and simplifies the creation of API queries. 
For example:

```python
from sqapi.api import SQAPI

sqapi = SQAPI(host=<HOST>,api_key=<API_KEY>, verbosity=2)  # instantiate the sqapi module
r=sqapi.get(<ENDPOINT>)              # define a get request using a specific endpoint
r.filter(<NAME>,<OPERATORE>,<VALUE>) # define a filter to compare a property with a value using an operator
data = r.execute().json()            # perform the request & return result as JSON dict (don't set template)
```

For more information about structuring queries, check out the [Making API queries](https://squidle.org/api/help?template=api_help_page.html#api_query)
section of the SQ+ API documentation page.

Instantiating `sqapi` without an API key argument will prompt for a user login, i.e.:
```python
sqapi = SQAPI(host=<HOST>, verbosity=2)  # instantiate the sqapi module
```

You can also use it to apply built-in templates to the data that comes out of the API:
```python
r.template(<TEMPLATE>)               # format the output of the request using an inbuilt HTML template
html = r.execute().text              # perform the request & return result as text (eg: for html)
```

> **IMPORTANT:** in order to proceed, you will need a user account on [SQUIDLE+](https://squidle.org). You will also 
> need to activate your API key.

## Examples
### Creating queries
This is by no means an extensive list of possible API queries. The API is extensive and the models are documented
[here](https://squidle.org/api/help?template=api_help_page.html) and the creation of queries is documented 
[here](https://squidle.org/api/help?template=api_help_page.html#api_query). `SQAPI` enables a convenient mechanism 
for creating these queries inside of Python. For example, a basic API query to list all the annotations that have valid 
labels starting with 'ecklonia' within a spatially constrained bounding box would be:
```json
{
   "filters": [
      {
         "name": "label",
         "op": "has",
         "val": {
            "name": "name",
            "op": "ilike",
            "val": "ecklonia%"
         }
      },
      {
         "name": "point",
         "op": "has",
         "val": {
            "name": "media",
            "op": "has",
            "val": {
               "name": "poses",
               "op": "any",
               "val": {
                  "name": "geom",
                  "op": "geo_in_bbox",
                  "val": [
                     {
                        "lat": -32.020013585799155,
                        "lon": 115.49980113118502
                     },
                     {
                        "lat": -32.01995006531625,
                        "lon": 115.49987604949759
                     }
                  ]
               }
            }
         }
      }
   ]
}
```
The result of that query can be accessed dynamically through [this link](https://squidle.org/api/annotation?template=models/annotation/list_thumbnails.html&q={"filters":[{"name":"point","op":"has","val":{"name":"has_xy","op":"eq","val":true}},{"name":"point","op":"has","val":{"name":"media","op":"has","val":{"name":"poses","op":"any","val":{"name":"geom","op":"geo_in_bbox","val":[{"lat":-32.020013585799155,"lon":115.49980113118502},{"lat":-32.01995006531625,"lon":115.49987604949759}]}}}}]}).
Note with a logged in browser session, that link will extract cropped thumbnails around each annotation, but without logging in,
you'll just see a thumbnail the whole image associated with that annotation.
The Python code required to build that query could be something like:
```python
from sqapi.api import SQAPI, query_filter as qf
api = SQAPI(host="https://squidle.org", )   # optionally pass in api_key to avoid log in prompt
r = api.get("/api/annotation")
r.filter("label", "has", qf("name","ilike","ecklonia%"))   # filter for label name, % here is a wildcard matching anything
bbox = [{"lat": -32.020013585799155,"lon": 115.49980113118502},{"lat": -32.01995006531625,"lon": 115.49987604949759}]
r.filter("point", "has", qf("media", "has", qf("poses", "any", qf("geom", "geo_in_bbox", bbox))))  # filter within bounding box
```

### Random annotation BOT
This is an example of an automated labelling bot that selects random class labels to assign to points.
It provides terrible suggestions, however it provides a simple boiler-plate example of how to integrate a
Machine Learning algorithm for label suggestions.

Set up the environment and a mini project. Creating a virtual environment, is optional, but recommended.
```shell
mkdir sqbot_demo && cd sqbot_demo   # make a directory
virtualenv -p python3 env           # create a virtual environment
source env/bin/activate             # activate it
pip install sqapi                   # install sqapi
```

#### 1. Create a bot class
In this example, we'll create an automated classifier that suggests random label suggestions for an annotation_set. 
It uses the `Annotator` class from the `sqapi.annotate` module, which does most of the heavy-lifting. The implementation
of the classifier is relatively straight forward.
In your project directory, create a file named `run_bot.py`:

```python
# run_bot.py
import random
from sqapi.annotate import Annotator
from sqapi.helpers import cli_init
from sqapi.media import SQMediaObject


class RandoBOT(Annotator):
    """
    An example of an automated labelling bot that selects random class labels to assign to points.
    It provides terrible suggestions, however it provides a simple boiler-plate example of how to integrate a
    Machine Learning algorithm for label suggestions.
    """       
    def classify_point(self, mediaobj: SQMediaObject, x, y, t):
       # This method is used to generate a point prediction
       # TODO: use the mediaobj, x and y point position to generate a real classifier_code and prob
       classifier_code = random.randint(0,3)  # get a random code (0-3) to match with label_map_file
       prob = round(random.random(), 2)  # generate a random probability
       return classifier_code, prob


if __name__ == '__main__':
    # Instantiate the bot from the default CLI arguments
    bot = cli_init(RandoBOT)  
    
    # Build the annotation_set query (this can be far more complex, see examples for more)
    annotation_set_id = input("Enter the ID of the annotation_set that you want to classify: ")
    r = bot.sqapi.get("/api/annotation_set").filter(name="id", op="eq", val=annotation_set_id)  
    
    # Run the classifier with the annotation_set query
    bot.start(r)
```

The `create_parser` method is a convenience tool that allows you to build a command line parser from the  
signature of the `__init__` methods for the RandoBot class and all inherited base classes (ie: `Annotator`).

This allows you to pass arguments from the command line, and helps to show how to use it:
```shell
# from the command line, run:
python run_bot.py --help
```

It will show you all the required parameters from the base class `Annotator` as well as any extra arguments added to the 
`__init__` method of the `RandoBot` class. Parameter descriptions come from the comment block.

It is necessary to build an `annotation_set` query that will tell the `RandoBot` instance which datasets to classify.
The example above prompts for an `annotation_set_id`, however, it is possible to define much more complex queries to run
the automated classifier. 

```python
from sqapi.api import query_filter as qf
r = bot.sqapi.get("/api/annotation_set")  # create the query, as above

# Only return annotation_sets that do not already have suggestions from this user
# This is necessary to avoid repeating suggestions each time the process runs
r.filter_not(qf("children", "any", val=qf("user_id", "eq", bot.sqapi.current_user.get("id"))))

# Filter annotation sets based on ID, as above
r.filter("id", "eq", ANNOTATION_SET_ID)

# Constrain date ranges to annotation_sets ceated after a specific date
r.filter("created_at", "gt", AFTER_DATE)

# Filter annotation_sets based on a user group
r.filter("usergroups", "any", val=qf("id", "eq", USER_GROUP_ID))

# Filter annotation_sets based on the users' affiliation
r.filter("user", "has", val=qf("affiliations_usergroups", "any", val=qf("group_id", "eq", AFFILIATION_GROUP_ID)))

# Filter annotation_sets based on the number of images in the media_collection
r.filter("media_count", "lte", MEDIA_COUNT_MAX)
```

In order to add these additional parameters, you can add arguments to the command-line parser.
For examples on how to do that, checkout the [examples](https://bitbucket.org/ariell/pysq/src/master/examples/) directory.

#### 2. Create a Label Mapper File
Before you run it, you also need to create a label map file to pass into the `--label_map_file` argument. 
This maps the outputs from your classifier to real class labels in the system.

In your project directory, create a file named `rando_bot_label_map.json` 
with the following content:
```json
[
  [{"name":"vocab_elements","op":"any","val":{"name":"key","op":"eq","val":"214344"}}],
  [{"name":"vocab_elements","op":"any","val":{"name":"key","op":"eq","val":"1839"}}],
  [{"name":"vocab_elements","op":"any","val":{"name":"key","op":"eq","val":"82001000"}}],
  null 
]
```
The example above, shows a label_map file for a classifier that outputs an integer value classifier code, where `0-2` 
would be a Label class that uses the vocab_element to lookup a Label across the Label Schemes. `3` would output nothing, 
which won't be submitted.

Note: if your classifier outputs a string code instead of an integer, you can define a similar 
mapping file using a dict lookup, like:
```json
{
  "ECK": [{"name":"vocab_elements","op":"any","val":{"name":"key","op":"eq","val":"214344"}}],
  "ASC": [{"name":"vocab_elements","op":"any","val":{"name":"key","op":"eq","val":"1839"}}],
  "SUB": [{"name":"vocab_elements","op":"any","val":{"name":"key","op":"eq","val":"82001000"}}]
}
```
That will attempt to map the classifier outputs `ECK`, `ASC` and `SUB` to a Label in SQ+.

#### 3. Run your bot
Now you're ready to run your classifier `RandoBot`, by simply executing this from the command line:
```shell
# bash
# Install sqapi module using pip
pip install sqapi
# See help to show all arguments
python run_bot.py --help
# Run automated labeler algorithm with selected arguments
python run_bot.py --host https://staging.squidle.org --label_map_file rando_bot_label_map.json --prob_thresh 0.5 --email_results
```

This will prompt you for a annotation_set id and attempt to provide automated suggestions on the labels it contains 
using random class allocations and probabilities. It will only submit suggestions with a probability > 0.5 and 
it will run once (as defined by the `--poll_delay=-1` parameter) 
and it will send an email to the owner the annotation_set once complete.

Now all that's left is for you to make the labels and probabilities real, and bob's your uncle,
you've made an automated classifier.

The [examples](https://bitbucket.org/ariell/pysq/src/master/examples/) directory has some examples that you can use and/or adapt for 
your purposes. Specifically with regard to classifiers:

1. **[demo_randobot.py](https://bitbucket.org/ariell/pysq/src/master/examples/bots/demo_randobot.py)**: similar to example above, but with additional command line 
   arguments for filtering annotation_sets and to keep running as a service.
2. **[keras_cnn_bot.py](https://bitbucket.org/ariell/pysq/src/master/examples/bots/keras_cnn_bot.py)**: a real classifier that uses a tensor_flow/keras model for 
   classifying points in images. The class received a number of additional parameters that can all be passed in as 
   command line arguments. Run `python keras_cnn_bot.py --help` for more information. This shows an example of how to 
   include additional model-specific arguments along with other parameters, as well as how to process the images and 
   for a real classifier.

