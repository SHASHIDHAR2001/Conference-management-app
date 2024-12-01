$(document).ready(function() {
    $('#login-btn').click(function() {
        const email = $('#email').val();
        const name = $('#name').val();

        if (!name || !email) {
            frappe.msgprint(__('Both Name and Email are mandatory.'));
            return;
        }
        if (email) {
            $('#user-name').text(name);
            $('#user-email').val(email);
            $('.login-form').hide();
            $('.dashboard').show();
            loadAvailableConferences();
        }
    });

    $('#available-tab').click(function() {
        $('#available-conferences').show();
        $('#registered-sessions').hide();
        $('#available-tab').addClass('active');
        $('#registered-tab').removeClass('active');
    });

    $('#registered-tab').click(function() {
        $('#registered-sessions').show();
        $('#available-conferences').hide();
        $('#registered-tab').addClass('active');
        $('#available-tab').removeClass('active');
        loadRegisteredSessions();
    });
});

// Load available conferences
function loadAvailableConferences() {
    $.get('/api/method/getupcomingConference', function(response) {
        if (response.message && response.message.conferences && response.message.conferences.length > 0) {
            let conferenceHtml = '';
            response.message.conferences.forEach(function(conference) {
                let sessionHtml = '';
                conference.sessions.forEach(function(session) {
                    sessionHtml += `
                        <div class="session-details">
                            <p class="session-name">Session: ${session.session_name}</p>
                            <p class="session-speaker">Speaker: ${session.speaker}</p>
                            <p class="session-time">Time: ${session.start_time} - ${session.end_time}</p>
                            <p class="session-fee">Fee: ${session.session_fee}</p>
                            <button class="register-btn" data-session-id="${session.name}" data-conference="${conference.conference_name}">
                                Register
                            </button>
                        </div>
                    `;
                });

                conferenceHtml += `
                    <div class="conference-item">
                        <h2 class="conference_name">${conference.conference_name}</h2>
                        <div class="session-list">${sessionHtml}</div>
                        <hr class="styled-divider">
                    </div>
                `;
            });
            // <h3 class="conf_desc">${conference.description}</h3>

            $('#available-conferences').html(conferenceHtml);

            // Register button click handler
            $('.register-btn').click(function() {
                const sessionId = $(this).data('session-id');
                const conferenceName = $(this).data('conference');
                const attendeeName = $('#user-name').text();
                const attendeeEmail = $('#user-email').val();
                registerSession(sessionId, conferenceName, attendeeName, attendeeEmail, $(this));
            });
        } else {
            $('#available-conferences').html('<p class="no-conferences-message">No conferences found.</p>');
        }
    });
}

// Register session
function registerSession(sessionId, conferenceName,attendeeName, attendeeEmail, buttonElement) {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');
    const registrationData = {
        attendee: {
            attendee_name: attendeeName, 
            email: attendeeEmail,
            phone_number: '',
            organization: ''
        },
        registration: {
            conference: conferenceName,
            session: sessionId
        }
    };

    $.ajax({
        url: '/api/method/add_attendee_and_register',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(registrationData),
        headers: {
            'X-Frappe-CSRF-Token': csrfToken 
        },
        success: function(response) {
            console.log(response);
            // Check if the response status is success, failure, or error
            if (response.message.status === "success") {
                frappe.msgprint({
                    message: response.message.message,
                    title: __('Success'),
                    indicator: 'green'  // Green indicator for success
                });
    
                buttonElement.text('Registered');
                buttonElement.removeClass('register-btn').addClass('registered-btn');
                buttonElement.prop('disabled', true);
            } else if (response.message.status === "Failure") {
                frappe.msgprint({
                    message: response.message.message,
                    title: __('Failure'),
                    indicator: 'red' 
                });
            } else if (response.message.status === "error") {
                console.log(response);
                frappe.msgprint({
                    message: response.message.message,
                    title: __('Error'),
                    indicator: 'orange' 
                });
            }
        },
        error: function(xhr) {
            // Showing a generic error message
            frappe.msgprint({
                message: 'An unexpected error occurred. Please try again later.',
                title: __('Error'),
                indicator: 'red'
            });
            console.error('Error registering session:', xhr.responseText);
        }
    });
    
}

// Load registered sessions for the user
function loadRegisteredSessions() {
    const email = $('#user-email').val();
    $.get(`/api/method/get_registered_sessions?attendee_email=${email}`, function(response) {
        if (response.message.registered_sessions && response.message.registered_sessions.length > 0) {
            let sessionHtml = '';
            response.message.registered_sessions.forEach(function(session) {
                sessionHtml += `
                    <div class="session-details">
                        <h4 class="session-name">Session: ${session.session_name}</h4>
                        <p class="session-speaker">Speaker: ${session.speaker}</p>
                        <p class="session-time">Time: ${session.start_time} - ${session.end_time}</p>
                    </div>
                `;
            });
            $('#registered-sessions').html(sessionHtml);
        } else {
            $('#registered-sessions').html('<p class="no-session-message">No registered session found.</p>');

        }
    });
}
