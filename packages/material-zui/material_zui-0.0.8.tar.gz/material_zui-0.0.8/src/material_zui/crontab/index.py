import datetime
from crontab import CronTab

# Create a new cron tab
my_cron = CronTab(user='chaunguyen')

# Create a new cron job
# job = my_cron.new(command='python3.10 /path/to/script.py')
job = my_cron.new(command='python3.10 src/material_zui_test/cron/test.py')

# Set the job to run every day at 5 PM
# job.setall('0 17 * * *')
# job.setall('1 * * * *')
job.minute.every(1)

print(job.hour, job.hours)
# my_cron.find_command("result")
print(my_cron.find_comment("result"))

for job in my_cron:
    sch = job.schedule(date_from=datetime.datetime.now())
    print(sch.get_next())

# Write the cron job to the cron tab
my_cron.write()
