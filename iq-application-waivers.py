#!/usr/bin/python3
# Retrieve all the waivers for a given application
# ----------------------------------------------------------------------------
# Python Dependencies
import json
import argparse
import asyncio
import aiohttp
import pandas
# ----------------------------------------------------------------------------
iq_url, iq_session = "", ""
api_calls = 0

def getArguments():
    global iq_url, iq_session, iq_auth
    parser = argparse.ArgumentParser(description='List waivers for an application')
    parser.add_argument('-i', '--app', help='Name of the Application you want to list waivers for', required=True)
    parser.add_argument('-u', '--url', help='eg. http://localhost:8070', required=True)
    parser.add_argument('-a', '--auth', help='eg. admin:admin123', required=True)
    args = vars(parser.parse_args())
    iq_url = args["url"]
    creds = args["auth"].split(":")
    iq_session = aiohttp.ClientSession()
    iq_auth = aiohttp.BasicAuth(creds[0], creds[1])
    return args

async def main():
    args = getArguments()
    appName = args["app"]

    application = await get_application(appName)
    if application is None:
        print("The application '" + appName + "' could not be found, exiting...")
    else:
        applicationId = application["id"]
        waiversList = await get_waivers(applicationId)

        if waiversList is None:
            print("No Waivers found for the application ''" + appName + "'', exiting...")
        else:
            df = pandas.read_json(json.dumps(waiversList))
            print(df)
            df.to_csv(appName + '_waivers.csv', encoding='utf-8', index=False)

    await iq_session.close()

# -----------------------------------------------------------------------------

async def handle_resp(resp, root=""):
    global api_calls
    api_calls += 1
    if resp.status != 200:
        print(await resp.text())
        return None
    node = await resp.json()
    if root in node:
        node = node[root]
    if node is None or len(node) == 0:
        return None
    return node

async def get_url(url, root=""):
    resp = await iq_session.get(url, auth=iq_auth)
    return await handle_resp(resp, root)

async def get_application(appId):
    url = f'{iq_url}/api/v2/applications?publicId={appId}'
    apps = await get_url(url, "applications")
    if apps is None:
        return None
    return apps[0]

async def get_waivers(appId):
    url = f'{iq_url}/api/v2/policyWaivers/application/{appId}'
    waivers = await get_url(url, "applications")
    if waivers is None:
        return None
    return waivers

if __name__ == "__main__":
    asyncio.run(main())
