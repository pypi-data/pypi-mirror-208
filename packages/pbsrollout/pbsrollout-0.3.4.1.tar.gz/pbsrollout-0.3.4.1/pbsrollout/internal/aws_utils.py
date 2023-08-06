import datetime
from typing import List

import boto3
from mypy_boto3_ecr.client import ECRClient


def get_ecr_client() -> ECRClient:
    session = boto3.Session(profile_name='ctv_engineer')
    return session.client('ecr', region_name='us-east-1')


def get_ecr_images(repository: str) -> List[str]:
    # see: https://stackoverflow.com/questions/70533690/boto3-how-to-get-newest-docker-image-from-ecr

    # query to sort by newest
    # jmespath_expression = 'Images[?CreationDate>`2022-04-01`]'
    jmespath_expression = "reverse(sort_by(imageDetails,&to_string(imagePushedAt)))[:40].imageTags[0]"
    # jmespath_expression = "reverse(sort_by(imageDetails,&to_string(imagePushedAt)))[:15].imageTags[0]"

    client = get_ecr_client()
    paginator = client.get_paginator('describe_images')
    # We need big page size because the result will be sent per page.
    # So if page size is 100, and we return the last 15 items [:15], then we will have 15 items per batch of 100 results!
    iterator = paginator.paginate(repositoryName=repository, registryId='689975898194', PaginationConfig={'PageSize': 1000})
    filter_iterator = iterator.search(jmespath_expression)
    return sorted(list(filter_iterator), reverse=True)
