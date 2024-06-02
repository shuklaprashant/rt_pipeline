
// 1. Total Events per Incident Station Ground, Grouped by Type of Event in March 2017

use('incidents');

const total_events = db.getCollection('LFB_METRICS').aggregate([
    {
        $match: {
            DATEOFCALL: { $regex: "03/.*2017" }
        }
    },
    {
        $group: {
            _id: {
                incident_station_ground: "$INCIDENTSTATIONGROUND",
                incident_type: "$INCIDENTGROUP"
            },
            total_events: { $sum: "$TOTALEVENTS" }
        }
    },
    {
        $project: {
            _id: 0,
            incident_station_ground: "$_id.incident_station_ground",
            incident_type: "$_id.incident_type",
            total_events: 1
        }
    }
]);

total_events.forEach(doc => {
    printjson(doc);
});

