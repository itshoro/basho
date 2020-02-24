### CherryPy doesn't clear cookies properly when you just reset the db
Steps to reproduce:
- with all programs closed, remove /database/auth_users.db
- start database/db_handler and client_app/server
- open browser the network tab still has cookie entries

-> Cookies **should** be cleared in this case.


### Device Emulation runs infinitely.

### GET_DATA doesn't work yet.

### Implement automatic updating in the website.