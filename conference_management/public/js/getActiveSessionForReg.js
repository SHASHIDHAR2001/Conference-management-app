frappe.ui.form.on('Registration', {
    refresh: function (frm) {
        // Set a query filter for the session field
        frm.set_query('session', function () {
            if (frm.doc.conference) {
                return {
                    filters: {
                        conference: frm.doc.conference // Only sessions belonging to the selected conference
                    }
                };
            }
        });
    },

    conference: function (frm) {
        // Clear the session field when the conference changes
        frm.set_value('session', null);
    }
});
