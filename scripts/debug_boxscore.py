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

    schedule = lib.fetch(session, "schedule.aspx")
    matches = schedule.findall(".//match")
    finished = [m for m in matches if m.findtext("homeScore") not in (None, "")]
    print(f"\nfound {len(finished)} finished matches for own team")
    if finished:
        last = finished[-1]
        matchid = last.get("id") or last.findtext("id")
        print(f"last finished match id={matchid} start={last.get('start')}")
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
        other_matches = other_schedule.findall(".//match")
        other_finished = [m for m in other_matches if m.findtext("homeScore") not in (None, "")]
        if other_finished:
            om = other_finished[-1]
            omid = om.get("id") or om.findtext("id")
            print(f"other team's last finished match id={omid}")
            obox = lib.fetch(session, "boxscore.aspx", {"matchid": omid})
            dump(obox, f"boxscore.aspx matchid={omid} (OTHER team's match)")

if __name__ == "__main__":
    main()
