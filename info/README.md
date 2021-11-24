# Patient Management System Backend
The following are further explanations of the tables of the sqlite database 
where necessary and a high-level overview of the appointments process.

### user_status (Managed by Admin)
Activating / deactivating user accounts works in the exact same way for
both GP's and patients.

The user_status of an Admin is 1 and cannot be changed, Admin details can
can only be changed through the database, there is no way to register as an
Admin throught the app.

Admin can also choose to delete users entirely from the database. This should
cascade a deletion throughout the database to prevent inconsistency.

### availability
Only GP's that have a their user_status set to 1 (Activated) are allowed to
insert rows into the availability table. The availability_status will be a 
default value of 0 (Available) for all newly inserted rows until a patient 
books an appointment. If the GP or Patient cancel that appointment, the 
availability status of the availability date selected resets back to 0 
(Available), so other Patients will be able to select it.

Only Patients that have their user_status set to 1 (Activated) are allowed to 
search through the availability table and book appointments with GP's.

### availability_status
If a booking has been cancelled by either the GP or the Patient, the 
availability should reset back to 0 (Available).

## Appointments Process
1. Patient and GP's register; their accounts are later activated by an Admin.
2. Patient views a table of all GP's availabilities depending on location 
and date he selected.
3. Patient selects a specific row from the above table, adds problem description.
This inserts a row into the appointment table and updates the availability_status 
of the aforementioned row to 1 (Unavailable). Other patients cannot then select 
that row as a potential date for an appointment.
4. GP logs in and checks the appointments table for any appointments where the
appointment_status is 0 (Pending Confirmation).
5. GP then either confirms the appointment and updates the appointment_status 
to 1 (Confirmed) or cancels the appointment (Cancelled by GP), which resets 
the availability of that date back to 0 (Available) in the availability table. 
Notifications will be sent to Patient depending on the GP's choice to confirm. 
The Admin sends the emails for next day appointments. 
Patients/GPs see the status of the appointment when they login.

### Cancellations
If the patient cannot make it to the appointment, the patient logs in, views
his appointments and clicks a button to cancel. The GP does not have the option
to cancel an appointment once he confirmed it. He should deselct his availability 
for that appointment which would remove both the availability and the appointment.
As shown in the diagram Notifications will be sent to the patient to 
confirm the appointment has been cancelled.

### Prescriptions
Once an appointment has been complete the status of the appointment should 
change to 4 (GP ACTION REQUIRED). The appoinmtnent time is compare dto the time 
when opening the app, so it automatically changes the appointment sttaus to 4.
Only then will the GP be able to enter a prescription into the prescription table. 
Once a prescription has been prescribed the appointment_status should change to 3 
(Completed with Prescription). If only diagnosis and comment are provided, the status 
changes to 2 (Completed without Prescription).

Once updated by the GP, Patients are then able to view their prescriptions.
