frappe.ui.form.on('Registration', {
    after_save: function (frm) {
        try {
            simulatePaymentProcessing(frm);
            console.log("not calling only");
        } catch (error) {
            console.log(error)
            logApiDetails({
                conference: frm.doc.conference, // Link to Conference
                session: frm.doc.session, // Link to Session
                attendee: frm.doc.attendee, // Link to Attendee
                registration_date: frm.doc.registration_date,
                payment_status: "Failed", // Select: Pending, Paid, Failed
            });
            frm.set_value('payment_status', 'Failed');
        }
    },
});

function simulatePaymentProcessing(frm) {
    console.log("yep shashidhar");
    const randomValue = Math.random();
    let paymentStatus;

    if (randomValue < 0.7) {
        paymentStatus = 'Paid';  // 70% chance for Paid
    } else {
        // 30% chance for either Pending or Failed
        paymentStatus = ['Pending', 'Failed'][Math.floor(Math.random() * 2)];
    }

    frm.set_value('payment_status', paymentStatus);
    logApiDetails({
        conference: frm.doc.conference, // Link to Conference
        session: frm.doc.session, // Link to Session
        attendee: frm.doc.attendee, // Link to Attendee
        registration_date: frm.doc.registration_date, // Date
        payment_status: paymentStatus, // Select: Pending, Paid, Failed
    });
}

function logApiDetails(payload) {
    frappe.call({
        method: "conference_management.conference_management.api.apis.update_api_log",
        args: payload, // Send payload directly without JSON.stringify
        callback: function (response) {
            if (response.message && response.message.status === "success") {
                if (response.message.data.success) {
                    frappe.msgprint(__('Payment Successful! Registration has been confirmed.'));
                } else {
                    frappe.msgprint(__('Payment Failed. Please try again.'));
                }
            } else if (response.message && response.message.status === "failure") {
                frappe.msgprint(__('Payment Failed. Please try again.'));
            } else {
                frappe.msgprint(__('Payment is Pending. If the amount is deducted, we will update the status. Otherwise, you will receive a refund.'));
            }
        },
        error: function (xhr, status, error) {
            console.error("Error logging API details:", error);
            frappe.msgprint(__('An error occurred while processing the payment.'));
        },
    });
}
