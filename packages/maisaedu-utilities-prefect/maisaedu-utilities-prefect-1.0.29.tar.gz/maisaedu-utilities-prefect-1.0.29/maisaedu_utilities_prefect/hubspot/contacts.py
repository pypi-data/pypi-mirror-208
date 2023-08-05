from datetime import datetime
import pytz
import time
import requests
import json
import urllib
from time import sleep


def get_contacts_search(
    hapikey, app_private_token, properties, since, after, id, tries=5, limit=100
):
    if hapikey is not None:
        url = "https://api.hubapi.com/crm/v3/objects/contacts/search?"
        parameter_dict = {"hapikey": hapikey}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}

        parameters = urllib.parse.urlencode(parameter_dict)
    else:
        url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }

        parameters = ""

    post_url = url + parameters
    if int(after) > 0:
        strAfter = ', "after":"%s"' % (after)
    else:
        strAfter = ""
    publicObjectSearchRequest = """{
        "filterGroups": [ 
            { "filters": [
                { "propertyName": "lastmodifieddate", "operator": "GTE", "value": "%s" },
                { "propertyName": "hs_object_id", "operator": "GT", "value": %d }
            ] 
        }],
        "sorts": [{ "propertyName": "lastmodifieddate", "direction": "ASCENDING" }],
        "query":"",
        "properties":["%s"],
        "limit":%d %s
    }""" % (
        since,
        id,
        '","'.join(properties),
        limit,
        strAfter,
    )

    for i in range(tries):
        try:
            r = requests.post(
                url=post_url, headers=headers, data=publicObjectSearchRequest
            )
            response_dict = json.loads(r.text)
            return response_dict
        except Exception as e:
            print(e)


def get_all_contact_incremental(
    hapikey, app_private_token, properties, since_parameter, limit=100
):
    after = 0
    hasmore = True
    since = since_parameter
    size = 0
    id = 0
    attempts = 0
    while hasmore:
        resp = get_contacts_search(
            hapikey, app_private_token, properties, since, after, id, limit=limit
        )

        try:
            yield resp["results"]
            lasttimestamp = int(
                pytz.utc.localize(
                    datetime.strptime(
                        list(resp["results"])[-1]["updatedAt"][:19], "%Y-%m-%dT%X"
                    ),
                    is_dst=False,
                ).timestamp()
                * 1000
            )
            attempts = 0
            after = resp["paging"]["next"]["after"]
            lastId = int(list(resp["results"])[-1]["id"])
            size = resp["total"]
        except KeyError as e:
            if size > 10000:
                since = lasttimestamp
                id = lastId
                after = 0
            else:
                if "status" in resp and resp["status"] == "error":
                    attempts += 1
                    sleep(10)
                    if attempts > 2:
                        raise Exception(resp["message"])
                else:
                    hasmore = False
        except Exception as e:
            hasmore = False


def get_contacts_full_load(hapikey, app_private_token, properties, after, tries=5):
    if hapikey is not None:
        url = "https://api.hubapi.com/crm/v3/objects/contacts?"
        parameter_dict = {"hapikey": hapikey}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}

        parameters = urllib.parse.urlencode(parameter_dict)
    else:
        url = "https://api.hubapi.com/crm/v3/objects/contacts?"
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }
        parameters = ""

    url = url + parameters
    url = url + "&properties=" + ",".join(properties)
    url = url + "&limit=100"
    if after:
        url = url + "&after=" + str(after)

    for i in range(tries):
        try:
            r = requests.get(url=url, headers=headers)
            response_dict = json.loads(r.text)
            return response_dict
        except Exception as e:
            print(e)


def get_all_contacts_full_load(hapikey, app_private_token, properties):
    after = 0
    hasmore = True
    attempts = 0
    while hasmore:
        resp = get_contacts_full_load(hapikey, app_private_token, properties, after)

        try:
            yield resp["results"]
            after = resp["paging"]["next"]["after"]
            attempts = 0
        except KeyError as e:
            if "message" in resp:
                if resp["message"] == "You have reached your secondly limit.":
                    attempts += 1
                    sleep(4)
                    if attempts > 2:
                        raise Exception(resp["message"])
            else:
                if "status" in resp and resp["status"] == "error":
                    attempts += 1
                    sleep(4)
                    if attempts > 2:
                        raise Exception(resp["message"])
                else:
                    hasmore = False
        except Exception as e:
            hasmore = False
