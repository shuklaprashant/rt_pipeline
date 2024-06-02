
// 2. Average First Response Time for First Responder, Grouped by Incident Station Ground on Mondays

use('incidents');

const avg_first_response = db.getCollection('LFB_METRICS').aggregate([
    {
        $match: {
            DATEOFCALL: { $regex: ".*2017" }
        }
    },
    {
        $group: {
            _id: "$INCIDENTSTATIONGROUND",
            average_attendance_time: { $avg: "$TOTAL_ATTENDANCETIME" }
        }
    },
    {
        $project: {
            _id: 0,
            incident_station_ground: "$_id",
            average_attendance_time: 1
        }
    }
]);

avg_first_response.forEach(doc => {
    printjson(doc);
});