frappe.ui.form.on('Attendee', {
    onload: function(frm) {
        console.log("hello")
        // Fetch the recommendations when the page loads (optional)
        if (frm.doc.email) {
            fetchSessionRecommendations(frm);
        }  // Check if the email is populated correctly
    }
});

function fetchSessionRecommendations(frm) {
    frappe.call({
        method: 'conference_management.conference_management.api.apis.get_recommended_sessions',
        args: {
            attendee_email: frm.doc.email  // Use email to identify the attendee
        },
        callback: function(response) {
            if (response.message) {
                displayRecommendationsInDialog(response.message);
            }
        }
    });
}

function displayRecommendationsInDialog(sessions) {
    // Create a new dialog to display the session recommendations
    let dialog = new frappe.ui.Dialog({
        title: 'Recommended Sessions',
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'recommendations',
                label: 'Recommended Sessions',
                options: formatSessionsHtml(sessions)
            }
        ]
    });

    dialog.show();
}

function formatSessionsHtml(sessions) {
    let html = "<ul>";
    sessions.forEach(session => {
        html += `<li><strong>${session.session_name}</strong> - ${session.start_time} - Speaker: ${session.speaker}</li>`;
    });
    html += "</ul>";
    return html;
}
