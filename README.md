# rlclient

## Summary

A client to communicate with the Rocket League game coordinator servers.

A few things to keep in mind:

 - You need to authenticate yourself with the API. I just grabbed authentication
   details from a running game session, and they haven't expired during the time
   it took for me to write this clients, so I hope the auth process just checks
   if the provided session ID and key match each other via some algorithm, and
   there's no actual state stored on the backend that would expire sessions
   after a while. But, of course, I have no idea, so this client might be
   completely useless until someone figures out how to generate session keys.

 - This package is expected to change a lot between versions. If you want to use
   it, pin the requirement spec to the latest version! A minor version will be
   bumped for a breaking API change (such as adding a parser for a new call
   type.)

 - We're accessing a private API here, so don't be surprised if your stuff just
   randomly breaks due to some change by Psyonix.

## Installation

```
pip3.5 install rlclient
```

## Configuration

Instantiate the client with `RocketLeagueClient('session_id', 'session_key')`.
You can change the environment from the default `Prod` with the third parameter.

Alternatively, you can use the `RLCLIENT_SESSION_ID`, `RLCLIENT_SESSION_KEY`,
and `RLCLIENT_ENVIRONMENT` environment variables, and pass no parameters.

## Usage

The basic usage goes like this:

```python
>>> from rlclient import RocketLeagueClient
>>> client = RocketLeagueClient()  # auth details are set in the environment
>>> call = client.GetPopulationAllPlaylists()
>>> client.request([call])[0]
{0: 35670, 1: 924, 2: 8398, 3: 10827, 4: 2017, 6: 3127, 7: 3926, 8: 7123, 9: 2928, 10: 2230, 11: 14718, 12: 2950, 13: 7358, 15: 801, 16: 1629, -2: 3961}
```

The client supports grouping multiple calls into one request, too, if the
call happens to support this on the backend:

```python
>>> calls = [
...     client.GetSkillLeaderboard_v2(10),
...     client.GetSkillLeaderboard_v2(11),
...     client.GetSkillLeaderboard_v2(12),
... ]
>>> responses = client.request(calls)
>>> [len(response) for response in responses]
[200, 200, 200]
```

If the call doesn't support this on the backend… don't worry! I've still got
your back. The client is smart enough to figure out all of it:

```python
>>> calls = [
...     client.GetPopulationAllPlaylists(),
...     client.GetSkillLeaderboard_v2(10),   #\
...     client.GetSeasonalPlaylists(),       # these three are grouped into one HTTP request
...     client.GetGenericDataAll(),          #/
...     client.GetPopulationAllPlaylists(),
... ]
>>> responses = client.request(calls)  # sends three HTTP requests
>>> for call, response in zip(calls, responses):
...     print('{0}: {1}'.format(call.method, response))
...
GetPopulationAllPlaylists: {0: 35670, 1: 924, 2: 8398, 3: 10827, 4: 2017, 6: 3127, 7: 3926, 8: 7123, 9: 2928, 10: 2230, 11: 14718, 12: 2950, 13: 7358, 15: 801, 16: 1629, -2: 3961}
GetSkillLeaderboard_v2: [...]  # trimmed in this example
GetSeasonalPlaylists: ['Experimental', 'SnowDayPromotion']
GetGenericDataAll: {'RankEnabled': True, 'Analytics': True, 'BugReports': False}
GetPopulationAllPlaylists: {0: 35670, 1: 924, 2: 8398, 3: 10827, 4: 2017, 6: 3127, 7: 3926, 8: 7123, 9: 2928, 10: 2230, 11: 14718, 12: 2950, 13: 7358, 15: 801, 16: 1629, -2: 3961}
```
