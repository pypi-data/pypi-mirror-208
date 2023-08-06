import requests

from eigeningenuity.core import get_default_server, EigenServer
from eigeningenuity.util import get_eigenserver, divide_chunks, parseEvents

from typing import Union

class EventLog (object):
    """An elasticsearch instance which talks the Eigen elastic endpoint.
    """
    def __init__(self, baseurl):
        """This is a constructor. It takes in a URL like http://infra:8080/ei-applet/search/"""
        self.baseurl = baseurl
        self.eigenserver = get_eigenserver(baseurl)

    def _testConnection(self):
        """Preflight Request to verify connection to ingenuity"""
        try:
            status = requests.get(self.baseurl, verify=False).status_code
        except (ConnectionError):
            raise ConnectionError ("Failed to connect to ingenuity instance at " + self.eigenserver + ". Please check the url is correct and the instance is up.")

    def pushToEventlog(self, events):
        """
        Push one or more events to the ingenuity eventlog, accepts any event structure

        Args:
            events: A single event as dict, many events as a list of dicts, or the string filepath of a file containing events

        Returns:
            A boolean representing the successful push of all events. False if at least one event failed to be created
        """
        events = parseEvents(events)
        url = self.baseurl + "events/save-multiple"
        event_chunks = list(divide_chunks(events, 500))
        success = []
        for chunk in event_chunks:
            data = {"events": chunk}
            resp = requests.post(url, json=data, verify=False)
            success.append(resp)

        return success

    def pushTo365(self, events:Union[dict,list,str]) -> bool:
        """
        Push one or more events to the office 365 connector, only accepts pre-defined event structures

        Args:
            events: Can only accept event structures that have been pre-defined in ingenuity. A single event as dict, many events as a list of dicts, or the string filepath of a file containing events

        Returns:
            A boolean representing the successful push of all events. False if at least one event failed to be created
        """
        events = parseEvents(events)
        url = self.baseurl + "eventbus/publish-multiple"
        event_chunks = list(divide_chunks(events, 500))
        success = []
        for chunk in event_chunks:
            data = {"events": chunk}
            success.append(requests.post(url, json=data, verify=False))
        return all(success)

def get_eventlog(eigenserver:EigenServer=None):
    """
    Connect to Assetmodel of eigenserver. If eigenserver is not provided this will default to the EIGENSERVER environmental variable

    Args:
        eigenserver: An instance of EigenServer() to query

    Returns:
        An object defining a connection to the AssetModel
    """
    if eigenserver is None:
            eigenserver = get_default_server()

    return EventLog(eigenserver.getEigenServerUrl() + "eventlog-servlet" + "/")

