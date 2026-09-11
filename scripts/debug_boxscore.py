#!/usr/bin/env python3
"""Throwaway debug script - dumps raw boxscore.aspx / schedule.aspx XML for
inspection. Not part of the pipeline; delete after use."""
import sys
from xml.etree import ElementTree as ET
import requests
import bbapi_lib as lib

def dump(root, label):
    print(f"\n===== {label} =====")
    print(ET.tostring(root, encoding="unicode"))

def main():
    session = requests.Session()
    lib.login(session)

    cfg = lib.load_team_config("../teams/sharpshooters/config.json")
    our_team_key = cfg.get("team_key")

    teaminfo = lib.fetch(session, "teaminfo.aspx")
    our_team_id = teaminfo.find(".//team").get("id")
    dump(teaminfo, "teaminfo.aspx (own team)")

    def finished_matches(schedule_root):
        out = []
        for m in schedule_root.findall(".//match"):
            away, home = m.find("awayTeam"), m.find("homeTeam")
            away_score = away.findtext("score") if away is not None else None
            home_score = home.findtext("score") if home is not None else None
            if away_score is not None and home_score is not None:
                out.append(m)
        return out

    schedule = lib.fetch(session, "schedule.aspx")
    finished = finished_matches(schedule)
    print(f"\nfound {len(finished)} finished matches for own team")
    if finished:
        last = finished[-1]
        matchid = last.get("id")
        print(f"last finished match id={matchid} start={last.get('start')} type={last.get('type')}")
        box = lib.fetch(session, "boxscore.aspx", {"matchid": matchid})
        dump(box, f"boxscore.aspx matchid={matchid} (own team's match)")

    standings = lib.fetch(session, "standings.aspx")
    dump(standings, "standings.aspx")

    other_team_id = None
    for t in standings.findall(".//conference/team"):
        if t.get("id") != our_team_id:
            other_team_id = t.get("id")
            other_team_name = t.findtext("teamName") or t.get("id")
            break
    if other_team_id:
        print(f"\nusing other team id={other_team_id} ({other_team_name}) for schedule.aspx?teamid=")
        other_schedule = lib.fetch(session, "schedule.aspx", {"teamid": other_team_id})
        dump(other_schedule, f"schedule.aspx teamid={other_team_id}")
        other_finished = finished_matches(other_schedule)
        print(f"found {len(other_finished)} finished matches for other team")
        if other_finished:
            om = other_finished[-1]
            omid = om.get("id")
            print(f"other team's last finished match id={omid} type={om.get('type')}")
            obox = lib.fetch(session, "boxscore.aspx", {"matchid": omid})
            dump(obox, f"boxscore.aspx matchid={omid} (OTHER team's match)")

if __name__ == "__main__":
    main()
