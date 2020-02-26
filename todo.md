### CherryPy doesn't clear cookies properly when you just reset the db
Steps to reproduce:
- with all programs closed, remove /database/auth_users.db
- start database/db_handler and client_app/server
- open browser the network tab still has cookie entries

-> Cookies **should** be cleared in this case.

### Add Time Out (added)

### Device Emulation runs infinitely. (fixed)

### GET_DATA doesn't work yet. (fixed)

### Implement automatic updating in the website. (added)

### When multiple requests hit the DB it breaks. (fixed)
Steps to reproduce:
- Open Webserver
- Create Breakpoint in db_handler after you recv bin data