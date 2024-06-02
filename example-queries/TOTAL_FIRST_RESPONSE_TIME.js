
// 3. Sum of All First Response Time Grouped by Incident Station Ground in 2017

use('incidents');

const total_attendance_time = db.getCollection('LFB_METRICS').aggregate([
    {
        $match: {
            DATEOFCALL: { $regex: ".*2017" }
        }
    },
    {
        $group: {
            _id: "$INCIDENTSTATIONGROUND",
            total_attendance_time: { $sum: "$TOTAL_ATTENDANCETIME" }
        }
    },
    {
        $project: {
            _id: 0,
            incident_station_ground: "$_id",
            total_attendance_time: 1
        }
    }
]);

total_attendance_time.forEach(doc => {
    printjson(doc);
});