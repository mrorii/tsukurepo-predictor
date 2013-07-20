# tsukurepo-predictor

## Crawl cookpad recipes

You will first need to crawl Cookpad and save the recipes.
Refer to https://github.com/mrorii/cookbot for an example Cookpad crawler.
We assume that the recipes are saved in a file where each line is a JSON-encoded item representing a single recipe.
An example recipe looks like the following:

    {
        "category": 11,
        "description": "",
        "ingredients": ["olive oil", "fettucine", "egg", "bacon", "black pepper"],
        "author": 1234,
        "report_count": 10,
        "comment_count": 1,
        "id": 5678,
        "categories": [177, 10, 523],
        "name": "mokomichi's olive oil carbonara"
    }

In the steps below, we assume that the file is named `cookpad.json`.

## Inspect frequently used ingredients

    python inspect_ingredients.py --n 1000 cookpad.json > ingredient_top.txt

## Plot a histogram of tsukurepo counts

    python inspect_report_count.py --xmax 200 cookpad.json tsukurepo_counts.png

## Pickle ingredient-ID mapping

    python generate_ingredient_mapping.py --threshold 10 cookpad.json ingredient_mapping.pkl

## Generate an ingredient complement network

    python generate_ingredient_network.py cookpad.json ingredient_mapping.pkl ingredient_complement_network.pkl

## Extract the backbone from the network

    python extract_network_backbone.py --alpha 0.01 ingredient_complement_network.pkl ingredient_complement_backbone.gexf

## Split data

Split the data into train, dev, and test set.

    mkdir split-data
    python split_data.py --threshold 10 cookpad.json split-data

## Train and test

    python classify.py split-data --pr_curve pr.png
