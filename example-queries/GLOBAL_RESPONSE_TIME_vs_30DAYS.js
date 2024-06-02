

// 4. What is the running average of the global response time for the the current day and of the last 30 days.

use('incidents');

function calculateRunningAverage(currentDate) {

    const current = new Date(currentDate);
    const start = new Date(current);
    start.setDate(current.getDate() - 30);

    const formatDate = (date) => {
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const year = date.getFullYear();
        return `${month}/${day}/${year}`;
    };

    const formattedCurrentDate = formatDate(current);
    const formattedStartDate = formatDate(start);

    const currentDayResponseTime = db.getCollection('LFB_METRICS').aggregate([
        {
            $match: {
                DATEOFCALL: { $regex: formattedCurrentDate }
            }
        },
        {
            $group: {
                _id: null,
                average_response_time: { $avg: "$TOTAL_ATTENDANCETIME" }
            }
        },
        {
            $project: {
                _id: 0,
                average_response_time: 1
            }
        }
    ]);

    const last30DaysResponseTime = db.getCollection('LFB_METRICS').aggregate([
        {
            $match: {
                DATEOFCALL: {
                    $gte: formattedStartDate,
                    $lte: formattedCurrentDate
                }
            }
        },
        {
            $group: {
                _id: null,
                average_response_time: { $avg: { $toInt: "$TOTAL_ATTENDANCETIME" } }
            }
        },
        {
            $project: {
                _id: 0,
                average_response_time: 1
            }
        }
    ]);

    print("Running average response time for the current day (" + formattedCurrentDate + "):");
    currentDayResponseTime.forEach(doc => {
        printjson(doc);
    });

    print("Running average response time for the last 30 days:");
    last30DaysResponseTime.forEach(doc => {
        printjson(doc);
    });
}

// Example usage: pass the current date as an argument in MM/DD/YYYY format
calculateRunningAverage("09/03/2017");
