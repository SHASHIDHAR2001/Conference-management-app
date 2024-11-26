frappe.ui.form.on('Conference', {
    refresh: function (frm) {
        // Check if the form is new (unsaved)
        if (frm.is_new()) {
            // Prevent adding rows to the Session child table
            frm.fields_dict['sessions'].grid.cannot_add_rows = true;
            // frappe.msgprint({
            //     title: __('Save Conference First'),
            //     indicator: 'orange',
            //     message: __('Please save the Conference before adding Sessions.')
            // });
        } else {
            // Allow adding rows to the Session child table for saved records
            frm.fields_dict['sessions'].grid.cannot_add_rows = false;
        }

        // Refresh the child table to apply the changes
        frm.refresh_field('sessions');
    },

    after_save: function (frm) {
        // Allow adding rows after the form is saved
        frm.fields_dict['sessions'].grid.cannot_add_rows = false;
        frm.refresh_field('sessions');
    },
});
