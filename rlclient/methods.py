# pylint: disable=invalid-name
from urllib import parse
from collections import defaultdict


class RocketLeagueMethod:

    urls = defaultdict(lambda: 'https://psyonix-rl.appspot.com/callproc105/')
    urls.update({
        'GetPopulationAllPlaylists': 'https://psyonix-rl.appspot.com/Population/GetPopulation/',
    })

    def __init__(self, attr, *args):
        self.method = attr
        self.args = args
        self.url = self.urls[self.method]
        self.supports_bulk_request = self.url in {'https://psyonix-rl.appspot.com/callproc105/'}
        self.parser = getattr(self, 'parse_{0}'.format(self.method), lambda x: x)

    @staticmethod
    def parse_GetPopulationAllPlaylists(response):
        return {
            int(parse.parse_qs(line)['PlaylistID'][0]): int(parse.parse_qs(line)['NumPlayers'][0])
            for line in response.splitlines() if line
        }

    @staticmethod
    def parse_GetSeasonalPlaylists(response):
        return [
            parse.parse_qs(line)['PlaylistName'][0]
            for line in response.splitlines() if line
        ]

    @staticmethod
    def parse_GetGenericDataAll(response):
        return {
            parse.parse_qs(line)['DataKey'][0]: parse.parse_qs(line)['DataValue'][0] == '1'
            for line in response.splitlines() if line
        }

    @staticmethod
    def parse_GetSkillLeaderboard_v2(response):
        results = []
        for line in response.splitlines():
            if not line or line.startswith('LeaderboardID'):
                continue
            parsed_line = parse.parse_qs(line)
            results.append({
                'username': parsed_line['UserName'][0],
                'mmr': float(parsed_line['MMR'][0]),
                'platform': parsed_line['Platform'][0],
                'steam_id': (
                    int(parsed_line['SteamID'][0])
                    if parsed_line['Platform'][0] == 'Steam'
                    else None
                ),
            })
        return results
