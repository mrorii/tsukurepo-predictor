# tsukurepo-predictor

## Crawl cookpad recipes

You will first need to crawl Cookpad and extract recipes.
Refer to https://github.com/mrorii/cookbot for an example Cookpad crawler.
We assume that the recipes are saved in a file where each line
is a JSON-encoded item representing a single recipe.
An example recipe looks like the following:

    {
        "id": 5678,
        "name": "mokomichi's olive oil carbonara"
        "description": "foobar",
        "category": 11,
        "categories": [177, 11, 589, 830]
        "ingredients": ["olive oil", "fettucine", "egg", "bacon", "black pepper"],
        "author": 1234,
        "report_count": 10,
        "published_date": '13/07/29',
        "image_main", "http://img.cpcdn.com/recipes/157692/280/bf45e2954bed59b344a315e0ed4b5a9f.jpg",
        "images_instruction": [
            "http://img.cpcdn.com/steps/11985786/136/6e389fe8b3d970740069a6836f1f5a1e.jpg",
            "http://img.cpcdn.com/steps/11985787/136/85c617f79cf1037a0646076cef827518.jpg",
        ]
    }

In the steps below, we assume that the file containing these
JSON-encoded items is saved as `cookpad.json`.

## Requirements

You need to have Python 2.7, [MeCab](https://code.google.com/p/mecab/),
and a corresponding MeCab python binding installed.

Install additional dependencies via `pip install -r requirements.txt`

## Usage

### Split the data

Split the data into train, dev, and test set.
The optional parameter `threshold` specifies the threshold
(on the number of tsukurepos) used to determine
whether a recipe should be labeled as positive or negative.

    mkdir -p data
    python split_data.py --threshold 10 cookpad.json data

### Train and test

    python classify.py data --pr_curve pr.png > results.txt

### OPTIONAL: Inspect frequently used ingredients

    python inspect_ingredients.py --n 1000 cookpad.json > ingredient_top.txt

### OPTIONAL: Plot a histogram of tsukurepo counts

    python inspect_report_count.py --xmax 200 cookpad.json tsukurepo_counts.png

### OPTIONAL: Pickle ingredient-ID mapping

    python generate_ingredient_mapping.py --threshold 10 cookpad.json ingredient_mapping.pkl

### OPTIONAL: Generate an ingredient complement network

    python generate_ingredient_network.py cookpad.json ingredient_mapping.pkl \
                                          ingredient_complement_network.pkl

### OPTIONAL: Extract the backbone from the network

    python extract_network_backbone.py --alpha 0.01 \
                                       ingredient_complement_network.pkl \
                                       ingredient_complement_backbone.gexf

