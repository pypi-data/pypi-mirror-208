import requests
import json

def do_cmd_getincidents(ops, args):
    if args.count:
            print("Matched %i incidents." % (ops.get_incidents_count(args.query)))
    else:
        incidents = ops.get_incidents(args.query, 1, args.brief, args.details, args.filter)
        print(json.dumps(incidents, indent=2, sort_keys=False))
        if args.resolve:
            update = {"status": "Resolved"}
            for incident in incidents:
                try:
                    print(ops.post_incident_update(incident['id'], update))
                except requests.exceptions.RequestException as e:
                    print(e)