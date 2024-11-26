frappe.ui.form.on('Registration', {
    onload: function(frm) {
        // Trigger fetch session details only when the field is focused
  
            fetchSessionDetails(frm);
    }
});
 
function fetchSessionDetails(frm) {
    // Get the conference reference field's value
    const conference = frm.doc.conference;

    // Ensure a conference is selected before making the API call
    if (conference) {
        // Call the API to fetch sessions for the specific conference
        frappe.call({
            method: "conference_management.conference_management.api.apis.get_sessions_with_details",
            args: { conference_id: conference },  // Pass conference ID or necessary parameter
            callback: function(response) {
                if (response.message) {
                    // Format the session data based on the response
                    const formatted_sessions = response.message.map(session => {
                        return {
                            value: session.session_name + ' (' + session.start_time + ')', // Show session name with start time
                            description: session.session_name  // Optional description for tooltips
                        };
                    });

                    // Dynamically set the session dropdown options
                    frm.fields_dict['session'].get_search = function() {
                        return formatted_sessions;
                    };
                    // Optionally, you can also update the session field with the first session value from the dropdown
                    if (formatted_sessions.length > 0) {
                        frm.set_value('session', formatted_sessions[0].value);
                    }
                }
            },
            error: function(err) {
                console.log("Error occurred while fetching session details: ", err);
            }
        });
    } else {
        console.log("No conference selected");
    }
}