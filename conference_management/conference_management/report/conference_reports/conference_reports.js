// Copyright (c) 2024, shashi and contributors
// For license information, please see license.txt


frappe.query_reports["Conference Reports"] = {

    onload: function(report) {
        const wrapper = document.querySelector(".report-wrapper");
        if (wrapper) {
            wrapper.classList.add("conference-report");
        }
    },

    filters: [
        {
            fieldname: "start_date",
            label: __("Start Date"),
            fieldtype: "Date",
            default: frappe.datetime.now_date(),
        },
        {
            fieldname: "end_date",
            label: __("End Date"),
            fieldtype: "Date",
        }
    ]
};
