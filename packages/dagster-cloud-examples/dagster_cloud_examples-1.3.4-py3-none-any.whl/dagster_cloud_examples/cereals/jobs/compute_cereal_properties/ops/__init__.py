import csv

import requests
from dagster import op


@op
def download_cereals():
    response = requests.get("https://docs.dagster.io/assets/cereal.csv")
    lines = response.text.split("\n")
    return [row for row in csv.DictReader(lines)]


@op
def find_highest_calorie_cereal(cereals):
    sorted_cereals = list(sorted(cereals, key=lambda cereal: cereal["calories"]))
    return sorted_cereals[-1]["name"]


@op
def find_highest_protein_cereal(cereals):
    sorted_cereals = list(sorted(cereals, key=lambda cereal: cereal["protein"]))
    return sorted_cereals[-1]["name"]


@op
def display_results(context, most_calories, most_protein):
    context.log.info(f"Most caloric cereal: {most_calories}")
    context.log.info(f"Most protein-rich cereal: {most_protein}")
